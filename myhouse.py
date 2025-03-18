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
            description="Welcome to the Kanto region!",
            size=(30, 30),
            entry_point=Coord(26, 26),
            background_tile_image='grass',
        )
    
    
    def add_ext_decor(self, objects, start_pos, end_pos, step=2, decor_type="tree_large_1", direction="horizontal"):
        """Helper method to add exterior decorations in a line
        
        Args:
            objects: List to append objects to
            start_pos: Starting coordinate (i, j)
            end_pos: Ending coordinate (i, j)
            step: Spacing between decorations
            decor_type: Type of decoration to place
            direction: "horizontal" or "vertical"
        """
        i_start, j_start = start_pos
        i_end, j_end = end_pos
        
        if direction == "horizontal":
            for j in range(j_start, j_end, step):
                if 0 <= i_start < self._map_rows-1 and 0 <= j < self._map_cols-1:
                    decor = ExtDecor(decor_type)
                    objects.append((decor, Coord(i_start, j)))
        else:  # vertical
            for i in range(i_start, i_end, step):
                if 0 <= i < self._map_rows-1 and 0 <= j_start < self._map_cols-1:
                    decor = ExtDecor(decor_type)
                    objects.append((decor, Coord(i, j_start)))
            """Helper method to add trees in a line
            
            Args:
                objects: List to append objects to
                start_pos: Starting coordinate (i, j)
                end_pos: Ending coordinate (i, j)
                step: Spacing between trees
                tree_type: Type of tree to place
                direction: "horizontal" or "vertical"
            """
            i_start, j_start = start_pos
            i_end, j_end = end_pos
            
            if direction == "horizontal":
                for j in range(j_start, j_end, step):
                    if 0 <= i_start < self._map_rows-1 and 0 <= j < self._map_cols-1:
                        tree = ExtDecor(decor_type)
                        objects.append((tree, Coord(i_start, j)))
            else:  # vertical
                for i in range(i_start, i_end, step):
                    if 0 <= i < self._map_rows-1 and 0 <= j_start < self._map_cols-1:
                        tree = ExtDecor(decor_type)
                        objects.append((tree, Coord(i, j_start)))
    
    def add_background(self, objects, start_pos, end_pos, bg_type="sand", direction="horizontal", radius=None, center=None):
        i_start, j_start = start_pos
        
        if direction == "horizontal":
            i_end, j_end = end_pos
            for j in range(j_start, j_end + 1):
                if 0 <= i_start < self._map_rows and 0 <= j < self._map_cols:
                    objects.append((Background(bg_type), Coord(i_start, j)))
        
        elif direction == "vertical":
            i_end, j_end = end_pos
            for i in range(i_start, i_end + 1):
                if 0 <= i < self._map_rows and 0 <= j_start < self._map_cols:
                    objects.append((Background(bg_type), Coord(i, j_start)))
        
        elif direction == "circle":
            if radius is None:
                raise ValueError("Radius must be provided for circle mode")
            
            center_i, center_j = center if center else start_pos
            radius_squared = radius * radius
            
            min_i = max(0, center_i - radius)
            max_i = min(self._map_rows - 1, center_i + radius)
            min_j = max(0, center_j - radius)
            max_j = min(self._map_cols - 1, center_j + radius)
            
            for i in range(min_i, max_i + 1):
                for j in range(min_j, max_j + 1):
                    distance_squared = (i - center_i)**2 + (j - center_j)**2
                    
                    if distance_squared <= radius_squared:
                        objects.append((Background(bg_type), Coord(i, j)))
        
        else:  # rectangle
            i_end, j_end = end_pos
            for i in range(i_start, i_end + 1):
                for j in range(j_start, j_end + 1):
                    if 0 <= i < self._map_rows and 0 <= j < self._map_cols:
                        objects.append((Background(bg_type), Coord(i, j)))
    
    def add_area(self, objects, start_pos, end_pos, obj_type_func, passable=False):

        """Helper method to add objects in a rectangular area
        
        Args:
            objects: List to append objects to
            start_pos: Starting coordinate (i, j)
            end_pos: Ending coordinate (i, j)
            obj_type_func: Function that creates the object
            passable: Whether the object should be passable
        """
        i_start, j_start = start_pos
        i_end, j_end = end_pos
        
        for i in range(i_start, i_end + 1):
            for j in range(j_start, j_end + 1):
                if 0 <= i < self._map_rows and 0 <= j < self._map_cols:
                    obj = obj_type_func()
                    if passable:
                        obj._MapObject__passable = True
                    objects.append((obj, Coord(i, j)))
    
    def add_bushes_with_plates(self, objects, start_pos, end_pos, plate_probability=0.8):
        """Add an area of bushes with random pressure plates underneath
        
        Args:
            objects: List to append objects to
            start_pos: Starting coordinate (i, j)
            end_pos: Ending coordinate (i, j)
            plate_probability: Probability of a pressure plate under each bush
        """
        i_start, j_start = start_pos
        i_end, j_end = end_pos
        
        bush_positions = []
        
        # Add all the bushes
        for i in range(i_start, i_end + 1):
            for j in range(j_start, j_end + 1):
                if 0 <= i < self._map_rows and 0 <= j < self._map_cols:
                    bush = ExtDecor("bush")
                    bush._MapObject__passable = True
                    objects.append((bush, Coord(i, j)))
                    bush_positions.append((i, j))
        
        # Randomly add pressure plates
        for i, j in bush_positions:
            if random.random() < plate_probability:
                pressure_plate = ScorePressurePlate()  #this needs to be changed to invoke our battle ui 
                objects.append((pressure_plate, Coord(i, j)))
    
    
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []
        
        # Add a door to exit back to Trottier Town
        door = Door('tube', linked_room="Trottier Town")
        objects.append((door, Coord(26, 25)))
        
        # pressure_plate = ScorePressurePlate()
        fight_pressure_plate = FightPressurePlate("Test")
        objects.append((fight_pressure_plate, Coord(26, 22)))
        
        # Create a border of trees
        # Bottom row
        self.add_ext_decor(objects, (self._map_rows - 3, 2), (self._map_rows - 3, self._map_cols - 1))
        
        # Left column
        self.add_ext_decor(objects, (1, 0), (self._map_rows - 1, 0), direction="vertical")
        
        # Right column
        self.add_ext_decor(objects, (1, 28), (self._map_rows - 1, 28), direction="vertical")
        
        # Top row
        self.add_ext_decor(objects, (0, 2), (0, self._map_cols - 2))
        
        # Create starting path
        for path_y in [26, 27]:
            end_x = 22 if path_y == 26 else 28
            self.add_background(objects, (path_y, 0), (path_y, end_x))
        
        # Add tree rows above paths
        for tree_row in [21, 22, 23]:
            self.add_ext_decor(objects, (tree_row, 3), (tree_row, 26))
        
        # Create vertical sand path
        self.add_background(objects, (10, 2), (25, 2), direction="vertical")

        # Create Professor Oak at position (26, 6)
        prof = Professor(
            encounter_text="Welcome to the Kanto region! I'm Professor Oak.\nYour very own Pokémon adventure is about to unfold!",
            staring_distance=0,  
            facing_direction='down'
        )
        objects.append((prof, Coord(25, 21)))
        
        # Add rock path along the top of the bush area (horizontal)
        self.add_ext_decor(objects, (16, 3), (16, 11), step=1, decor_type="rock_1")
        
        # Add rock path along the right of the bush area (vertical)
        self.add_ext_decor(objects, (16, 11), (21, 11), step=1, decor_type="rock_1", direction="vertical")
        
        # Adding bushes and pressure plates 
        self.add_bushes_with_plates(objects, (17, 3), (20, 10), plate_probability=0.5)
        
        return objects