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
from typing import Literal
from collections.abc import Callable


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
#not needed anymore, simply interact with the prof.
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

            # Define options with display name and image path
            options = [
                {"Charmander": "image/Pokemon/Charmander_front.png"},
                {"Squirtle": "image/Pokemon/Squirtle_front.png"},
                {"Bulbasaur": "image/Pokemon/Bulbasaur_front.png"}
            ]

            return [
                DialogueMessage(self, player, self._PressurePlate__stepping_text, ""),
                ChooseObjectMessage(self, player, options, window_title="Choose your starter Pokémon!")
            ]
        else:
            return [DialogueMessage(self, player, f"Welcome back to the Kanto region! How is your {starter_pokemon} doing?", "")]

    def set_choice(self, player, choice: str) -> None:
        # Create the actual Pokemon object
        pokemon = PokemonFactory.create_pokemon(choice)

        player.set_state("starter_pokemon", pokemon.name)
        player.set_state("active_pokemon", pokemon)  
        player.set_state("pokeballs", [])  

#not needed anymore, now use keybind v     
class DisplayActivePokemonPlate(PressurePlate):
    def __init__(self):
        super().__init__(image_name="red_down_arrow")

    def player_entered(self, player) -> list[Message]:
        active_pokemon = player.get_state("active_pokemon", None)

        if not active_pokemon:
            return [DialogueMessage(self, player, "No active Pokémon found.", "")]

        # Extract relevant stats
        name = active_pokemon.name
        level = active_pokemon.level
        current_hp = active_pokemon.current_health
        max_hp = active_pokemon.max_health
        p_type = active_pokemon.p_type.name
        xp = active_pokemon.xp
        evo_level = active_pokemon.evolution_state.get_evo_level()
        attacks = active_pokemon.known_attacks

        # Format stats as strings
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
            attack_name = attack.get("name", "")
            damage = attack.get("damage", 0)
            stats_lines.append(f" {i + 1}. {attack_name} ({damage})")

        # Image paths (relative to resource folder)
        top_image_path = f"image/Pokemon/{name}_front.png"
        bottom_image_path = f"image/Pokemon/{name}_back.png"

        return [
            DisplayStatsMessage(
                sender=self,
                recipient=player,
                stats=stats_lines,
                top_image_path=top_image_path,
                bottom_image_path=bottom_image_path,
                scale=1.5,
                window_title="Pokémon Stats"
            )
        ]
               
class ChooseDifficultyPlate(PressurePlate):
    def __init__(self):
        super().__init__(image_name="hal9000", stepping_text="Choose your battle difficulty!")
        self.__pending_messages: dict[HumanPlayer, list[Message]] = {}

    def player_entered(self, player) -> list[Message]:
        current_ai = player.get_state("enemy_ai", None)
        current_difficulty = type(current_ai).__name__.replace("AI", "") if current_ai else "None"

        return [
            DialogueMessage(self, player, f"Current difficulty: {current_difficulty}\nChoose a new difficulty.", ""),
            OptionsMessage(self, player, ["Easy", "Medium", "Hard"])
        ]

    def select_option(self, player, selected_option: str) -> list[Message]:
        difficulty_map = {
            "Easy": EasyAI,
            "Medium": MediumAI,
            "Hard": HardAI,
        }

        ai_class = difficulty_map.get(selected_option)
        if ai_class:
            player.set_state("enemy_ai", ai_class())
            self.__pending_messages[player] = [
                # DialogueMessage(self, player, f"Difficulty set to {selected_option}.", ""),
                OptionsMessage(self, player, [], destroy=True)
            ]

        return []  # Responses are handled in update()

    def update(self) -> list[Message]:
        messages = []
        for player, pending in list(self.__pending_messages.items()):
            messages.extend(pending)
            del self.__pending_messages[player]
        return messages

#not needed anymore, simply interact with the nurse
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

