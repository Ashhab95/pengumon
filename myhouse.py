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
from .custom_NPCs import ProfessorOak


class PokemonCenter(Building):
    def __init__(self, linked_room_str: str = "") -> None:
        super().__init__('pokemon_center', door_position=Coord(5, 3), linked_room_str=linked_room_str)

            
# class ProfessorOak(NPC, SelectionInterface):
#     def __init__(self, encounter_text: str = "Welcome to the Kanto Region. Choose your starter Pokémon!",
#                  staring_distance: int = 3, facing_direction: Literal['up', 'down', 'left', 'right'] = 'down') -> None:
#         super().__init__(
#             name="Professor Oak",
#             image='prof',
#             encounter_text=encounter_text,
#             facing_direction=facing_direction,
#             staring_distance=staring_distance
#         )

#     def done_talking(self, player) -> bool:
#         """Override to allow re-interaction even after first contact."""
#         return False

#     def player_interacted(self, player: HumanPlayer) -> list[Message]:
#         messages: list[Message] = []

#         starter_pokemon = player.get_state("starter_pokemon", None)
#         print(f"[DEBUG] Oak sees starter_pokemon: {starter_pokemon}")

#         if starter_pokemon:
#             messages.append(ServerMessage(player, f"You have already chosen {starter_pokemon} as your starter pokemon"))
#             return messages

#         # First-time interaction
#         messages.append(ServerMessage(player, self._NPC__encounter_text))
#         # messages.append(DialogueMessage(self, player, self._NPC__encounter_text, ""))

#         # Give starting items only once
#         if player.get_state("starter_items_given", False) is not True:
#             bag = Bag()
#             bag.add_item(PotionFlyweightFactory.get_small_potion())
#             bag.add_item(PotionFlyweightFactory.get_medium_potion())
#             bag.add_item(RegularPokeball())
#             bag.add_item(GreatBall())
#             bag.add_item(MasterBall())
#             player.set_state("bag", bag)
#             player.set_state("starter_items_given", True)

#         # Set this NPC as the current menu handler
#         player.set_current_menu(self)

#         # Starter Pokémon options
#         options = [
#             {"Charmander": "image/Pokemon/Charmander_front.png"},
#             {"Squirtle": "image/Pokemon/Squirtle_front.png"},
#             {"Bulbasaur": "image/Pokemon/Bulbasaur_front.png"}
#         ]
#         messages.append(ChooseObjectMessage(self, player, options, window_title="Choose your starter Pokémon!"))

#         return messages

#     def select_option(self, player: HumanPlayer, choice: str) -> list[Message]:
#         print(f"[DEBUG] Oak received selected option: {choice}")

#         pokemon = PokemonFactory.create_pokemon(choice)
#         player.set_state("starter_pokemon", pokemon.name)
#         player.set_state("active_pokemon", pokemon)
#         player.set_state("pokeballs", [])

#         player.set_current_menu(None)

