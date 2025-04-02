from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    
import time
from enum import Enum, auto
from .pokemon import *
from .enemyAI import *

class TurnStage(Enum):
    IDLE = auto()
    INTRO = auto()
    PLAYER_TURN = auto()
    AWAIT_INPUT = auto()
    ENEMY_WAIT = auto()
    ENEMY_TURN = auto()
    END = auto()
    CLEANUP = auto()
    
# Global constants
PLAYER_CHANCE_TO_DODGE = 0.5
OPPONENT_CHANCE_TO_DODGE = 0.5
ENEMY_RESPONSE_TIME = 3
PLAYER_CHANCE_TO_RUN = 0.7
    

class PokemonBattlePressurePlate(PressurePlate, SelectionInterface):
    def __init__(self, wild_pokemon_name: str):
        super().__init__(image_name="bushh", stepping_text=f"You encountered a wild {wild_pokemon_name}!")
        self.__wild_pokemon_name = wild_pokemon_name
        self.__current_option = None
        self.__player = None
        self.__player_pokemon = None
        self.__enemy_pokemon = None
        self.__player_used_dodge = False
        self.__enemy_used_dodge = False
        self.__turn_stage = TurnStage.IDLE
        self.__last_action_time = time.time()

    def select_option(self, player, selected_option: str) -> list[Message]:
        self.__current_option = selected_option
        return []  # actual logic handled in update()

    def clear_option(self) -> None:
        self.__current_option = None

    def player_entered(self, player) -> list[Message]:
        self.__player = player
        self.__player_pokemon = player.get_state("active_pokemon", None)
        self.__enemy_pokemon = PokemonFactory.create_pokemon(self.__wild_pokemon_name)
        self.__player_used_dodge = False
        self.__enemy_used_dodge = False
        self.__turn_stage = TurnStage.INTRO
        self.__last_action_time = time.time()

        # Set this plate as the active selection handler
        player.set_current_menu(self)

        return []

    def update(self) -> list[Message]:
        now = time.time()
        messages = []

        def battle_data():
            return PokemonBattleMessage(
                self.__player,
                self.__player,
                player_data={
                    "name": self.__player_pokemon.name if self.__player_pokemon else "Unknown",
                    "level": self.__player_pokemon.level if self.__player_pokemon else 1,
                    "hp": self.__player_pokemon.current_health if self.__player_pokemon else 0,
                    "max_hp": self.__player_pokemon.max_health if self.__player_pokemon else 1
                },
                enemy_data={
                    "name": self.__enemy_pokemon.name if self.__enemy_pokemon else "Unknown",
                    "level": self.__enemy_pokemon.level if self.__enemy_pokemon else 1,
                    "hp": self.__enemy_pokemon.current_health if self.__enemy_pokemon else 0,
                    "max_hp": self.__enemy_pokemon.max_health if self.__enemy_pokemon else 1
                }
            )

        if self.__turn_stage == TurnStage.INTRO:
            messages.extend([
                ServerMessage(self.__player, f"You encountered a wild {self.__enemy_pokemon.name}!"),
                battle_data()
            ])
            self.__turn_stage = TurnStage.PLAYER_TURN
            self.__last_action_time = now

        elif self.__turn_stage == TurnStage.PLAYER_TURN:
            self.clear_option()
            attack_options = [
                f"{i}: {attack['name']} ({attack['damage']})"
                for i, attack in enumerate(self.__player_pokemon.known_attacks)
            ]
            full_options = attack_options + ["Dodge", "Run"]
            messages.append(OptionsMessage(self, self.__player, full_options))
            self.__turn_stage = TurnStage.AWAIT_INPUT
            self.__last_action_time = now

        elif self.__turn_stage == TurnStage.AWAIT_INPUT:
            if self.__current_option is not None:
                selected = self.__current_option
                self.clear_option()

                if selected == "Dodge":
                    self.__player_used_dodge = True
                    messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__player_pokemon.name} prepares to dodge!"))
                    self.__turn_stage = TurnStage.ENEMY_WAIT

                elif selected == "Run":
                    if random.random() < PLAYER_CHANCE_TO_RUN:
                        messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) You ran away safely!"))
                        self.__turn_stage = TurnStage.END
                    else:
                        messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) You tried to run but couldn't escape!"))
                        self.__turn_stage = TurnStage.ENEMY_WAIT

                elif ":" in selected and selected.split(":")[0].isdigit():
                    attack_index = int(selected.split(":")[0])
                    if 0 <= attack_index < len(self.__player_pokemon.known_attacks):
                        if self.__enemy_used_dodge and random.random() < OPPONENT_CHANCE_TO_DODGE:
                            messages.append(ServerMessage(self.__player,
                                f"(Opp) {self.__enemy_pokemon.name} dodged {self.__player_pokemon.known_attacks[attack_index]['name']}!"))
                        else:
                            if self.__enemy_used_dodge:
                                messages.append(ServerMessage(self.__player, f"(Opp) Dodge failed!"))
                            result = self.__player_pokemon.attack(attack_index, self.__enemy_pokemon)
                            messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {result['message']} It dealt {result['damage']} damage."))
                            messages.append(battle_data())

                            if result.get("evolved"):
                                self.__player.set_state("active_pokemon", result["evolved"])
                                self.__player_pokemon = result["evolved"]
                                messages.append(ServerMessage(self.__player, f"Your Pokémon evolved into {self.__player_pokemon.name}!"))

                        self.__enemy_used_dodge = False

                    if self.__player_pokemon.is_fainted():
                        messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__player_pokemon.name} has fainted! You lost."))
                        self.__turn_stage = TurnStage.END
                    elif self.__enemy_pokemon.is_fainted():
                        messages.append(ServerMessage(self.__player, f"(Opp) {self.__enemy_pokemon.name} has fainted! You won!"))
                        self.__turn_stage = TurnStage.END
                    else:
                        self.__turn_stage = TurnStage.ENEMY_WAIT

                else:
                    messages.append(ServerMessage(self.__player, "Unrecognized action."))
                    self.__turn_stage = TurnStage.PLAYER_TURN

                self.__last_action_time = now

        elif self.__turn_stage == TurnStage.ENEMY_WAIT:
            if now - self.__last_action_time >= ENEMY_RESPONSE_TIME:
                self.__turn_stage = TurnStage.ENEMY_TURN

        elif self.__turn_stage == TurnStage.ENEMY_TURN:
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
                    messages.append(battle_data())

            self.__player_used_dodge = False

            if self.__player_pokemon.is_fainted():
                messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__player_pokemon.name} has fainted! You lost."))
                self.__turn_stage = TurnStage.END
            elif self.__enemy_pokemon.is_fainted():
                messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__enemy_pokemon.name} has fainted! You won!"))
                self.__turn_stage = TurnStage.END
            else:
                self.__turn_stage = TurnStage.PLAYER_TURN

            self.__last_action_time = now

        elif self.__turn_stage == TurnStage.END:
            messages.append(ServerMessage(self.__player, "The battle has ended!"))
            messages.append(OptionsMessage(self, self.__player, [], destroy=True))
            messages.append(PokemonBattleMessage(self, self.__player, {}, {}, destroy=True))
            self.__player.set_state("active_pokemon", self.__player_pokemon)
            self.__player.set_current_menu(None)
            self.__turn_stage = TurnStage.CLEANUP

        elif self.__turn_stage == TurnStage.CLEANUP:
            return []

        return messages


