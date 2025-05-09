from .imports import *
from collections.abc import Callable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
   
from .custom_NPCs import Nurse
from .pokemon import Pokemon
import random
from .bag import Bag
from .items import *
from .pokeball import *
from .pokedex import *
from enum import Enum, auto
from .custom_pressure_plates import PokeCounter
from .custom_keybinds import get_keybinds

class PokemonCenter(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Pokemon Center",
            description="Welcome to the Pokémon Center",
            size=(17, 17),
            entry_point=Coord(13, 7),
            background_tile_image='poke_center_tile',
            background_music='killswitch'
        )
        
    def _get_keybinds(self):
        keybinds = super()._get_keybinds()
        keybinds.update(get_keybinds(self))
        return keybinds
        
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []

        # add a door
        door = Door('mat', linked_room="Pokemon House")
        objects.append((door, Coord(14, 7)))
        # objects.append((MapObject.get_obj('wall'), Coord(0, 0)))
        # objects.append((MapObject.get_obj('wall'), Coord(0, 1)))
        # objects.append((MapObject.get_obj('wall'), Coord(0, 2)))
        # objects.append((MapObject.get_obj('wall'), Coord(0, 3)))
        # objects.append((MapObject.get_obj('wall'), Coord(0, 11)))
        # objects.append((MapObject.get_obj('wall'), Coord(0, 12)))
        # objects.append((MapObject.get_obj('wall'), Coord(0, 13)))
        # objects.append((MapObject.get_obj('wall'), Coord(0, 14)))
        #objects.append((MapObject.get_obj('l'), Coord(0, 4)))


        nurse = Nurse(
            encounter_text="Hello, I am Nurse Joy, Allow me to heal your active Pokémon!",
            staring_distance=2,
        )
        objects.append((nurse, Coord(2, 7)))
        main_counter = PokeCounter(nurse)
        objects.append((main_counter, Coord(0, 4)))
        nurse2 = Nurse(
            encounter_text="Hello, I am Nurse Alicia, Allow me to heal your active Pokémon!",
            staring_distance=2,
            facing_direction='right'
        )
        objects.append((nurse2, Coord(7, 0)))
        left_counter = PokeCounter(nurse2, "ff")
        objects.append((left_counter, Coord(6, 0)))

        

        #objects.append((MapObject.get_obj('c_l'), Coord(6, 0)))
        objects.append((MapObject.get_obj('sofa_table'), Coord(5, 11)))
        objects.append((MapObject.get_obj('sofa_table'), Coord(10, 11)))
        objects.append((MapObject.get_obj('sofa_table_2'), Coord(11, 0)))
        objects.append((MapObject.get_obj('bookshelf'), Coord(1, 0)))
        objects.append(((MapObject('poke_floor', passable=True)), Coord(7,6)))
        objects.append(((MapObject('shadow', passable=True)), Coord(4,4)))
        objects.append((MapObject.get_obj('poke_tree'), Coord(2, 14)))
        objects.append((MapObject.get_obj('poke_tree'), Coord(12, 14)))
        
        self._validate_coordinates(objects)

        return objects
        
    def _validate_coordinates(self, objects: list[tuple["MapObject", "Coord"]]) -> None:
        """Raises an error if any Coord in the object list is outside the map bounds."""
        for obj, coord in objects:
            if not (0 <= coord.y < self._map_rows and 0 <= coord.x < self._map_cols):
                raise ValueError(
                    f"Invalid Coord: ({coord.y}, {coord.x}) for object {obj.__class__.__name__}. "
                    f"Map size is ({self._map_rows}, {self._map_cols})"
                )
    

