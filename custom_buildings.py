from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from tiles.buildings import Building
    
class PokemonCenter(Building):
    def __init__(self, linked_room_str: str = "") -> None:
        super().__init__('p1', door_position=Coord(4, 2), linked_room_str=linked_room_str)