class ChooseDifficultyPlate(PressurePlate, SelectionInterface):
    def __init__(self):
        super().__init__(image_name="hal9000", stepping_text="Choose your battle difficulty!")

    def player_entered(self, player) -> list[Message]:
        current_ai = player.get_state("enemy_ai", None)
        current_difficulty = type(current_ai).__name__.replace("AI", "") if current_ai else "None"

        # Register this plate as the active menu
        player.set_current_menu(self)

        return [
            ServerMessage(player, f"Current difficulty: {current_difficulty}\nChoose a new difficulty."),
            # DialogueMessage(self, player, f"Current difficulty: {current_difficulty}\nChoose a new difficulty.", ""),
            OptionsMessage(self, player, ["Easy", "Medium", "Hard"])
        ]

    def select_option(self, player, selected_option: str) -> list[Message]:
        difficulty_map = {
            "Easy": EasyAI,
            "Medium": MediumAI,
            "Hard": HardAI,
        }

        ai_class = difficulty_map.get(selected_option)
        if ai_class:
            player.set_state("enemy_ai", ai_class())
            player.set_current_menu(None)  # Clear menu so future interactions work
            return [
                ServerMessage(player, f"Difficulty set to {selected_option}."),
                OptionsMessage(self, player, [], destroy=True)
            ]

        return [ServerMessage(player, "Invalid difficulty selection.")]