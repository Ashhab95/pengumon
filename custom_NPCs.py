from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    
from typing import Literal
from .bag import Bag
from .items import PotionFlyweightFactory 
from .pokeball import *
from .pokemon import PokemonFactory

class ProfessorOak(NPC, SelectionInterface):
    def __init__(self, encounter_text: str = "Hello Pokémon trainer! I am Professor Oak! Choose your starter Pokémon!",
                 staring_distance: int = 3, facing_direction: Literal['up', 'down', 'left', 'right'] = 'down') -> None:
        super().__init__(
            name="Professor Oak",
            image='prof',
            encounter_text=encounter_text,
            facing_direction=facing_direction,
            staring_distance=staring_distance
        )

    def done_talking(self, player) -> bool:
        """Override to allow re-interaction even after first contact."""
        return False

    def player_interacted(self, player: HumanPlayer) -> list[Message]:
        messages: list[Message] = []

        starter_pokemon = player.get_state("starter_pokemon", None)
        print(f"[DEBUG] Oak sees starter_pokemon: {starter_pokemon}")

        if starter_pokemon:
            messages.append(ServerMessage(player, f"You have already chosen {starter_pokemon} as your starter pokemon"))
            return messages

        # First-time interaction
        messages.append(ServerMessage(player, self._NPC__encounter_text))
        # messages.append(DialogueMessage(self, player, self._NPC__encounter_text, ""))

        # Give starting items only once
        if player.get_state("starter_items_given", False) is not True:
            bag = Bag()
            bag.add_item(PotionFlyweightFactory.get_small_potion())
            bag.add_item(PotionFlyweightFactory.get_medium_potion())
            bag.add_item(RegularPokeball())
            bag.add_item(GreatBall())
            bag.add_item(MasterBall())
            player.set_state("bag", bag)
            player.set_state("starter_items_given", True)

        # Set this NPC as the current menu handler
        player.set_current_menu(self)

        # Starter Pokémon options
        options = [
            {"Charmander": "image/Pokemon/Charmander_front.png"},
            {"Squirtle": "image/Pokemon/Squirtle_front.png"},
            {"Bulbasaur": "image/Pokemon/Bulbasaur_front.png"}
        ]
        messages.append(ChooseObjectMessage(self, player, options, window_title="Choose your starter Pokémon!"))

        return messages

    def select_option(self, player: HumanPlayer, choice: str) -> list[Message]:
        print(f"[DEBUG] Oak received selected option: {choice}")

        pokemon = PokemonFactory.create_pokemon(choice)
        player.set_state("starter_pokemon", pokemon.name)
        player.set_state("active_pokemon", pokemon)
        player.set_state("pokeballs", [])

        player.set_current_menu(None)

        return [ServerMessage(player, f"Excellent choice! Take good care of {pokemon.name}.")]
    
    
    
class Nurse(NPC):
    def __init__(self, encounter_text: str, staring_distance: int = 3) -> None:
        super().__init__(
            name="Nurse Joy",
            image='joy3',
            encounter_text=encounter_text,
            facing_direction='down',
            staring_distance=staring_distance
        )
        
    def done_talking(self, player) -> bool:
        """Override to allow re-interaction even after first contact."""
        return False
    
    def player_interacted(self, player: HumanPlayer) -> list[Message]:
        messages: list[Message] = []

        # Initial dialogue
        messages.append(ServerMessage(player, self._NPC__encounter_text))

        # Get active Pokémon
        active_pokemon = player.get_state("active_pokemon", None)
        if active_pokemon is None:
            messages.append(ServerMessage(player, "You don’t have a Pokémon to heal."))
            return messages

        if active_pokemon.current_health == active_pokemon.max_health:
            messages.append(ServerMessage(player, "Your Pokémon is already at full health."))
            return messages

        # Heal the Pokémon
        active_pokemon.current_health = active_pokemon.max_health
        player.set_state("active_pokemon", active_pokemon)
        messages.append(ServerMessage(player, f"{active_pokemon.name} was fully healed!"))

        return messages
