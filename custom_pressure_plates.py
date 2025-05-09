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
from .bag import Bag
from .items import *
from .pokeball import *
from .pokemon import PokemonFactory
    

class PokemonBattlePressurePlate(PressurePlate, SelectionInterface):
    """Triggers a wild Pokémon battle when stepped on."""
    def __init__(self, wild_pokemon_name: str):
        super().__init__(image_name="bushh", stepping_text=f"You encountered a wild {wild_pokemon_name}!")
        self.__wild_pokemon_name = wild_pokemon_name
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
        poke_data = player.get_state("active_pokemon", None)
        
        # Check if the player has a active Pokémon
        if poke_data is None:
            return [ServerMessage(player, "You don't have a Pokémon! Visit Professor Oak to choose your starter.")]

        # This is a safeguard - only allow battle if active pokemon is not fainted
        active_pokemon = Pokemon.from_list(poke_data)

        # Check if the active pokemon is fainted
        if active_pokemon.is_fainted():
            return [ServerMessage(player, "Your active Pokémon is fainted! Fainted Pokémon cannot battle.")]

        self.__player = player
        self.__battle = PokemonBattleManager(player, self.__wild_pokemon_name)
        player.set_current_menu(self)
        
        return []

    def update(self) -> list[Message]:
        if not self.__battle:
            return []

        messages = self.__battle.update()

        if self.__battle.is_over():
            updated_pokemon = self.__battle.get_player_pokemon() # active pokemon at end of battle
            updated_bag = self.__battle.get_bag() # bag at end of battle
            self.__player.set_state("active_pokemon", updated_pokemon.to_list())
            self.__player.set_state("bag", updated_bag.to_dict())
            self.__player.set_current_menu(None) # clear menu
            self.__battle = None

        return messages


class ChooseDifficultyPlate(PressurePlate, SelectionInterface):
    """Allows the player to choose the difficulty level of enemy AI."""
    def __init__(self):
        super().__init__(image_name="hal9000", stepping_text="Choose your battle difficulty!")

    def player_entered(self, player) -> list[Message]:
        # Get string from state
        current_ai_level = player.get_state("enemy_ai", None)
        current_difficulty = current_ai_level.capitalize() if current_ai_level else "None"

        # Set this plate as active menu
        player.set_current_menu(self)

        return [
            ServerMessage(player, f"Current difficulty: {current_difficulty}\nChoose a new difficulty."),
            OptionsMessage(self, player, ["Easy", "Medium", "Hard"])
        ]

    def select_option(self, player, selected_option: str) -> list[Message]:
        # Map strings to lowercase keys for storage
        difficulty_map = {
            "Easy": "easy",
            "Medium": "medium",
            "Hard": "hard",
        }

        difficulty_key = difficulty_map.get(selected_option)
        if difficulty_key:
            # Store just the lowercase string in player state
            player.set_state("enemy_ai", difficulty_key)
            player.set_current_menu(None)

            return [
                ServerMessage(player, f"Difficulty set to {selected_option}."),
                OptionsMessage(self, player, [], destroy=True)
            ]

        return [ServerMessage(player, "Invalid difficulty selection.")]
    


class PotionPressurePlate(PressurePlate):
    """Gives the player a random healing or revive potion when stepped on."""
    def __init__(self, position: Coord, is_revive: bool = False):
        self.__pos = position
        self.is_revive = is_revive

        # Randomly choose one of the base potion classes
        potion_classes = [SmallPotion, MediumPotion, LargePotion]
        self.potion_class = random.choice(potion_classes)
        base_potion: Item = self.potion_class()

        if is_revive:
            self.potion: Item = RevivePotion(base_potion)
            potion_to_image = {
                SmallPotion: "revive_small",
                MediumPotion: "revive_medium",
                LargePotion: "revive_large"
            }
            stepping_text = "You stepped on a revive pad!"
        else:
            self.potion: Item = base_potion
            potion_to_image = {
                SmallPotion: "heal_smal",
                MediumPotion: "heal_mediu",
                LargePotion: "heal_ful"
            }
            stepping_text = "You stepped on a potion pad!"

        image_name = potion_to_image.get(self.potion_class, "blue_circle")
        super().__init__(image_name=image_name, stepping_text=stepping_text)

    def player_entered(self, player) -> list:
        # Load and update bag
        bag_data = player.get_state("bag")
        bag = Bag.from_dict(bag_data)
        bag.potions.add(self.potion)
        player.set_state("bag", bag.to_dict())

        # Remove this pressure plate from the map
        if self.__pos is not None:
            game_map: Map = player.get_current_room()
            game_map.remove_from_grid(map_obj=self, start_pos=self.__pos)

        return [ServerMessage(player, f"You found a {self.potion.get_name()}! It has been added to your bag.")]


class PokeballPressurePlate(PressurePlate):
    """Grants the player a random type of Pokéball when stepped on."""
    def __init__(self, position: Coord):
        # Randomly assign a Pokeball type to this plate
        pokeball_classes = [RegularPokeball, GreatBall, UltraBall, MasterBall]
        self.pokeball_class = random.choice(pokeball_classes)
        self.__pos = position

        # Determine image name based on Pokeball type
        pokeball_to_image = {
            RegularPokeball: "poke",
            GreatBall: "great",
            UltraBall: "ultra",
            MasterBall: "master"
        }
        image_name = pokeball_to_image.get(self.pokeball_class, "blue_circle")

        super().__init__(image_name=image_name, stepping_text="You stepped on a Pokéball pad!")

    def player_entered(self, player) -> list:
        pokeball = self.pokeball_class()

        # Load and update the player's bag
        bag_data = player.get_state("bag")
        bag = Bag.from_dict(bag_data)
        bag.pokeballs.add(pokeball)
        player.set_state("bag", bag.to_dict())

        # Remove this pressure plate from the map
        if self.__pos is not None:
            game_map: Map = player.get_current_room()
            game_map.remove_from_grid(map_obj=self, start_pos=self.__pos)

        return [ServerMessage(player, f"You found a {pokeball.name}! It has been added to your bag.")]
    
    
class ResetPlate(PressurePlate):
    """Resets all player progress and state variables."""
    def __init__(self):
        super().__init__(image_name="red_down_arrow", stepping_text="Resetting your progress...")

    def player_entered(self, player: HumanPlayer) -> list[Message]:
        # Reset all persistent player state variables
        player.set_state("starter_pokemon", None)
        player.set_state("active_pokemon", None)
        player.set_state("enemy_ai", None)
        player.set_state("bag", None)
        player.set_state("starter_items_given", None)

        return [ServerMessage(player, "All your progress has been reset. You may start fresh!")]
    
    
class PokeCounter(Counter):
    """A specialized counter object for interaction with Nurse Joy to heal pokemon."""
    def __init__(self, npc: "NPC", image_name="f") -> None:
        super().__init__(image_name, npc)