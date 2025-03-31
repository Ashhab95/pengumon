from .imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *

class HealActivePokemonPlate(PressurePlate):
    
    def __init__(self):
        super().__init__(image_name="green_circle", stepping_text="Your Pokémon feels refreshed!")

    def player_entered(self, player) -> list[Message]:
        active_pokemon = player.get_state("active_pokemon", None) # get the player's active pokemon

        if active_pokemon is None:
            return [DialogueMessage(self, player, "You don’t have an active Pokémon to heal.", "")]
        
        if active_pokemon.current_health == active_pokemon.max_health:
            return [DialogueMessage(self, player, "Your Pokémon is already at full health.", "")]

        active_pokemon.current_health = active_pokemon.max_health # fully heal the pokemon
        player.set_state("active_pokemon", active_pokemon) # update player state with pokemon after healing

        return [DialogueMessage(self, player, f"{active_pokemon.name} was fully healed!", "")]

class Nurse(NPC):
    def __init__(self, encounter_text: str, staring_distance: int = 0,) -> None:
        super().__init__(
            name="Nurse Joy",
            image='joy3',
            encounter_text=encounter_text,
            staring_distance=staring_distance,
        )



class PokemonCenter(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Pokemon Center",
            description="Welcome to the Pokemon Center",
            size=(15, 15),
            entry_point=Coord(13, 7),
            background_tile_image='wood_brown',
        )

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []

        # add a door
        door = Door('int_entrance', linked_room="Pokemon House")
        objects.append((door, Coord(14, 7)))

        objects.append((HealActivePokemonPlate(), Coord(3, 8)))

        objects.append((MapObject.get_obj('counter_l'), Coord(0, 1)))
        objects.append((MapObject.get_obj('counter_r'), Coord(0, 7)))

        objects.append((MapObject.get_obj('counter_u'), Coord(4, 0)))
        objects.append((MapObject.get_obj('counter_d'), Coord(8, 0)))
        objects.append((MapObject.get_obj('sofa'), Coord(5, 11)))
        objects.append((MapObject.get_obj('table'), Coord(6, 12)))
        objects.append((MapObject.get_obj('sofa'), Coord(7, 11)))

        objects.append((MapObject.get_obj('sofa'), Coord(9, 11)))
        objects.append((MapObject.get_obj('table'), Coord(10, 12)))
        objects.append((MapObject.get_obj('sofa'), Coord(11, 11)))
        
        nurse = Nurse(
            encounter_text="Hello I am Nurse Joy, Please step on the plate beside you to heal your active Pokemon!",
            staring_distance=3,
        )
        nurse1 = Nurse(
            encounter_text="Did you know that water type has a type advantage of fire type?",
            staring_distance=3,
        )
        nurse2 = Nurse(
            encounter_text="Always make sure to carry potions in order to take care of your pokemon during battles!",
            staring_distance=3,
        )
        objects.append((nurse, Coord(2, 5)))
        objects.append((nurse1, Coord(7, 3)))
        objects.append((nurse2, Coord(10, 3)))
        

        #need to fix nurse facing
        
        


        return objects

