from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *

class ScorePressurePlate(PressurePlate):
    def __init__(self, image_name='pressure_plate'):
        super().__init__(image_name)
    
    def player_entered(self, player) -> list[Message]:
        messages = super().player_entered(player)
        # add score to player
        player.set_state("score", player.get_state("score") + 1)
        return messages

class PokemonHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Pokemon House",
            description="Welcome to the Pokemon House!",
            size=(30, 30),
            entry_point=Coord(27, 27),  # Center of the map
            background_tile_image='grass',
        )
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []
        
        # Create a border of trees
        # Top row (y=0)
        for j in range(self._map_cols-1):  # 0 to 28
            if j != 15:  # Skip position 15,0 for the entrance
                objects.append((MapObject.get_obj("tree_small_1"), Coord(0, j)))
        
        # Bottom row (y=28)
        for j in range(self._map_cols-1):  # 0 to 28
            objects.append((MapObject.get_obj("tree_small_1"), Coord(28, j)))
        
        # Left column (x=0)
        for i in range(1, self._map_rows-1):  # 1 to 27
            objects.append((MapObject.get_obj("tree_small_1"), Coord(i, 0)))
        
        # Right column (x=28)
        for i in range(1, self._map_rows-1):  # 1 to 27
            objects.append((MapObject.get_obj("tree_small_1"), Coord(i, 28)))
        
        # Add a door to exit back to Trottier Town
        door = Door('tube', linked_room="Trottier Town")
        objects.append((door, Coord(27, 27)))  # Just inside the top border
        
        # Add a pressure plate in the center
        pressure_plate = ScorePressurePlate()
        objects.append((pressure_plate, Coord(25, 27)))  # Centered in the map
        
        return objects