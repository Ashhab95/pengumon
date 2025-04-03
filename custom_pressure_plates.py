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
        
        # TODO
        # Check if active pokemon is fainted and pokemon in inventory is also fainted
        
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