from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from message import *
    
from .pokemon import PokemonFactory
from enum import Enum, auto
import time
from .enemyAI import *

# Global constants
PLAYER_CHANCE_TO_DODGE = 0.5
OPPONENT_CHANCE_TO_DODGE = 0.5
ENEMY_RESPONSE_TIME = 3
PLAYER_CHANCE_TO_RUN = 0.7

class TurnStage(Enum):
    IDLE = auto()
    INTRO = auto()
    PLAYER_TURN = auto()
    AWAIT_INPUT = auto()
    ENEMY_WAIT = auto()
    ENEMY_TURN = auto()
    END = auto()
    CLEANUP = auto()


class PokemonBattleManager:
    def __init__(self, player, wild_pokemon_name: str):
        self.__player = player
        self.__player_pokemon = player.get_state("active_pokemon", None)
        self.__enemy_pokemon = PokemonFactory.create_pokemon(wild_pokemon_name)
        self.__player_used_dodge = False
        self.__enemy_used_dodge = False
        self.__turn_stage = TurnStage.INTRO
        self.__current_option = None
        self.__last_action_time = time.time()

    def set_selected_option(self, selected_option: str) -> None:
        self.__current_option = selected_option

    def clear_option(self) -> None:
        self.__current_option = None

    def is_over(self) -> bool:
        return self.__turn_stage == TurnStage.CLEANUP

    def get_player_pokemon(self):
        return self.__player_pokemon

    def update(self) -> list[Message]:
        now = time.time()
        messages = []

        def battle_data():
            return PokemonBattleMessage(
                self.__player,
                self.__player,
                player_data=self._pokemon_data(self.__player_pokemon),
                enemy_data=self._pokemon_data(self.__enemy_pokemon)
            )

        match self.__turn_stage:
            case TurnStage.INTRO:
                messages.extend(self._handle_intro(battle_data))

            case TurnStage.PLAYER_TURN:
                messages.extend(self._handle_player_turn())

            case TurnStage.AWAIT_INPUT:
                messages.extend(self._handle_await_input(battle_data))

            case TurnStage.ENEMY_WAIT:
                if now - self.__last_action_time >= ENEMY_RESPONSE_TIME:
                    self.__turn_stage = TurnStage.ENEMY_TURN

            case TurnStage.ENEMY_TURN:
                messages.extend(self._handle_enemy_turn(battle_data))

            case TurnStage.END:
                messages.extend(self._handle_end())

            case TurnStage.CLEANUP:
                return []

        return messages

    def _pokemon_data(self, pokemon):
        return {
            "name": pokemon.name if pokemon else "Unknown",
            "level": pokemon.level if pokemon else 1,
            "hp": pokemon.current_health if pokemon else 0,
            "max_hp": pokemon.max_health if pokemon else 1
        }

    def _handle_intro(self, battle_data_fn):
        messages = [
            ServerMessage(self.__player, f"You encountered a wild {self.__enemy_pokemon.name}!"),
            battle_data_fn()
        ]
        self.__turn_stage = TurnStage.PLAYER_TURN
        self.__last_action_time = time.time()
        return messages

    def _handle_player_turn(self):
        self.clear_option()
        attack_options = [
            f"{i}: {attack['name']} ({attack['damage']})"
            for i, attack in enumerate(self.__player_pokemon.known_attacks)
        ]
        full_options = attack_options + ["Dodge", "Run"]
        self.__last_action_time = time.time()
        self.__turn_stage = TurnStage.AWAIT_INPUT
        return [OptionsMessage(self.__player, self.__player, full_options)]

    def _handle_await_input(self, battle_data_fn):
        messages = []
        now = time.time()
        selected = self.__current_option
        if selected is None:
            return messages

        self.clear_option()
        name = self.__player.get_name()

        if selected == "Dodge":
            self.__player_used_dodge = True
            messages.append(ServerMessage(self.__player, f"({name}) {self.__player_pokemon.name} prepares to dodge!"))
            self.__turn_stage = TurnStage.ENEMY_WAIT

        elif selected == "Run":
            if random.random() < PLAYER_CHANCE_TO_RUN:
                messages.append(ServerMessage(self.__player, f"({name}) You ran away safely!"))
                self.__turn_stage = TurnStage.END
            else:
                messages.append(ServerMessage(self.__player, f"({name}) You tried to run but couldn't escape!"))
                self.__turn_stage = TurnStage.ENEMY_WAIT

        elif ":" in selected and selected.split(":")[0].isdigit():
            attack_index = int(selected.split(":")[0])
            messages.extend(self._process_player_attack(attack_index, battle_data_fn))

        else:
            messages.append(ServerMessage(self.__player, "Unrecognized action."))
            self.__turn_stage = TurnStage.PLAYER_TURN

        self.__last_action_time = now
        return messages

    def _process_player_attack(self, index, battle_data_fn):
        messages = []
        name = self.__player.get_name()
        if 0 <= index < len(self.__player_pokemon.known_attacks):
            if self.__enemy_used_dodge and random.random() < OPPONENT_CHANCE_TO_DODGE:
                messages.append(ServerMessage(self.__player,
                    f"(Opp) {self.__enemy_pokemon.name} dodged {self.__player_pokemon.known_attacks[index]['name']}!"))
            else:
                if self.__enemy_used_dodge:
                    messages.append(ServerMessage(self.__player, f"(Opp) Dodge failed!"))
                result = self.__player_pokemon.attack(index, self.__enemy_pokemon)
                messages.append(ServerMessage(self.__player, f"({name}) {result['message']} It dealt {result['damage']} damage."))
                messages.append(battle_data_fn())

                if result.get("evolved"):
                    self.__player.set_state("active_pokemon", result["evolved"])
                    self.__player_pokemon = result["evolved"]
                    messages.append(ServerMessage(self.__player, f"Your Pokémon evolved into {self.__player_pokemon.name}!"))

            self.__enemy_used_dodge = False

        if self.__player_pokemon.is_fainted():
            messages.append(ServerMessage(self.__player, f"({name}) {self.__player_pokemon.name} has fainted! You lost."))
            self.__turn_stage = TurnStage.END
        elif self.__enemy_pokemon.is_fainted():
            messages.append(ServerMessage(self.__player, f"(Opp) {self.__enemy_pokemon.name} has fainted! You won!"))
            self.__turn_stage = TurnStage.END
        else:
            self.__turn_stage = TurnStage.ENEMY_WAIT

        return messages

    def _handle_enemy_turn(self, battle_data_fn):
        messages = []
        ai: EnemyAI = self.__player.get_state("enemy_ai", MediumAI())
        action = ai.choose_action(self.__enemy_pokemon, self.__player_pokemon)

        if action == "Dodge":
            messages.append(ServerMessage(self.__player, f"(Opp) {self.__enemy_pokemon.name} is preparing to dodge!"))
            self.__enemy_used_dodge = True
        else:
            attack_index = int(action)
            attack = self.__enemy_pokemon.known_attacks[attack_index]

            if self.__player_used_dodge and random.random() < PLAYER_CHANCE_TO_DODGE:
                messages.append(ServerMessage(self.__player,
                    f"({self.__player.get_name()}) {self.__player_pokemon.name} dodged {attack['name']} attack!"))
            else:
                result = self.__enemy_pokemon.attack(attack_index, self.__player_pokemon)
                messages.append(ServerMessage(self.__player, f"(Opp) {result['message']} It dealt {result['damage']} damage."))
                messages.append(battle_data_fn())

        self.__player_used_dodge = False

        if self.__player_pokemon.is_fainted():
            messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__player_pokemon.name} has fainted! You lost."))
            self.__turn_stage = TurnStage.END
        elif self.__enemy_pokemon.is_fainted():
            messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__enemy_pokemon.name} has fainted! You won!"))
            self.__turn_stage = TurnStage.END
        else:
            self.__turn_stage = TurnStage.PLAYER_TURN

        self.__last_action_time = time.time()
        return messages

    def _handle_end(self):
        messages = [
            ServerMessage(self.__player, "The battle has ended!"),
            OptionsMessage(self.__player, self.__player, [], destroy=True),
            PokemonBattleMessage(self.__player, self.__player, {}, {}, destroy=True)
        ]
        self.__turn_stage = TurnStage.CLEANUP
        return messages