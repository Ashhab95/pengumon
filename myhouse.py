from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *

# Our imports   
import time
from .pokemon import *
from .items import PotionFlyweightFactory 
from .pokeball import *
from .bag import Bag
from .enemyAI import *
from enum import Enum, auto

# Global constants
PLAYER_CHANCE_TO_DODGE = 0.5
OPPONENT_CHANCE_TO_DODGE = 0.5
ENEMY_RESPONSE_TIME = 3
PLAYER_CHANCE_TO_RUN = 0.7

class TurnStage(Enum):
    IDLE = auto()
    INTRO = auto()
    PLAYER_TURN = auto()
    AWAIT_INPUT = auto()
    ENEMY_WAIT = auto()
    ENEMY_TURN = auto()
    END = auto()
    CLEANUP = auto()
     
     
# Map objects we added ourselves
# --------------------------------
class ChoosePokemonPlate(PressurePlate):
    def __init__(self):
        super().__init__(image_name="blue_circle", stepping_text='Choose your starter Pokémon!')

    def player_entered(self, player) -> list[Message]:
        # Check if the player already chose a starter
        starter_pokemon = player.get_state("starter_pokemon", None)
        
        if starter_pokemon is None:
            
            # Initialize and add some items to the player's bag
            bag = Bag()
            bag.add_item(PotionFlyweightFactory.get_small_potion())
            bag.add_item(PotionFlyweightFactory.get_medium_potion())
            bag.add_item(RegularPokeball())
            bag.add_item(GreatBall())
            bag.add_item(MasterBall())
            player.set_state("bag", bag)
            
            return [
                DialogueMessage(self, player, self._PressurePlate__stepping_text, ""),
                ChoosePokemonMessage(self, player, ["Charmander", "Squirtle", "Bulbasaur"])
            ]
        else:
            return [DialogueMessage(self, player, f"You've already chosen {starter_pokemon} as your starter Pokémon.", "")]

    def set_starter(self, player, starter_pokemon: str) -> None:
        # Create the actual Pokemon object
        pokemon = PokemonFactory.create_pokemon(starter_pokemon)

        player.set_state("starter_pokemon", pokemon.name)
        player.set_state("active_pokemon", pokemon)  
        player.set_state("pokeballs", [])  
        
        
class ChooseDifficultyPlate(PressurePlate):
    def __init__(self):
        super().__init__(image_name="hal9000", stepping_text="Choose your battle difficulty!")
        self.__player = None
        self.__current_difficulty = "None"
        self.__pending_messages: list[Message] = []

    def player_entered(self, player) -> list[Message]:
        self.__player = player
        current_ai = player.get_state("enemy_ai", None)
        self.__current_difficulty = type(current_ai).__name__.replace("AI", "") if current_ai else "None"

        return [
            DialogueMessage(self, player, f"Current difficulty: {self.__current_difficulty}\nChoose a new difficulty.", ""),
            OptionsMessage(self, player, ["Easy", "Medium", "Hard"])
        ]

    def select_option(self, player, selected_option: str) -> list[Message]:
        difficulty_map = {
            "Easy": EasyAI,
            "Medium": MediumAI,
            "Hard": HardAI,
        }

        ai_class = difficulty_map.get(selected_option)
        player.set_state("enemy_ai", ai_class()) # update player state
        self.__current_difficulty = selected_option

        # Queue messages to be sent in next update
        self.__pending_messages.append(DialogueMessage(self, player, f"Difficulty set to {selected_option}.", ""))
        self.__pending_messages.append(OptionsMessage(self, player, [], destroy=True))

        return [] # handled in update

    def update(self) -> list[Message]:
        if len(self.__pending_messages) > 0:
            messages = self.__pending_messages
            self.__pending_messages = [] # clear pending messages so next update doesn't send them again
            return messages
        
        return []


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