#         return [ServerMessage(player, f"Excellent choice! Take good care of {pokemon.name}.")]
        

    
class PokemonHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Pokemon House",
            description="Welcome to the Kanto region!",
            size=(30, 30),
            entry_point=Coord(26, 26),
            background_tile_image='poke_grass',
        )
    
    def _add_trees(self, objects, start_pos, end_pos, step=1, tree_type="tree_lar", direction="horizontal"):
        """
        Helper method to add trees to the map.
        
        Args:
            objects: List to append objects to
            start_pos: (i, j) tuple, top-left corner
            end_pos: (i, j) tuple, bottom-right corner
            step: Gap between trees
            tree_type: Image name of tree
            direction: "horizontal", "vertical", or "area"
        """
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
        y, x = position
        tile = MapObject.get_obj(tile_name)
        tile._MapObject__z_index = 0
        objects.append((tile, Coord(y, x)))
  
    def _add_bushes_with_plates(self, objects, start_pos, end_pos, evolution_stage=1, plate_probability=0.8):
        """Add an area of bushes with random PokemonBattlePressurePlates beneath.
        
        Args:
            objects: List to append objects to.
            start_pos: Top left corner coordinate (i, j) of the area.
            end_pos: Bottom right corner coordinate (i, j) of the area.
            evolution_stage: 1 (BASE), 2 (SECOND), or 3 (FINSL).
            plate_probability: Probability of placing a pressure plate under a bush.
        """
        i_start, j_start = start_pos
        i_end, j_end = end_pos

        # Define pools of Pokémon based on evolution stage
        evolution_pools = {
            1: ["Charmander", "Squirtle", "Bulbasaur"],
            2: ["Charmeleon", "Wartortle", "Ivysaur"],
            3: ["Charizard", "Blastoise", "Venusaur"]
        }

        for i in range(i_start, i_end + 1):
            for j in range(j_start, j_end + 1):
                if 0 <= i < self._map_rows and 0 <= j < self._map_cols:
                    if random.random() < plate_probability:
                        possible_pokemon = evolution_pools.get(evolution_stage, [])
                        if possible_pokemon:
                            chosen = random.choice(possible_pokemon)
                            plate = PokemonBattlePressurePlate(chosen) # pokemon battle pressure plate with random Pokémon
                            objects.append((plate, Coord(i, j)))
                    else: # random.random() >= plate_probability
                        bush = ExtDecor("bushh") # regular bush
                        bush._MapObject__passable = True
                        objects.append((bush, Coord(i, j)))
    
    def _get_keybinds(self) -> dict[str, Callable[["HumanPlayer"], list[Message]]]:
        #cannot get this work in a seperate file 
        keybinds = super()._get_keybinds()

        def view_active_pokemon(player: HumanPlayer) -> list[Message]:
            active_pokemon = player.get_state("active_pokemon", None)
            if not active_pokemon:
                return [ServerMessage(player, "No active Pokémon found.")]

            name = active_pokemon.name
            level = active_pokemon.level
            current_hp = active_pokemon.current_health
            max_hp = active_pokemon.max_health
            p_type = active_pokemon.p_type.name
            xp = active_pokemon.xp
            evo_level = active_pokemon.evolution_state.get_evo_level()
            attacks = active_pokemon.known_attacks

            stats_lines = [
                f"Name: {name}",
                f"Type: {p_type}",
                f"Evolution Level: {evo_level}",
                f"Level: {level}",
                f"XP: {xp}",
                f"HP: {current_hp}/{max_hp}",
                "Attacks:"
            ]
            for i, attack in enumerate(attacks):
                stats_lines.append(f" {i + 1}. {attack['name']} ({attack['damage']})")

            return [
                DisplayStatsMessage(
                    sender=self,
                    recipient=player,
                    stats=stats_lines,
                    top_image_path=f"image/Pokemon/{name}_front.png",
                    bottom_image_path=f"image/Pokemon/{name}_back.png",
                    scale=1.5,
                    window_title="Pokémon Stats"
                )
            ]

        keybinds["v"] = view_active_pokemon
        return keybinds

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []
        
        # Add a door to exit back to Trottier Town
        door = Door('tube', linked_room="Trottier Town")
        objects.append((door, Coord(26, 27)))
        
        pokemon_battle_plate = PokemonBattlePressurePlate("Bulbasaur")
        objects.append((pokemon_battle_plate, Coord(19, 26)))
        
        # heal_pokemon_plate = HealActivePokemonPlate()
        # objects.append((heal_pokemon_plate, Coord(19, 25)))
        
        # choose_pokemon_plate = ChoosePokemonPlate()
        # objects.append((choose_pokemon_plate, Coord(19, 24)))
        
        choose_difficulty_plate = ChooseDifficultyPlate()
        objects.append((choose_difficulty_plate, Coord(19, 27)))
        
        # display_active_pokemon_plate = DisplayActivePokemonPlate()
        # objects.append((display_active_pokemon_plate, Coord(19, 22)))
        
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
        for tree_row in [21, 22]:
            self._add_trees(objects, (tree_row, 4), (tree_row, 26),step=2)

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

        sign = Sign(text="You can view the stats of your active Pokemon by clicking on v! ")
        objects.append((sign, Coord(26, 2)))

        prof = ProfessorOak(
            facing_direction="down",
            staring_distance=3,
        )
        objects.append((prof, Coord(25, 24)))

        #choose_pokemon_plate = ChoosePokemonPlate()
        #objects.append((choose_pokemon_plate, Coord(26, 20)))

        self._add_trees(objects, (16, 2), (16, 16),step=1, tree_type="tree_s")
        self._add_bushes_with_plates(objects, (18, 4), (20, 7), evolution_stage=1, plate_probability=0.5)
        
        #path after the first bush 
        self._add_tile_line(objects, 'g_up', start=(18, 8), end=(18, 15))
        self._add_tile_line(objects, 'g_down', start=(19, 8), end=(19, 15))
        self.place(objects, 'g_top_left', (18, 8))
        self.place(objects, 'g_bottom_left', (19, 8))
        self.place(objects, 'g_top_left', (18, 8))
        self.place(objects, 'g_bottom_right', (19, 15))
        self.place(objects, 'g_top_right', (18, 15))


        building = PokemonCenter(linked_room_str="Pokemon Center")
        objects.append((building, Coord(10, 22)))
        sign = Sign(text="Welcome to the Pokemon Center")
        objects.append((sign, Coord(15, 21)))
        self._add_bushes_with_plates(objects, (7, 22), (9, 27), evolution_stage=1, plate_probability=0.4)
        self._add_bushes_with_plates(objects, (3, 22), (6, 27), evolution_stage=2, plate_probability=0.7)
        objects.append((MapObject.get_obj('flower_small_red'), Coord(3, 21)))
        objects.append((MapObject.get_obj('flower_small_red'), Coord(4, 21)))
        objects.append((MapObject.get_obj('flower_small_red'), Coord(8, 21)))
        objects.append((MapObject.get_obj('flower_small_red'), Coord(9, 21)))
        self._add_trees(objects, (5, 15), (16, 15),step = 1, tree_type = "tree_s", direction="vertical")
        self._add_trees(objects, (5, 14), (16, 14),step = 1, tree_type = "tree_s", direction="vertical")
        self._add_trees(objects, (5, 13), (16, 13),step = 1, tree_type = "tree_s", direction="vertical")
        self._add_trees(objects, (5, 12), (16, 12),step = 1, tree_type = "tree_s", direction="vertical")
        self._add_trees(objects, (3, 7), (13, 7),step = 1, tree_type = "tree_s", direction="vertical")
        self._add_trees(objects, (7, 6), (13, 6),step = 1, tree_type = "tree_s", direction="vertical")
       
        
        #path from pokemon center
        self.place(objects, 'top_left', (16, 24))
        self.place(objects, 'top_right', (16, 25))
        self.place(objects, 'poke_sand', (17, 24))
        self.place(objects, 'sand_right', (17, 25))
        self.place(objects, 'bottom_right', (18, 25))
        self._add_tile_line(objects, 'poke_sand_up', start=(17, 23), end=(17, 18))
        self._add_tile_line(objects, 'poke_sand_down', start=(18, 24), end=(18, 18))
        self.place(objects, 'bottom_left', (18, 17))
        self._add_tile_line(objects, 'sand_left', start=(17, 17), end=(7, 17))
        self._add_tile_line(objects, 'sand_right', start=(17, 18), end=(7, 18))
        self.place(objects, 'poke_sand', (17, 18))
        self.place(objects, 'top_left', (6, 17))
        self.place(objects, 'top_right', (6, 18))
        
        
        
        sign = Sign(text="Dangerous Pokemon's ahead, continue at your own risk. ")
        objects.append((sign, Coord(5, 16)))
        self.place(objects, 'g_top_right', (3, 15))
        self.place(objects, 'g_bottom_right', (4, 15))
        self._add_tile_line(objects, 'g_up', start=(3, 14), end=(3, 10))
        self._add_tile_line(objects, 'g_down', start=(4, 14), end=(4, 10))
        self.place(objects, 'g_top_left', (3, 9))
        self._add_tile_line(objects, 'g_l', start=(4, 9), end=(13, 9))
        self._add_tile_line(objects, 'g_r', start=(5, 10), end=(14, 10))
        self.place(objects, 'g', (4, 10))
        self.place(objects, 'g_bottom_right', (15, 10))
        self._add_tile_line(objects, 'g_up', start=(14, 8), end=(14, 4))
        self._add_tile_line(objects, 'g_down', start=(15, 9), end=(15, 4))
        self.place(objects, 'g', (14, 9))
        self.place(objects, 'g_bottom_left', (15, 3))
        self._add_tile_line(objects, 'g_l', start=(14, 3), end=(8, 3))
        self._add_tile_line(objects, 'g_r', start=(13, 4), end=(8, 4))
        self.place(objects, 'g', (14, 4))
        self.place(objects, 'g_top_left', (8, 3))
        self.place(objects, 'g_top_right', (8, 4))
        self._add_trees(objects, (6, 2), (6, 5),step = 1, tree_type = "tree_s")

       
        #self._add_bushes_with_plates(objects, (8, 2), (13, 5), evolution_stage=2, plate_probability=0.6)
        #self._add_bushes_with_plates(objects, (3, 12), (4,15), evolution_stage=1, plate_probability=0.6)
        #self._add_bushes_with_plates(objects, (13, 8), (15,11), evolution_stage=1, plate_probability=0.6)
        self._add_bushes_with_plates(objects, (3, 2), (5, 4), evolution_stage=3, plate_probability=0.5)
        objects.append((MapObject.get_obj('rock_1'), Coord(3, 5)))
        objects.append((MapObject.get_obj('rock_1'), Coord(5, 5)))
        
        
               
       
        

        
        


        return objects

