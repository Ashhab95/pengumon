from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    
import time    
from .pokemon import *
from .battle_manager import PokemonBattleManager, TurnStage
from .enemyAI import *
    

class PokemonBattlePressurePlate(PressurePlate, SelectionInterface):
    def __init__(self, wild_pokemon_name: str):
        super().__init__(image_name="bushh", stepping_text=f"You encountered a wild {wild_pokemon_name}!")
        self.__wild_pokemon_name = wild_pokemon_name
        self.__current_option = None
        self.__turn_stage = TurnStage.IDLE
        self.__last_action_time = time.time()

        self.__player = None
        self.__battle = None

    def select_option(self, player, selected_option: str) -> list[Message]:
        if self.__battle:
            self.__battle.set_selected_option(selected_option)
        return []

    def clear_option(self) -> None:
        if self.__battle:
            self.__battle.clear_option()

    def player_entered(self, player) -> list[Message]:
        # This is a safeguard - only allow battle if player has chosen starter pokemon
        active_pokemon = player.get_state("active_pokemon", None)
        if active_pokemon is None:
            return [ServerMessage(player, "You don't have a Pokémon! Visit Professor Oak to choose your starter.")]
        
        if active_pokemon.is_fainted():
            return [ServerMessage(player, "Your active Pokémon is fainted! Fainted Pokémon cannot battle.")]
        
        self.__player = player
        self.__battle = PokemonBattleManager(player, self.__wild_pokemon_name)
        self.__turn_stage = TurnStage.INTRO
        self.__last_action_time = time.time()

        player.set_current_menu(self)
        return []

    def update(self) -> list[Message]:
        if not self.__battle:
            return []

        messages = self.__battle.update()
        
        if self.__battle.is_over():
            self.__player.set_state("active_pokemon", self.__battle.get_player_pokemon())
            self.__player.set_current_menu(None)
            self.__battle = None

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
    

class SwitchActivePokemonPlate(PressurePlate, SelectionInterface):
    def __init__(self):
        super().__init__(image_name="blue_circle", stepping_text="You stepped on a Pokémon switching pad!")
        self.__player = None
        self.__current_option = None
        self.__options_map: dict[str, int] = {}  # Maps option strings to compartment indices

    def player_entered(self, player) -> list[Message]:
        self.__player = player
        bag = player.get_state("bag", None)

        if not bag:
            return [ServerMessage(player, "You don't have a bag yet! Please visit Professor Oak.")]

        available = bag.pokemon.get_available_pokemon()
        if not available:
            return [ServerMessage(player, "You don't have any healthy Pokémon to switch to!")]

        options = []
        self.__options_map.clear()

        for index, ball in available:
            label = f"{ball.get_name()} HP: {ball.get_health()}"
            self.__options_map[label] = index
            options.append(label)

        options.append("Exit")  # give user an option to exit
        player.set_current_menu(self)

        return [
            ServerMessage(player, "Choose a Pokémon to set as your active Pokémon:"),
            OptionsMessage(self, player, options)
        ]

    def select_option(self, player, selected_option: str) -> list[Message]:
        bag = player.get_state("bag", None) 

        if selected_option == "Exit":
            player.set_current_menu(None)
            return [
                ServerMessage(player, "You chose not to switch active Pokémon."),
                OptionsMessage(self, player, [], destroy=True)
            ]

        index = self.__options_map.get(selected_option)

        if index is not None:
            old_active_pokemon = player.get_state("active_pokemon", None)

            # Swap the Pokémon
            new_active_pokemon = bag.pokemon.switch_pokemon(old_active_pokemon, index)
                
            # Set the new bag state
            player.set_state("bag", bag)

            if new_active_pokemon:
                player.set_state("active_pokemon", new_active_pokemon)
                player.set_current_menu(None)
                return [
                    ServerMessage(player, f"{new_active_pokemon.name} is now your active Pokémon!"),
                    OptionsMessage(self, player, [], destroy=True)
                ]
                
        return []


    def clear_option(self) -> None:
        self.__current_option = None