class FightPressurePlate(PressurePlate):
    def __init__(self, wild_pokemon_name: str):
        super().__init__(image_name="bush", stepping_text=f"You encountered a wild {wild_pokemon_name}!")
        self.__wild_pokemon_name = wild_pokemon_name
        self.__current_option = None
        self.__player = None
        self.__player_pokemon = None
        self.__enemy_pokemon = None
        self.__player_used_dodge = False
        self.__enemy_used_dodge = False
        self.__turn_stage = TurnStage.IDLE
        self.__last_action_time = time.time()

    def select_option(self, player, selected_option: str) -> None:
        self.__current_option = selected_option

    def clear_option(self) -> None:
        self.__current_option = None

    def player_entered(self, player) -> list[Message]:
        self.__player = player
        self.__player_pokemon = player.get_state("active_pokemon", None)
        self.__enemy_pokemon = PokemonFactory.create_pokemon(self.__wild_pokemon_name)
        self.__player_used_dodge = False
        self.__enemy_used_dodge = False
        self.__turn_stage = TurnStage.INTRO
        self.__last_action_time = time.time()
        return []

    def update(self) -> list[Message]:
        now = time.time()
        messages = []

        if self.__turn_stage == TurnStage.INTRO:
            messages.extend([
                ServerMessage(self.__player, f"You encountered a wild {self.__enemy_pokemon.name}!"),
                FightMessage(self.__player, self.__player,
                             self.__player_pokemon.name, self.__player_pokemon.current_health, self.__player_pokemon.max_health,
                             self.__enemy_pokemon.name, self.__enemy_pokemon.current_health, self.__enemy_pokemon.max_health),
            ])
            self.__turn_stage = TurnStage.PLAYER_TURN
            self.__last_action_time = now

        elif self.__turn_stage == TurnStage.PLAYER_TURN:
            self.clear_option()
            attack_options = []
            for i, attack in enumerate(self.__player_pokemon.known_attacks):
                option = f"{i}: {attack['name']} ({attack['damage']})"
                attack_options.append(option)
            full_options = attack_options + ["Dodge", "Run"]
            messages.append(OptionsMessage(self, self.__player, full_options))
            self.__turn_stage = TurnStage.AWAIT_INPUT
            self.__last_action_time = now

        elif self.__turn_stage == TurnStage.AWAIT_INPUT:
            if self.__current_option is not None:
                selected = self.__current_option
                self.clear_option()

                if selected == "Dodge":
                    self.__player_used_dodge = True
                    messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__player_pokemon.name} prepares to dodge!"))
                    self.__turn_stage = TurnStage.ENEMY_WAIT
                    self.__last_action_time = now

                elif selected == "Run":
                    if random.random() < PLAYER_CHANCE_TO_RUN:
                        messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) You ran away safely!"))
                        self.__turn_stage = TurnStage.END
                    else:
                        messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) You tried to run but couldn't escape!"))
                        self.__turn_stage = TurnStage.ENEMY_WAIT
                        self.__last_action_time = now

                elif ":" in selected and selected.split(":" )[0].isdigit():
                    attack_index = int(selected.split(":" )[0])
                    if 0 <= attack_index < len(self.__player_pokemon.known_attacks):
                        if self.__enemy_used_dodge and random.random() < OPPONENT_CHANCE_TO_DODGE:
                            messages.append(ServerMessage(self.__player,
                                f"(Opp) {self.__enemy_pokemon.name} dodged {self.__player_pokemon.known_attacks[attack_index]['name']}!"))
                        else:
                            if self.__enemy_used_dodge:
                                messages.append(ServerMessage(self.__player, f"(Opp) Dodge failed!"))
                            result = self.__player_pokemon.attack(attack_index, self.__enemy_pokemon)
                            messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {result['message']} It dealt {result['damage']} damage."))
                            messages.append(FightMessage(self.__player, self.__player,
                                                        self.__player_pokemon.name, self.__player_pokemon.current_health, self.__player_pokemon.max_health,
                                                        self.__enemy_pokemon.name, self.__enemy_pokemon.current_health, self.__enemy_pokemon.max_health))
                            if result.get("evolved"):
                                self.__player.set_state("active_pokemon", result["evolved"])
                                self.__player_pokemon = result["evolved"]
                                messages.append(ServerMessage(self.__player, f"Your Pokémon evolved into {self.__player_pokemon.name}!"))
                                
                            self.__enemy_used_dodge = False

                    if self.__player_pokemon.is_fainted():
                        messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__player_pokemon.name} has fainted! You lost."))
                        self.__turn_stage = TurnStage.END
                    elif self.__enemy_pokemon.is_fainted():
                        messages.append(ServerMessage(self.__player, f"(Opp) {self.__enemy_pokemon.name} has fainted! You won!"))
                        self.__turn_stage = TurnStage.END
                    else:
                        self.__turn_stage = TurnStage.ENEMY_WAIT
                        self.__last_action_time = now
                else:
                    messages.append(ServerMessage(self.__player, "Unrecognized action."))
                    self.__turn_stage = TurnStage.PLAYER_TURN

        elif self.__turn_stage == TurnStage.ENEMY_WAIT:
            if now - self.__last_action_time >= ENEMY_RESPONSE_TIME:
                self.__turn_stage = TurnStage.ENEMY_TURN

        elif self.__turn_stage == TurnStage.ENEMY_TURN:
            ai: EnemyAI = self.__player.get_state("enemy_ai", MediumAI())
            action = ai.choose_action(self.__enemy_pokemon, self.__player_pokemon)

            if action == "Dodge":
                messages.append(ServerMessage(self.__player, f"(Opp) {self.__enemy_pokemon.name} is preparing to dodge!"))
                self.__enemy_used_dodge = True
            else:
                attack_index = int(action)
                attack = self.__enemy_pokemon.known_attacks[attack_index]
                
                if self.__player_used_dodge and random.random() < PLAYER_CHANCE_TO_DODGE:
                    messages.append(ServerMessage(self.__player,
                        f"({self.__player.get_name()}) {self.__player_pokemon.name} dodged {attack['name']} attack!"))
                else:
                    result = self.__enemy_pokemon.attack(attack_index, self.__player_pokemon)
                    messages.append(ServerMessage(self.__player, f"(Opp) {result['message']} It dealt {result['damage']} damage."))
                    messages.append(FightMessage(self.__player, self.__player,
                                                 self.__player_pokemon.name, self.__player_pokemon.current_health, self.__player_pokemon.max_health,
                                                 self.__enemy_pokemon.name, self.__enemy_pokemon.current_health, self.__enemy_pokemon.max_health))
            self.__player_used_dodge = False

            if self.__player_pokemon.is_fainted():
                messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__player_pokemon.name} has fainted! You lost."))
                self.__turn_stage = TurnStage.END
            elif self.__enemy_pokemon.is_fainted():
                messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__enemy_pokemon.name} has fainted! You won."))
                self.__turn_stage = TurnStage.END
            else:
                self.__turn_stage = TurnStage.PLAYER_TURN
                self.__last_action_time = now

        elif self.__turn_stage == TurnStage.END:
            messages.append(ServerMessage(self.__player, "The battle has ended!"))
            messages.append(OptionsMessage(self, self.__player, [], destroy=True))
            messages.append(FightMessage(self, self.__player, "", "", 0, 0, 0, 0, destroy=True))

            self.__player.set_state("active_pokemon", self.__player_pokemon)
            self.__turn_stage = TurnStage.CLEANUP

        elif self.__turn_stage == TurnStage.CLEANUP:
            return []

        return messages
                
