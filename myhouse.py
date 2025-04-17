from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from tiles.buildings import Building


# Our imports   
import time
from .pokemon import *
from .items import PotionFlyweightFactory 
from .pokeball import *
from .bag import Bag
from .enemyAI import *
from enum import Enum, auto
from typing import Literal
from collections.abc import Callable
from .custom_pressure_plates import *
from .custom_NPCs import ProfessorOak, Nurse
from .custom_buildings import PokemonCenter
from .pokedex import *
from .custom_keybinds import get_keybinds

class PokemonHouse(Map):
    MAIN_ENTRANCE = True
    def __init__(self) -> None:
        super().__init__(
            name="Pokemon House",
            description="Welcome to the Kanto region!",
            size=(30, 30),
            entry_point=Coord(26, 26),
            background_tile_image='p_grass',
            background_music='swimming'
        )
        
    def _get_keybinds(self):
        """Override the _get_keybinds method to add custom keybinds."""
        keybinds = super()._get_keybinds()
        keybinds.update(get_keybinds(self))
        return keybinds
    
    def _add_trees(self, objects, start_pos, end_pos, step=1, tree_type="tree_lar", direction="horizontal"):
        """Helper method to add trees to the map."""
        i_start, j_start = start_pos
        i_end, j_end = end_pos

        if direction == "horizontal":
            for j in range(j_start, j_end, step):
                if 0 <= i_start < self._map_rows-1 and 0 <= j < self._map_cols-1:
                    tree = ExtDecor(tree_type)
                    objects.append((tree, Coord(i_start, j)))

        elif direction == "vertical":
            for i in range(i_start, i_end, step):
                if 0 <= i < self._map_rows-1 and 0 <= j_start < self._map_cols-1:
                    tree = ExtDecor(tree_type)
                    objects.append((tree, Coord(i, j_start)))

        elif direction == "area":
            for i in range(i_start, i_end + 1, step):
                for j in range(j_start, j_end + 1, step):
                    if 0 <= i < self._map_rows-1 and 0 <= j < self._map_cols-1:
                        tree = ExtDecor(tree_type)
                        objects.append((tree, Coord(i, j)))

    def _add_tile_line(self, objects, tile_name: str, start: tuple[int, int], end: tuple[int, int]):
        """Helper Method to add a layer of tile background on top of existing background"""
        y1, x1 = start
        y2, x2 = end

        if y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                tile = MapObject.get_obj(tile_name)
                tile._MapObject__z_index = 0
                objects.append((tile, Coord(y1, x)))
        elif x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                tile = MapObject.get_obj(tile_name)
                tile._MapObject__z_index = 0
                objects.append((tile, Coord(y, x1)))

    def place(self, objects, tile_name: str, position: tuple[int, int]):
        """Helper Method to add a layer of tile background on top of existing background
            on one specific tile.
        """
        y, x = position
        tile = MapObject.get_obj(tile_name)
        tile._MapObject__z_index = 0
        objects.append((tile, Coord(y, x)))
  
    def _add_bushes_with_plates(self, objects, start_pos, end_pos, evolution_stage=1, plate_probability=0.8):
        """Add an area of bushes with random PokemonBattlePressurePlates beneath."""
        i_start, j_start = start_pos
        i_end, j_end = end_pos

        # Define pools of Pokémon based on evolution stage
        evolution_pools = {
            1: ["Charmander", "Squirtle", "Bulbasaur", "Chimchar", "Piplup", "Turtwig"],
            2: ["Charmeleon", "Wartortle", "Ivysaur", "Monferno", "Prinplup", "Grotle"],
            3: ["Charizard", "Blastoise", "Venusaur", "Infernape", "Empoleon", "Torterra"],
        }

        for i in range(i_start, i_end + 1):
            for j in range(j_start, j_end + 1):
                if 0 <= i < self._map_rows and 0 <= j < self._map_cols:
                    if random.random() < plate_probability:
                        possible_pokemon = evolution_pools.get(evolution_stage, [])
                        if possible_pokemon:
                            chosen = random.choice(possible_pokemon)
                            plate = PokemonBattlePressurePlate(chosen)
                            objects.append((plate, Coord(i, j)))
                    else:
                        bush = ExtDecor("bushh")
                        bush._MapObject__passable = True
                        objects.append((bush, Coord(i, j)))
    
    def add_pressure_plate(self, objects, plate_class, position: tuple[int, int], **kwargs):
        """Helper Method to add our custom pressure plates on the map"""
        y, x = position
        coord = Coord(y, x)
        plate = plate_class(position=coord, **kwargs)
        objects.append((plate, coord))
    

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []
        
        # Add a door to exit back to Trottier Town
        door = Door('tube', linked_room="Trottier Town", is_main_entrance=True)
        objects.append((door, Coord(26, 27)))
        
        
        #pokemon_battle_plate = PokemonBattlePressurePlate("Infernape")
        #objects.append((pokemon_battle_plate, Coord(19, 26)))
        
        
        potion_plate = PokeballPressurePlate(position=Coord(19, 27))
        objects.append((potion_plate, Coord(19, 27)))
       
       # Create a border of trees
        # Bottom row
        self._add_trees(objects, (self._map_rows - 3, 2), (self._map_rows - 3, self._map_cols - 1), step=2)
        # Left column
        self._add_trees(objects, (1, 0), (self._map_rows - 1, 0),step=2, direction="vertical")
        # Right column
        self._add_trees(objects, (1, 28), (self._map_rows - 1, 28), step = 2,  direction="vertical")
        # Top row
        self._add_trees(objects, (0, 2), (0, self._map_cols - 2), step=2)
            
        # Add tree rows above entry path
        self._add_trees(objects, (21, 4), (21, 27), step=2)
        self._add_trees(objects, (22, 4), (22, 23), step=2)
        
        reset_plate = ResetPlate()
        objects.append((reset_plate, Coord(24, 27)))
        
        choose_difficulty_plate = ChooseDifficultyPlate()
        objects.append((choose_difficulty_plate, Coord(24, 26)))
        

        self._add_tile_line(objects, 'poke_sand_up', start=(25, 4), end=(25, 25))
        self._add_tile_line(objects, 'poke_sand_down', start=(26, 2), end=(26, 25))
        self.place(objects,'bottom_left', (26,2))
        self._add_tile_line(objects, 'sand_left', start=(25, 2), end=(18, 2))
        self._add_tile_line(objects, 'sand_right', start=(24, 3), end=(18, 3))
        self.place(objects, 'poke_sand', (25, 3))
        self.place(objects, 'top_left', (18, 2))
        self.place(objects, 'top_right', (18, 3))
        self.place(objects, 'top_right', (25, 26))
        self.place(objects, 'bottom_right', (26, 26))

        sign = Sign(text="You can view hints by clicking on h! ")
        objects.append((sign, Coord(26, 2)))

        prof = ProfessorOak(
            facing_direction="down",
            staring_distance=3,
        )
        objects.append((prof, Coord(24, 24)))
  

        

        self._add_trees(objects, (15, 2), (15, 16),step=1, tree_type="tree_f")
        self._add_bushes_with_plates(objects, (18, 4), (20, 7), evolution_stage=1, plate_probability=0.5)
        
        #path after the first bush 
        self._add_tile_line(objects, 'g_up', start=(19, 9), end=(19, 14))
        self._add_tile_line(objects, 'g_down', start=(20, 9), end=(20, 14))
        self.place(objects, 'g_top_left', (19, 8))
        self.place(objects, 'g_bottom_left', (20, 8))
        self.place(objects, 'g_top_left', (19, 8))
        self.place(objects, 'g_bottom_right', (20, 15))
        self.place(objects, 'g_top_right', (19, 15))


        
        self._add_bushes_with_plates(objects, (7, 22), (9, 27), evolution_stage=1, plate_probability=0.4)
        self._add_bushes_with_plates(objects, (3, 22), (6, 27), evolution_stage=2, plate_probability=0.7)
        objects.append((MapObject.get_obj('flower_r'), Coord(3, 21)))
        objects.append((MapObject.get_obj('flower_r'), Coord(4, 21)))
        objects.append((MapObject.get_obj('flower_r'), Coord(8, 21)))
        objects.append((MapObject.get_obj('flower_r'), Coord(9, 21)))
        # self.place(objects, 'fence', (10, 22))
       
        building = PokemonCenter(linked_room_str="Pokemon Center")
        objects.append((building, Coord(11, 23)))
        sign = Sign(text="Welcome to the Pokemon Center")
        objects.append((sign, Coord(15, 23)))
        '''
        nurse = Nurse(
            encounter_text="Hello, I am Nurse Joy, Allow me to heal your active Pokémon!",
            staring_distance=2,
        )
        '''
        #objects.append((nurse, Coord(16, 22)))
        #path from pokemon center
        self.place(objects, 'top_left', (16, 24))
        self.place(objects, 'poke_sand_up', (16, 25))
        self.place(objects, 'top_right', (16, 26))
        self.place(objects, 'poke_sand', (17, 24))
        self.place(objects, 'poke_sand', (17, 25))
        self.place(objects, 'sand_right', (17, 26))
        self.place(objects, 'bottom_right', (18, 26))
        self._add_tile_line(objects, 'poke_sand_up', start=(17, 23), end=(17, 18))
        self._add_tile_line(objects, 'poke_sand_down', start=(18, 25), end=(18, 18))
        self.place(objects, 'bottom_left', (18, 17))
        self._add_tile_line(objects, 'sand_left', start=(17, 17), end=(7, 17))
        self._add_tile_line(objects, 'poke_sand', start=(17, 18), end=(7, 18))
        self._add_tile_line(objects, 'sand_right', start=(16, 19), end=(7, 19))
        self.place(objects, 'poke_sand', (17, 19))
        self.place(objects, 'top_left', (6, 17))
        self.place(objects, 'top_right', (6, 19))
        self.place(objects, 'poke_sand_up', (6, 18))
        
        
        
        objects.append((MapObject.get_obj('big_rock'), Coord(5, 8)))
        objects.append((MapObject.get_obj('flower_r'), Coord(12, 13)))
        objects.append((MapObject.get_obj('flower_r'), Coord(13, 13)))
        objects.append((MapObject.get_obj('flower_r'), Coord(14, 13)))
        objects.append((MapObject.get_obj('rock_led'), Coord(12, 14)))
        
        sign = Sign(text="Dangerous Pokemon's ahead, continue at your own risk. ")
        objects.append((sign, Coord(5, 15)))
        
        self.place(objects, 'g_top_left', (3, 6))
        self.place(objects, 'g_top_right', (3, 7))
        self._add_tile_line(objects, 'g_l', start=(4, 6), end=(12, 6))
        self._add_tile_line(objects, 'g_r', start=(4, 7), end=(13, 7))
        self.place(objects, 'g', (13, 6))
        self._add_tile_line(objects, 'g_up', start=(13, 3), end=(13, 5))
        self._add_tile_line(objects, 'g_down', start=(14, 3), end=(14, 6))
        self.place(objects, 'g_bottom_right', (14, 7))
        self.place(objects, 'g_bottom_left', (14, 2))
        self.place(objects, 'g_top_left', (13, 2))
        
        


        self._add_bushes_with_plates(objects, (7, 2), (12, 5), evolution_stage=2, plate_probability=0.6)
        self._add_bushes_with_plates(objects, (3, 8), (4,14), evolution_stage=1, plate_probability=0.6)
        self._add_bushes_with_plates(objects, (12, 9), (14,12), evolution_stage=2, plate_probability=0.6)
        self._add_bushes_with_plates(objects, (3, 2), (5, 4), evolution_stage=3, plate_probability=0.5)
        objects.append((MapObject.get_obj('rock_903'), Coord(3,5)))
        objects.append((MapObject.get_obj('rock_903'), Coord(4,5)))
        objects.append((MapObject.get_obj('rock_902'), Coord(6, 3)))
        
        self.place(objects, 'fence_2', (6, 3))
        self.place(objects, 'fence_2', (6, 4))
        self.place(objects, 'fence_2', (6, 5))


        self.add_pressure_plate(objects,PokeballPressurePlate,(4,20))
        self.add_pressure_plate(objects,PokeballPressurePlate,(18,8))
        self.add_pressure_plate(objects,PokeballPressurePlate,(3,15))
        self.add_pressure_plate(objects,PokeballPressurePlate,(3,20))
        self.add_pressure_plate(objects,PokeballPressurePlate,(18,9))
        self.add_pressure_plate(objects,PokeballPressurePlate,(14,15))
        self.add_pressure_plate(objects,PokeballPressurePlate,(12,8))


        self.add_pressure_plate(objects,PotionPressurePlate,(14,7))
        self.add_pressure_plate(objects,PotionPressurePlate,(3,11))
        self.add_pressure_plate(objects,PotionPressurePlate,(11,22))
        self.add_pressure_plate(objects,PotionPressurePlate,(16,27))
        self.add_pressure_plate(objects,PotionPressurePlate,(4,15))
        self.add_pressure_plate(objects,PotionPressurePlate,(20,16))
        self.add_pressure_plate(objects,PotionPressurePlate,(20,17))
        self.add_pressure_plate(objects,PotionPressurePlate,(13,8))
        self.add_pressure_plate(objects,PotionPressurePlate,(9,15))

        
        self.add_pressure_plate(objects, PotionPressurePlate, (14, 2), is_revive=True)
        self.add_pressure_plate(objects, PotionPressurePlate, (6, 2), is_revive=True)
        self.add_pressure_plate(objects, PotionPressurePlate, (13, 15), is_revive=True)
        self.add_pressure_plate(objects, PotionPressurePlate, (14, 8), is_revive=True)
        self.add_pressure_plate(objects, PotionPressurePlate, (18, 10), is_revive=True)
        self.add_pressure_plate(objects, PotionPressurePlate, (6, 15), is_revive=True)

        
        
        return objects
    

