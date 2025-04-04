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
from .observers import BattleMessageNotifier 

# Global constants
PLAYER_CHANCE_TO_DODGE = 0.5
OPPONENT_CHANCE_TO_DODGE = 0.5
ENEMY_RESPONSE_TIME = 3
PLAYER_CHANCE_TO_RUN = 0.7

class TurnStage(Enum):
    IDLE = auto()           # the stage the battle manager initializes in
    INTRO = auto()          # setup stage, where the battle is introduced 
    PLAYER_TURN = auto()    # present options to player (called once so option messages don't repeat)
    AWAIT_INPUT = auto()    # wait for player input and process it
    AWAIT_SWITCH = auto()   # wait for player input and process it
    ENEMY_WAIT = auto()     # time delay before enemy action
    ENEMY_TURN = auto()     # perform enemy action
    END = auto()            # end stage where we announce the battle is over and destroy the windows
    CLEANUP = auto()        # cleanup stage, pressure plate sees that battle is over and performs cleanup


class PokemonBattleManager:
    def __init__(self, player, wild_pokemon_name: str):
        self.__player = player
        self.__player_pokemon = player.get_state("active_pokemon", None)
        self.__enemy_pokemon = PokemonFactory.create_pokemon(wild_pokemon_name)
        self.__used_dodge = False # player and enemy share this flag (can be done since this game is turn-based)
        self.__turn_stage = TurnStage.INTRO
        self.__current_option = None
        self.__last_action_time = time.time()
        self.__switch_options_map = {}

        # Observer setup
        self.__battle_messages: list[Message] = []
        self.__player_pokemon.add_observer(BattleMessageNotifier(player, self.__battle_messages))
        self.__enemy_pokemon.add_observer(BattleMessageNotifier(player, self.__battle_messages))

    def set_selected_option(self, selected_option: str) -> None:
        """Called from outside (pressure plate) to set the selected option."""
        self.__current_option = selected_option

    def clear_option(self) -> None:
        self.__current_option = None

    def is_over(self) -> bool:
        """Battle is over when we are in the cleanup stage."""
        return self.__turn_stage == TurnStage.CLEANUP

    def get_player_pokemon(self) -> Pokemon:
        return self.__player_pokemon

    # Update is called every second
    def update(self) -> list[Message]:
        now = time.time()
        messages = []

        match self.__turn_stage:
            case TurnStage.INTRO:
                messages.extend(self._handle_intro())

            case TurnStage.PLAYER_TURN:
                messages.extend(self._handle_player_turn())

            case TurnStage.AWAIT_INPUT | TurnStage.AWAIT_SWITCH: # player inputs are handled in the same way
                messages.extend(self._handle_await_input())

            case TurnStage.ENEMY_WAIT:
                # When ENEMY_RESPONSE_TIME amount of time has passed, switch to enemy turn
                if now - self.__last_action_time >= ENEMY_RESPONSE_TIME:
                    self.__turn_stage = TurnStage.ENEMY_TURN

            case TurnStage.ENEMY_TURN:
                messages.extend(self._handle_enemy_turn())

            case TurnStage.END:
                messages.extend(self._handle_end())

            case TurnStage.CLEANUP:
                return [] # return empty list to avoid sending new messages (reason why END is not last stage)

        messages.extend(self.__battle_messages)  # include health change messages from observers
        self.__battle_messages.clear()  # clear buffer after flushing messages
        
        return messages

    def _pokemon_data(self, pokemon) -> dict[str, int]:
        """Pokémon data for battle message. These are the only fields needed for battle window."""
        return {
            "name": pokemon.name if pokemon else "Unknown",
            "level": pokemon.level if pokemon else 1,
            "hp": pokemon.current_health if pokemon else 0,
            "max_hp": pokemon.max_health if pokemon else 1
        }

    def _make_battle_message(self) -> PokemonBattleMessage:
        """Create a battle message with player and enemy Pokémon data."""
        return PokemonBattleMessage(
            self.__player,
            self.__player,
            player_data=self._pokemon_data(self.__player_pokemon),
            enemy_data=self._pokemon_data(self.__enemy_pokemon)
        )

    def _handle_intro(self) -> list[Message]:
        """Initialize the battle with encounter text setting up battle."""
        messages = [
            ServerMessage(self.__player, f"You encountered a wild {self.__enemy_pokemon.name}!"),
            self._make_battle_message()
        ]
        self.__turn_stage = TurnStage.PLAYER_TURN # player goes first
        self.__last_action_time = time.time() 
        return messages

    def _handle_player_turn(self) -> list[Message]:
        """This function is called once before we await for player input."""
        self.clear_option()

        # Collect available attack options
        attack_options = []
        for i, attack in enumerate(self.__player_pokemon.known_attacks):
            attack_options.append(f"{i}: {attack['name']} ({attack['damage']})")

        utility_options = ["Dodge", "Run"]

        # Add switch option if other Pokémon are available (not fainted)
        bag = self.__player.get_state("bag")
        switch_option = []
        if bag.pokemon.get_available_pokemon():
            switch_option.append("Switch Pokemon")

        full_options = attack_options + utility_options + switch_option # combine all options

        self.__last_action_time = time.time()
        self.__turn_stage = TurnStage.AWAIT_INPUT

        return [OptionsMessage(self.__player, self.__player, full_options)] # present options to player

    def _handle_await_input(self) -> list[Message]:
        messages = []
        now = time.time()
        selected = self.__current_option
        if selected is None:
            return messages

        self.clear_option()
        name = self.__player.get_name()

        if self.__turn_stage == TurnStage.AWAIT_SWITCH:
            if selected == "Return":
                self.__turn_stage = TurnStage.PLAYER_TURN
                return [ServerMessage(self.__player, "Returning to main options.")]

            index = self.__switch_options_map.get(selected)
            if index is not None:
                bag = self.__player.get_state("bag")
                new_active = bag.pokemon.switch_pokemon(self.__player_pokemon, index)
                if new_active:
                    self.__player.set_state("active_pokemon", new_active)
                    self.__player.set_state("bag", bag)
                    self.__player_pokemon = new_active
                    self.__turn_stage = TurnStage.ENEMY_WAIT
                    return [
                        ServerMessage(self.__player, f"You switched to {new_active.name}!"),
                        self._make_battle_message()
                    ]
            return [ServerMessage(self.__player, "Invalid selection. Returning to main options.")]

        if selected == "Dodge":
            self.__used_dodge = True
            messages.append(ServerMessage(self.__player, f"({name}) {self.__player_pokemon.name} prepares to dodge!"))
            self.__turn_stage = TurnStage.ENEMY_WAIT

        elif selected == "Run":
            if random.random() < PLAYER_CHANCE_TO_RUN:
                messages.append(ServerMessage(self.__player, f"({name}) You ran away safely!"))
                self.__turn_stage = TurnStage.END
            else:
                messages.append(ServerMessage(self.__player, f"({name}) You tried to run but couldn't escape!"))
                self.__turn_stage = TurnStage.ENEMY_WAIT

        elif selected == "Switch Pokemon":
            bag = self.__player.get_state("bag")
            available = bag.pokemon.get_available_pokemon()
            if not available:
                messages.append(ServerMessage(self.__player, "No healthy Pokémon available to switch."))
                self.__turn_stage = TurnStage.PLAYER_TURN
                return messages

            switch_options = []
            self.__switch_options_map.clear()

            for index, ball in available:
                label = f"{ball.get_name()} HP: {ball.get_health()}"
                self.__switch_options_map[label] = index
                switch_options.append(label)

            switch_options.append("Return")
            self.__turn_stage = TurnStage.AWAIT_SWITCH
            return [
                ServerMessage(self.__player, "Choose a Pokémon to switch to:"),
                OptionsMessage(self.__player, self.__player, switch_options)
            ]

        elif ":" in selected and selected.split(":")[0].isdigit():
            attack_index = int(selected.split(":")[0])
            messages.extend(self._process_player_attack(attack_index))

        else: # debugging
            messages.append(ServerMessage(self.__player, "Unrecognized action."))
            self.__turn_stage = TurnStage.PLAYER_TURN

        self.__last_action_time = now
        return messages

    def _process_player_attack(self, index):
        messages = []
        player_name = self.__player.get_name()

        if 0 <= index < len(self.__player_pokemon.known_attacks):
            if self.__used_dodge and random.random() < OPPONENT_CHANCE_TO_DODGE:
                messages.append(ServerMessage(
                    self.__player,
                    f"(Opp) {self.__enemy_pokemon.name} dodged {self.__player_pokemon.known_attacks[index]['name']}!"
                ))
            else:
                if self.__used_dodge:
                    messages.append(ServerMessage(self.__player, f"(Opp) Dodge failed!"))

                result = self.__player_pokemon.attack(index, self.__enemy_pokemon)
                messages.append(ServerMessage(
                    self.__player,
                    f"({player_name}) {result['message']}"
                ))

                # Trigger stat update
                messages.append(self._make_battle_message())

                if result.get("evolved"):
                    self.__player.set_state("active_pokemon", result["evolved"])
                    self.__player_pokemon = result["evolved"]
                    messages.append(ServerMessage(
                        self.__player,
                        f"Your Pokémon evolved into {self.__player_pokemon.name}!"
                    ))

        self.__used_dodge = False

        # Flush observer messages before fainting logic
        messages.extend(self.__battle_messages)
        self.__battle_messages.clear()

        # Now handle fainting message after damage was shown
        if self.__enemy_pokemon.is_fainted():
            messages.append(ServerMessage(
                self.__player,
                f"(Opp) {self.__enemy_pokemon.name} has fainted! You won!"
            ))
            self.__turn_stage = TurnStage.END
        else:
            self.__turn_stage = TurnStage.ENEMY_WAIT

        return messages

    def _handle_enemy_turn(self):
        messages = []
        ai: EnemyAI = self.__player.get_state("enemy_ai", MediumAI())
        action = ai.choose_action(self.__enemy_pokemon, self.__player_pokemon)

        if action == "Dodge":
            messages.append(ServerMessage(self.__player, f"(Opp) {self.__enemy_pokemon.name} is preparing to dodge!"))
            self.__used_dodge = True
        else:
            attack_index = int(action)
            attack = self.__enemy_pokemon.known_attacks[attack_index]

            if self.__used_dodge and random.random() < PLAYER_CHANCE_TO_DODGE:
                messages.append(ServerMessage(
                    self.__player,
                    f"({self.__player.get_name()}) {self.__player_pokemon.name} dodged {attack['name']} attack!"
                ))
            else:
                if self.__used_dodge:
                    messages.append(ServerMessage(self.__player, "(Opp) Dodge failed!"))

                result = self.__enemy_pokemon.attack(attack_index, self.__player_pokemon)
                messages.append(ServerMessage(self.__player, f"(Opp) {result['message']}"))
                messages.append(self._make_battle_message())

        self.__used_dodge = False

        # Flush health change messages from observers
        messages.extend(self.__battle_messages)
        self.__battle_messages.clear()

        if self.__player_pokemon.is_fainted():
            messages.append(ServerMessage(
                self.__player,
                f"({self.__player.get_name()}) {self.__player_pokemon.name} has fainted! You lost."
            ))
            self.__turn_stage = TurnStage.END
        else:
            self.__turn_stage = TurnStage.PLAYER_TURN

        self.__last_action_time = time.time()
        return messages

    def _handle_end(self) -> list[Message]:
        """Send end message and destroy windows."""
        messages = [
            ServerMessage(self.__player, "The battle has ended!"),
            OptionsMessage(self.__player, self.__player, [], destroy=True),
            PokemonBattleMessage(self.__player, self.__player, {}, {}, destroy=True)
        ]
        self.__turn_stage = TurnStage.CLEANUP
        return messages