# --------------------------------



class PokemonHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Pokemon House",
            description="Welcome to the Kanto region!",
            size=(30, 30),
            entry_point=Coord(26, 26),
            background_tile_image='grass',
        )
    
    def _add_trees(self, objects, start_pos, end_pos, step=2, tree_type="tree_large_1", direction="horizontal"):
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
                    tree = ExtDecor(tree_type)
                    objects.append((tree, Coord(i_start, j)))
        else:  # vertical
            for i in range(i_start, i_end, step):
                if 0 <= i < self._map_rows-1 and 0 <= j_start < self._map_cols-1:
                    tree = ExtDecor(tree_type)
                    objects.append((tree, Coord(i, j_start)))
    
    def _add_backgrounds(self, objects, start_pos, end_pos, step=1, bg_type="sand", direction="area"):
        i_start, j_start = start_pos
        i_end, j_end = end_pos
        
        if direction == "horizontal":
            for j in range(j_start, j_end, step):
                if 0 <= i_start < self._map_rows-1 and 0 <= j < self._map_cols-1:
                    bg = Background(bg_type)
                    objects.append((bg, Coord(i_start, j)))
        elif direction == "vertical":
            for i in range(i_start, i_end, step):
                if 0 <= i < self._map_rows-1 and 0 <= j_start < self._map_cols-1:
                    bg = Background(bg_type)
                    objects.append((bg, Coord(i, j_start)))
        else:  # "area" - fill a rectangular area
            for i in range(i_start, i_end, step):
                for j in range(j_start, j_end, step):
                    if 0 <= i < self._map_rows-1 and 0 <= j < self._map_cols-1:
                        bg = Background(bg_type)
                        objects.append((bg, Coord(i, j)))
    def _add_area(self, objects, start_pos, end_pos, obj_type_func, passable=False):

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
    
    def _add_bushes_with_plates(self, objects, start_pos, end_pos, evolution_stage=1, plate_probability=0.8):
        """Add an area of bushes with random FightPressurePlates beneath.
        
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
                            plate = FightPressurePlate(chosen) # fight ressure plate with random Pokémon
                            objects.append((plate, Coord(i, j)))
                    else: # random.random() >= plate_probability
                        bush = ExtDecor("bush") # regular bush
                        bush._MapObject__passable = True
                        objects.append((bush, Coord(i, j)))
    
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []
        
        # Add a door to exit back to Trottier Town
        door = Door('tube', linked_room="Trottier Town")
        objects.append((door, Coord(26, 27)))
        
        
        fight_pressure_plate = FightPressurePlate("Bulbasaur")
        objects.append((fight_pressure_plate, Coord(26, 22)))
        
        heal_pokemon_plate = HealActivePokemonPlate()
        objects.append((heal_pokemon_plate, Coord(25, 22)))
        
        choose_pokemon_plate = ChoosePokemonPlate()
        objects.append((choose_pokemon_plate, Coord(24, 22)))
        
        
        choose_difficulty_plate = ChooseDifficultyPlate()
        objects.append((choose_difficulty_plate, Coord(23, 22)))
        
        # Create a border of trees
        # Bottom row
        self._add_trees(objects, (self._map_rows - 3, 2), (self._map_rows - 3, self._map_cols - 1))
        
        # Left column
        self._add_trees(objects, (1, 0), (self._map_rows - 1, 0), direction="vertical")
        
        # Right column
        self._add_trees(objects, (1, 28), (self._map_rows - 1, 28), direction="vertical")
        
        # Top row
        self._add_trees(objects, (0, 2), (0, self._map_cols - 2))
        
        
        # This code only clutters the map and will be removed for the duration of testing
        

        # Add a sandy path
        #self._add_backgrounds(objects, (20, 10), (20, 20), step=1, bg_type="sand", direction="vertical")

        # Add a water area 
        #self._add_backgrounds(objects, (5, 5), (10, 10), step=1, bg_type="water", direction="area")
        
        # Add tree rows above paths
        #for tree_row in [21, 22, 23]:
         #   self._add_trees(objects, (tree_row, 3), (tree_row, 26))
        
        prof = Professor(
            encounter_text="Welcome to the Kanto Region, I am Professor Oak. Please step on the blue plate to choose your starter pokemon.",
            facing_direction='down',
            staring_distance=3,
        )
        objects.append((prof, Coord(25, 24)))

        # Adding bushes and pressure plates 
        self._add_bushes_with_plates(objects, (24, 16), (26, 19), evolution_stage=1, plate_probability=0.5)
        self._add_bushes_with_plates(objects, (20, 16), (22, 19), evolution_stage=2, plate_probability=0.5)
        self._add_bushes_with_plates(objects, (16, 16), (18, 19), evolution_stage=3, plate_probability=0.5)
        
        return objects