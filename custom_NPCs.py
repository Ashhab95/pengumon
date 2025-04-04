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
from .items import *
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

    def give_starter_items(self, player: HumanPlayer) -> None:
        """Gives starting items to the player if not already given."""
        if player.get_state("starter_items_given", False) is not True:
            bag = Bag()

            # Add potions
            bag.potions.add(SmallPotion())
            bag.potions.add(MediumPotion())

            # Add pokeballs
            bag.pokeballs.add(RegularPokeball())
        
            # Attach the new bag to player
            player.set_state("bag", bag.to_dict())
            player.set_state("starter_items_given", True)

    def player_interacted(self, player: HumanPlayer) -> list[Message]:
        messages: list[Message] = []

        starter_pokemon = player.get_state("starter_pokemon", None)

        if starter_pokemon:
            messages.append(ServerMessage(player, f"You have already chosen {starter_pokemon} as your starter Pokémon!"))
            return messages

        # First-time interaction
        messages.append(ServerMessage(player, self._NPC__encounter_text))

        # Set Professor Oak as the current menu handler
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
        pokemon = PokemonFactory.create_pokemon(choice)
        player.set_state("starter_pokemon", pokemon.name)
        player.set_state("active_pokemon", pokemon.to_list())

        # Give starter items after selection
        self.give_starter_items(player)

        player.set_current_menu(None) # clear menu handler

        return [ServerMessage(player, f"Excellent choice! Take good care of {pokemon.name}.")]


    
    
class Nurse(NPC):
    def __init__(self, encounter_text: str, staring_distance: int = 0, facing_direction: Literal['up', 'down', 'left', 'right'] = 'down') -> None:
        super().__init__(
            name="Nurse Joy",
            image='joy5',
            encounter_text=encounter_text,
            facing_direction=facing_direction,
            staring_distance=staring_distance,
        )
        
    def done_talking(self, player) -> bool:
        """Override to allow re-interaction even after first contact."""
        return False

    def player_interacted(self, player: HumanPlayer) -> list[Message]:
        messages: list[Message] = []

        # Initial dialogue
        messages.append(ServerMessage(player, self._NPC__encounter_text))

        # --- Load and heal active Pokémon ---
        active_data = player.get_state("active_pokemon", None)
        if active_data is None:
            messages.append(ServerMessage(player, "You don’t have a Pokémon to heal."))
            return messages

        active_pokemon = Pokemon.from_list(active_data)

        if active_pokemon.current_health < active_pokemon.max_health:
            active_pokemon.current_health = active_pokemon.max_health
            messages.append(ServerMessage(player, f"{active_pokemon.name} was fully healed!"))
        else:
            messages.append(ServerMessage(player, f"{active_pokemon.name} is already at full health."))

        # --- Load and heal Pokémon in the bag ---
        bag_data = player.get_state("bag", None)
        if bag_data:
            bag = Bag.from_dict(bag_data)
            healed_any = False

            for pokeball in bag.pokemon.stored_pokemon:
                if not pokeball.is_empty():
                    pokemon = pokeball.captured_pokemon
                    if pokemon.current_health < pokemon.max_health:
                        pokemon.current_health = pokemon.max_health
                        healed_any = True
                        messages.append(ServerMessage(player, f"{pokemon.name} in your bag was fully healed!"))

            if not healed_any:
                messages.append(ServerMessage(player, "All Pokémon in your bag are already at full health."))

            player.set_state("bag", bag.to_dict())

        # Save updated active Pokémon
        player.set_state("active_pokemon", active_pokemon.to_list())

        return messages