class PokemonBattlePressurePlate(PressurePlate):
    def __init__(self, wild_pokemon_name: str):
        super().__init__(image_name="bushh", stepping_text=f"You encountered a wild {wild_pokemon_name}!")
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

        def battle_data():
            return PokemonBattleMessage(
                self.__player,
                self.__player,
                player_data={
                    "name": self.__player_pokemon.name if self.__player_pokemon else "Unknown",
                    "level": self.__player_pokemon.level if self.__player_pokemon else 1,
                    "hp": self.__player_pokemon.current_health if self.__player_pokemon else 0,
                    "max_hp": self.__player_pokemon.max_health if self.__player_pokemon else 1
                },
                enemy_data={
                    "name": self.__enemy_pokemon.name if self.__enemy_pokemon else "Unknown",
                    "level": self.__enemy_pokemon.level if self.__enemy_pokemon else 1,
                    "hp": self.__enemy_pokemon.current_health if self.__enemy_pokemon else 0,
                    "max_hp": self.__enemy_pokemon.max_health if self.__enemy_pokemon else 1
                }
            )

        if self.__turn_stage == TurnStage.INTRO:
            messages.extend([
                ServerMessage(self.__player, f"You encountered a wild {self.__enemy_pokemon.name}!"),
                battle_data()
            ])
            self.__turn_stage = TurnStage.PLAYER_TURN
            self.__last_action_time = now

        elif self.__turn_stage == TurnStage.PLAYER_TURN:
            self.clear_option()
            attack_options = [
                f"{i}: {attack['name']} ({attack['damage']})"
                for i, attack in enumerate(self.__player_pokemon.known_attacks)
            ]
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

                elif selected == "Run":
                    if random.random() < PLAYER_CHANCE_TO_RUN:
                        messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) You ran away safely!"))
                        self.__turn_stage = TurnStage.END
                    else:
                        messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) You tried to run but couldn't escape!"))
                        self.__turn_stage = TurnStage.ENEMY_WAIT

                elif ":" in selected and selected.split(":")[0].isdigit():
                    attack_index = int(selected.split(":")[0])
                    if 0 <= attack_index < len(self.__player_pokemon.known_attacks):
                        if self.__enemy_used_dodge and random.random() < OPPONENT_CHANCE_TO_DODGE:
                            messages.append(ServerMessage(self.__player,
                                f"(Opp) {self.__enemy_pokemon.name} dodged {self.__player_pokemon.known_attacks[attack_index]['name']}!"))
                        else:
                            if self.__enemy_used_dodge:
                                messages.append(ServerMessage(self.__player, f"(Opp) Dodge failed!"))
                            result = self.__player_pokemon.attack(attack_index, self.__enemy_pokemon)
                            messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {result['message']} It dealt {result['damage']} damage."))
                            messages.append(battle_data())

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

                else:
                    messages.append(ServerMessage(self.__player, "Unrecognized action."))
                    self.__turn_stage = TurnStage.PLAYER_TURN

                self.__last_action_time = now

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
                    messages.append(battle_data())

            self.__player_used_dodge = False

            if self.__player_pokemon.is_fainted():
                messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__player_pokemon.name} has fainted! You lost."))
                self.__turn_stage = TurnStage.END
            elif self.__enemy_pokemon.is_fainted():
                messages.append(ServerMessage(self.__player, f"({self.__player.get_name()}) {self.__enemy_pokemon.name} has fainted! You won!"))
                self.__turn_stage = TurnStage.END
            else:
                self.__turn_stage = TurnStage.PLAYER_TURN

            self.__last_action_time = now

        elif self.__turn_stage == TurnStage.END:
            messages.append(ServerMessage(self.__player, "The battle has ended!"))
            messages.append(OptionsMessage(self, self.__player, [], destroy=True))
            messages.append(PokemonBattleMessage(self, self.__player, {}, {}, destroy=True))
            self.__player.set_state("active_pokemon", self.__player_pokemon)
            self.__turn_stage = TurnStage.CLEANUP

        elif self.__turn_stage == TurnStage.CLEANUP:
            return []

        return messages

class PokemonCenter(Building):
    def __init__(self, linked_room_str: str = "") -> None:
        super().__init__('pokemon_center', door_position=Coord(5, 3), linked_room_str=linked_room_str)

                
# --------------------------------
from typing import Literal

class ProfessorOak(NPC):
    def __init__(self, encounter_text: str = "Welcome to the Kanto Region. Choose your starter Pokémon!", staring_distance: int = 3, facing_direction: Literal['up', 'down', 'left', 'right'] = 'down') -> None:
        super().__init__(
            name="Professor Oak",
            image='prof',
            encounter_text=encounter_text,
            facing_direction=facing_direction,
            staring_distance=staring_distance
        )

    def player_interacted(self, player: HumanPlayer) -> list[Message]:
        messages: list[Message] = []

        # Has the player already chosen a starter?
        starter_pokemon = player.get_state("starter_pokemon", None)
        if starter_pokemon:
            messages.append(DialogueMessage(self, player, f"Welcome back to the Kanto region! How is your {starter_pokemon} doing?", ""))
            return messages

        # Intro message
        messages.append(DialogueMessage(self, player, self._NPC__encounter_text, self.get_image_name()))

        # Give initial items
        bag = Bag()
        bag.add_item(PotionFlyweightFactory.get_small_potion())
        bag.add_item(PotionFlyweightFactory.get_medium_potion())
        bag.add_item(RegularPokeball())
        bag.add_item(GreatBall())
        bag.add_item(MasterBall())
        player.set_state("bag", bag)

        # Starter options
        options = [
            {"Charmander": "image/Pokemon/Charmander_front.png"},
            {"Squirtle": "image/Pokemon/Squirtle_front.png"},
            {"Bulbasaur": "image/Pokemon/Bulbasaur_front.png"}
        ]

        # Show starter selection menu
        messages.append(ChooseObjectMessage(self, player, options, window_title="Choose your starter Pokémon!"))

        return messages

    def set_choice(self, player: HumanPlayer, choice: str) -> None:
        pokemon = PokemonFactory.create_pokemon(choice)

        # Save choice
        player.set_state("starter_pokemon", pokemon.name)
        player.set_state("active_pokemon", pokemon)
        player.set_state("pokeballs", [])




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
                return [DialogueMessage(self, player, "No active Pokémon found.", "")]

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
        
        heal_pokemon_plate = HealActivePokemonPlate()
        objects.append((heal_pokemon_plate, Coord(19, 25)))
        
        #choose_pokemon_plate = ChoosePokemonPlate()
        #objects.append((choose_pokemon_plate, Coord(19, 24)))
        
        choose_difficulty_plate = ChooseDifficultyPlate()
        objects.append((choose_difficulty_plate, Coord(19, 23)))
        
        display_active_pokemon_plate = DisplayActivePokemonPlate()
        objects.append((display_active_pokemon_plate, Coord(19, 22)))
        
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
        for tree_row in [21, 22, 23]:
            self._add_trees(objects, (tree_row, 3), (tree_row, 25),step=2)

        prof = ProfessorOak(
            encounter_text="Welcome to the Kanto Region, I am Professor Oak. Please step on the blue plate to choose your starter Pokemon. ",
            facing_direction="down",
            staring_distance=3,
        )
        objects.append((prof, Coord(25, 24)))

        #choose_pokemon_plate = ChoosePokemonPlate()
        #objects.append((choose_pokemon_plate, Coord(26, 20)))

        self._add_trees(objects, (16, 2), (16, 16),step=1, tree_type="tree_s")
        self._add_bushes_with_plates(objects, (18, 3), (20, 6), evolution_stage=1, plate_probability=0.5)
        self._add_trees(objects, (18, 7), (21, 7),step = 2, tree_type = "rock_1", direction="vertical")
    
        self._add_trees(objects, (18, 8), (18, 12),step = 1, tree_type = "flower_large_blue")
        self._add_trees(objects, (20, 8), (20, 12),step = 1, tree_type = "flower_large_blue")
        
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
        self._add_bushes_with_plates(objects, (8, 2), (13, 5), evolution_stage=2, plate_probability=0.6)
        self._add_bushes_with_plates(objects, (3, 12), (4,15), evolution_stage=1, plate_probability=0.6)
        self._add_bushes_with_plates(objects, (13, 8), (15,11), evolution_stage=1, plate_probability=0.6)
        sign = Sign(text="Dangerous Pokemon's ahead, continue at your own risk. ")
        objects.append((sign, Coord(5, 16)))
            

        
     

        # Adding bushes and pressure plates 

        #self._add_bushes_with_plates(objects, (20, 16), (22, 19), evolution_stage=2, plate_probability=0.5)
        self._add_bushes_with_plates(objects, (3, 2), (5, 4), evolution_stage=3, plate_probability=0.5)
        objects.append((MapObject.get_obj('rock_1'), Coord(3, 5)))
        objects.append((MapObject.get_obj('rock_1'), Coord(5, 5)))
        self._add_trees(objects, (6, 2), (6, 5),step = 1, tree_type = "tree_small_1")
        
        
        return objects
