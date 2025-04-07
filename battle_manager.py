from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from message import *

from enum import Enum, auto
import time
from .pokemon import PokemonFactory
from .bag import Bag
from .enemyAI import *
from .observers import BattleMessageNotifier 

# Global constants
PLAYER_CHANCE_TO_DODGE = 0.5
OPPONENT_CHANCE_TO_DODGE = 0.5
ENEMY_RESPONSE_TIME = 3
PLAYER_CHANCE_TO_RUN = 0.7

class TurnStage(Enum):
    """Represents the various stages of a Pokémon battle turn lifecycle."""
    IDLE = auto()           # the stage the battle manager initializes in
    INTRO = auto()          # setup stage, where the battle is introduced 
    PLAYER_TURN = auto()    # present options to player (called once so option messages don't repeat)
    AWAIT_INPUT = auto()    # wait for player input and process it
    AWAIT_SWITCH = auto()   # wait for player input and process it
    AWAIT_BAG = auto() 
    ENEMY_WAIT = auto()     # time delay before enemy action
    ENEMY_TURN = auto()     # perform enemy action
    END = auto()            # end stage where we announce the battle is over and destroy the windows
    CLEANUP = auto()        # cleanup stage, pressure plate sees that battle is over and performs cleanup


class PokemonBattleManager:
    """
    Manages the full turn-based battle logic between the player and a wild Pokémon.
    Handles state transitions, player actions, enemy AI decisions, and battle messages.
    """
    def __init__(self, player, wild_pokemon_name: str):
        self.__player = player
    
        active_data = player.get_state("active_pokemon", None)
        self.__player_pokemon = Pokemon.from_list(active_data) 

        self.__enemy_pokemon = PokemonFactory.create_pokemon(wild_pokemon_name)
        self.__used_dodge = False # player and enemy share this flag (can be done since this game is turn-based)
        self.__turn_stage = TurnStage.INTRO
        self.__current_option = None
        self.__last_action_time = time.time()
        self.__switch_options_map = {}
        
        # Observer setup
        self.__battle_messages: list[Message] = []
        self.__player_pokemon.add_observer(BattleMessageNotifier(player, self.__battle_messages))
        self.__enemy_pokemon.add_observer(BattleMessageNotifier(player, self.__battle_messages))

    def set_selected_option(self, selected_option: str) -> None:
        """Called from outside (pressure plate) to set the selected option."""
        self.__current_option = selected_option

    def clear_option(self) -> None:
        """Clear the currently selected option."""
        self.__current_option = None

    def is_over(self) -> bool:
        """Battle is over when we are in the cleanup stage."""
        return self.__turn_stage == TurnStage.CLEANUP

    def get_player_pokemon(self) -> Pokemon:
        """Return the current active Pokémon of the player."""
        return self.__player_pokemon

    # Update is called every second
    def update(self) -> list[Message]:
        """
        Update the battle state based on current turn stage.
        Called repeatedly to progress the battle flow.
        """
        now = time.time()
        messages = []

        match self.__turn_stage:
            case TurnStage.INTRO:
                messages.extend(self._handle_intro())

            case TurnStage.PLAYER_TURN:
                messages.extend(self._handle_player_turn())

            case TurnStage.AWAIT_INPUT | TurnStage.AWAIT_SWITCH|TurnStage.AWAIT_BAG: # player inputs are handled in the same way
                messages.extend(self._handle_await_input())

            case TurnStage.ENEMY_WAIT:
                # When ENEMY_RESPONSE_TIME amount of time has passed, switch to enemy turn
                if now - self.__last_action_time >= ENEMY_RESPONSE_TIME:
                    self.__turn_stage = TurnStage.ENEMY_TURN

            case TurnStage.ENEMY_TURN:
                messages.extend(self._handle_enemy_turn())

            case TurnStage.END:
                messages.extend(self._handle_end())

            case TurnStage.CLEANUP:
                return [] # return empty list to avoid sending new messages (reason why END is not last stage)

        messages.extend(self.__battle_messages)  # include health change messages from observers
        self.__battle_messages.clear()  # clear buffer after flushing messages
        
        return messages

    def _pokemon_data(self, pokemon) -> dict[str, int]:
        """Pokémon data for battle message. These are the only fields needed for battle window."""
        return {
            "name": pokemon.name if pokemon else "Unknown",
            "level": pokemon.level if pokemon else 1,
            "hp": pokemon.current_health if pokemon else 0,
            "max_hp": pokemon.max_health if pokemon else 1
        }

    def _make_battle_message(self) -> PokemonBattleMessage:
        """Create a battle message with player and enemy Pokémon data."""
        return PokemonBattleMessage(
            self.__player,
            self.__player,
            player_data=self._pokemon_data(self.__player_pokemon),
            enemy_data=self._pokemon_data(self.__enemy_pokemon)
        )

    def _handle_intro(self) -> list[Message]:
        """Initialize the battle with encounter text setting up battle."""
        messages = [
            ServerMessage(self.__player, f"You encountered a wild {self.__enemy_pokemon.name}!"),
            self._make_battle_message()
        ]
        self.__turn_stage = TurnStage.PLAYER_TURN # player goes first
        self.__last_action_time = time.time() 
        return messages

    def _handle_player_turn(self) -> list[Message]:
        """This function is called once before we await for player input."""
        self.clear_option()

        # Collect available attack options
        attack_options = []
        for i, attack in enumerate(self.__player_pokemon.known_attacks):
            attack_options.append(f"{i}: {attack['name']} ({attack['damage']})")

        utility_options = ["Dodge", "Run", "Bag"]

        # Reconstruct bag from saved dict state
        bag_data = self.__player.get_state("bag")
        bag = Bag.from_dict(bag_data)

        # Add switch option if other Pokémon are available (not fainted)
        switch_option = []
        if bag.pokemon.get_available_pokemon():
            switch_option.append("Switch Pokemon")

        full_options = attack_options + utility_options + switch_option  # combine all options

        self.__last_action_time = time.time()
        self.__turn_stage = TurnStage.AWAIT_INPUT

        return [OptionsMessage(self.__player, self.__player, full_options)]  # present options to player

    def _handle_await_input(self) -> list[Message]:
        """
        Process the player’s selected option and handle all action logic 
        (attacks, potions, Pokéballs, switching Pokémon, running).
        """
        messages = []
        now = time.time()
        selected = self.__current_option
        if selected is None:
            return messages

        self.clear_option()
        name = self.__player.get_name()
        if self.__turn_stage == TurnStage.AWAIT_BAG:
            if selected == "Return":
                self.__turn_stage = TurnStage.PLAYER_TURN
                return [ServerMessage(self.__player, "Returning to main options.")]
        # Parse the selected item
            if selected.startswith("Potion:"):
                item_key = selected.split("Potion: ")[1].lower().replace(" ", "_")
                bag_data = self.__player.get_state("bag")
                bag = Bag.from_dict(bag_data)
                potion = bag.potions.remove(item_key)
                
                if potion:
                    # Use the potion
                    old_health = self.__player_pokemon.current_health
                    success = potion.use(self.__player_pokemon)
                    
                    if success:
                        # Update player state
                        # self.__player.set_state("active_pokemon", self.__player_pokemon.to_list())
                        self.__player.set_state("bag", bag.to_dict())
                        
                        messages.append(ServerMessage(
                            self.__player,
                            f"({name}) Used {potion.get_name()}! {self.__player_pokemon.name} was healed!"
                        ))
                        
                        # Update battle UI
                        messages.append(self._make_battle_message())
                        
                        # Move to enemy turn
                        self.__turn_stage = TurnStage.ENEMY_WAIT
                    else:
                        # Return the potion to the bag if not used
                        bag.potions.add(potion)
                        self.__player.set_state("bag", bag.to_dict())
                        
                        messages.append(ServerMessage(
                            self.__player, 
                            f"The potion had no effect! {self.__player_pokemon.name} is already at full health."
                        ))
                        self.__turn_stage = TurnStage.PLAYER_TURN
                else:
                    messages.append(ServerMessage(self.__player, "Item not found in bag."))
                    self.__turn_stage = TurnStage.PLAYER_TURN
                    
            elif selected.startswith("Ball:"):
                item_key = selected.split("Ball: ")[1].lower().replace(" ", "_")
                print(f"Item key: {item_key}")
                bag_data = self.__player.get_state("bag")
                bag = Bag.from_dict(bag_data)
                pokeball = bag.pokeballs.remove(item_key)
                print(pokeball.name)
                
                if pokeball:
                    messages.append(ServerMessage(
                        self.__player,
                        f"({name}) threw a {pokeball.name}!"
                    ))
                    
                    # Try to catch the Pokémon using the modified use method
                    catch_success = pokeball.use(self.__enemy_pokemon)
                    
                    if catch_success:
                        messages.append(ServerMessage(
                            self.__player,
                            f"({name}) caught {self.__enemy_pokemon.name}!"
                        ))
                        
                        # Add the pokeball with the caught Pokémon to the player's bag
                        bag.pokemon.add(pokeball)
                        self.__player.set_state("bag", bag.to_dict())
                        
                        # End the battle
                        self.__turn_stage = TurnStage.END
                    else:
                        messages.append(ServerMessage(
                            self.__player,
                            f"Oh no! The {self.__enemy_pokemon.name} broke free!"
                        ))
                        
                        # Enemy turn - we used our turn attempting to catch
                        self.__turn_stage = TurnStage.ENEMY_WAIT
                else:
                    messages.append(ServerMessage(self.__player, "Item not found in bag."))
                    self.__turn_stage = TurnStage.PLAYER_TURN
                
            return messages
        if self.__turn_stage == TurnStage.AWAIT_SWITCH:
            if selected == "Return":
                self.__turn_stage = TurnStage.PLAYER_TURN
                return [ServerMessage(self.__player, "Returning to main options.")]

            index = self.__switch_options_map.get(selected)
            if index is not None:
                bag_data = self.__player.get_state("bag")
                bag = Bag.from_dict(bag_data)
                new_active = bag.pokemon.switch_pokemon(self.__player_pokemon, index)
                if new_active:
                    self.__player.set_state("active_pokemon", new_active.to_list())  
                    self.__player.set_state("bag", bag.to_dict())
                    self.__player_pokemon = new_active
                    self.__turn_stage = TurnStage.ENEMY_WAIT
                    return [
                        ServerMessage(self.__player, f"You switched to {new_active.name}!"),
                        self._make_battle_message()
                    ]
            return [ServerMessage(self.__player, "Invalid selection. Returning to main options.")]


        # Add handler for "Bag" option selection
        if selected == "Bag":
            bag_data = self.__player.get_state("bag")
            bag = Bag.from_dict(bag_data)
            
            # Create options list for potions
            potion_options = []
            for key, count in bag.potions._get_counts().items():
                if count > 0:
                    formatted_key = key.replace("_", " ").title()
                    potion_options.append(f"Potion: {formatted_key}")
            
            # Create options list for pokeballs
            pokeball_options = []
            for key, count in bag.pokeballs._get_counts().items():
                if count > 0:
                    formatted_key = key.replace("_", " ").title()
                    pokeball_options.append(f"Ball: {formatted_key}")
            
            # Combine options
            bag_options = potion_options + pokeball_options
            
            if not bag_options:
                messages.append(ServerMessage(self.__player, "Your bag is empty!"))
                self.__turn_stage = TurnStage.PLAYER_TURN
                return messages
            
            # Add return option
            bag_options.append("Return")
            
            # Set state and return options message
            self.__turn_stage = TurnStage.AWAIT_BAG
            return [
                ServerMessage(self.__player, "Choose an item to use:"),
                OptionsMessage(self.__player, self.__player, bag_options)
            ]


        if selected == "Dodge":
            self.__used_dodge = True
            messages.append(ServerMessage(self.__player, f"({name}) {self.__player_pokemon.name} prepares to dodge!"))
            self.__turn_stage = TurnStage.ENEMY_WAIT

        elif selected == "Run":
            if random.random() < PLAYER_CHANCE_TO_RUN:
                messages.append(ServerMessage(self.__player, f"({name}) You ran away safely!"))
                self.__turn_stage = TurnStage.END
            else:
                messages.append(ServerMessage(self.__player, f"({name}) You tried to run but couldn't escape!"))
                self.__turn_stage = TurnStage.ENEMY_WAIT

        elif selected == "Switch Pokemon":
            bag_data = self.__player.get_state("bag")
            bag = Bag.from_dict(bag_data)
            available = bag.pokemon.get_available_pokemon()
            if not available:
                messages.append(ServerMessage(self.__player, "No healthy Pokémon available to switch."))
                self.__turn_stage = TurnStage.PLAYER_TURN
                return messages

            switch_options = []
            self.__switch_options_map.clear()

            for index, ball in available:
                label = f"{ball.get_name()} HP: {ball.get_health()}"
                self.__switch_options_map[label] = index
                switch_options.append(label)

            switch_options.append("Return")
            self.__turn_stage = TurnStage.AWAIT_SWITCH
            return [
                ServerMessage(self.__player, "Choose a Pokémon to switch to:"),
                OptionsMessage(self.__player, self.__player, switch_options)
            ]

        elif ":" in selected and selected.split(":")[0].isdigit():
            attack_index = int(selected.split(":")[0])
            messages.extend(self._process_player_attack(attack_index))

        else: # debugging
            messages.append(ServerMessage(self.__player, "Unrecognized action."))
            self.__turn_stage = TurnStage.PLAYER_TURN

        self.__last_action_time = now
        return messages

    def _process_player_attack(self, index):
        """Process an attack chosen by the player and apply damage and evolution logic."""
        messages = []
        player_name = self.__player.get_name()

        if 0 <= index < len(self.__player_pokemon.known_attacks):
            if self.__used_dodge and random.random() < OPPONENT_CHANCE_TO_DODGE:
                messages.append(ServerMessage(
                    self.__player,
                    f"(Opp) {self.__enemy_pokemon.name} dodged {self.__player_pokemon.known_attacks[index]['name']}!"
                ))
            else:
                if self.__used_dodge:
                    messages.append(ServerMessage(self.__player, f"(Opp) Dodge failed!"))

                result = self.__player_pokemon.attack(index, self.__enemy_pokemon)
                messages.append(ServerMessage(
                    self.__player,
                    f"({player_name}) {result['message']}"
                ))

                # Trigger stat update
                messages.append(self._make_battle_message())

                if result.get("evolved"):
                    self.__player.set_state("active_pokemon", result["evolved"].to_list())
                    self.__player_pokemon = result["evolved"]
                    messages.append(ServerMessage(
                        self.__player,
                        f"Your Pokémon evolved into {self.__player_pokemon.name}!"
                    ))

        self.__used_dodge = False

        # Flush observer messages before fainting logic
        print("Battle buffer before flush in player attack:", self.__battle_messages)
        messages.extend(self.__battle_messages)
        self.__battle_messages.clear()

        # Now handle fainting message after damage was shown
        if self.__enemy_pokemon.is_fainted():
            messages.append(ServerMessage(
                self.__player,
                f"(Opp) {self.__enemy_pokemon.name} has fainted! You won!"
            ))
            self.__turn_stage = TurnStage.END
        else:
            self.__turn_stage = TurnStage.ENEMY_WAIT

        return messages

    def _handle_enemy_turn(self):
        """Let the enemy Pokémon take its turn using AI to choose actions."""
        messages = []
        ai_level = self.__player.get_state("enemy_ai", "medium")  # stored as a string
        if ai_level == "easy":
            ai = EasyAI()
        elif ai_level == "hard":
            ai = HardAI()
        else:
            ai = MediumAI()

        action = ai.choose_action(self.__enemy_pokemon, self.__player_pokemon)

        if action == "Dodge":
            messages.append(ServerMessage(self.__player, f"(Opp) {self.__enemy_pokemon.name} is preparing to dodge!"))
            self.__used_dodge = True
        else:
            attack_index = int(action)
            attack = self.__enemy_pokemon.known_attacks[attack_index]

            if self.__used_dodge and random.random() < PLAYER_CHANCE_TO_DODGE:
                messages.append(ServerMessage(
                    self.__player,
                    f"({self.__player.get_name()}) {self.__player_pokemon.name} dodged {attack['name']} attack!"
                ))
            else:
                if self.__used_dodge:
                    messages.append(ServerMessage(self.__player, "(Opp) Dodge failed!"))

                if len(self.__player_pokemon._observers) == 0:
                    self.__player_pokemon.add_observer(BattleMessageNotifier(self.__player, self.__battle_messages))
                
                result = self.__enemy_pokemon.attack(attack_index, self.__player_pokemon)
                messages.append(ServerMessage(self.__player, f"(Opp) {result['message']}"))
                messages.append(self._make_battle_message())

                self.__used_dodge = False

        # Flush health change messages from observers
        print("Battle buffer before flush in enemy turn:", self.__battle_messages)
        messages.extend(self.__battle_messages)
        self.__battle_messages.clear()

        if self.__player_pokemon.is_fainted():
            messages.append(ServerMessage(
                self.__player,
                f"({self.__player.get_name()}) {self.__player_pokemon.name} has fainted! You lost."
            ))
            self.__turn_stage = TurnStage.END
        else:
            self.__turn_stage = TurnStage.PLAYER_TURN

        self.__last_action_time = time.time()
        return messages

    def _handle_end(self) -> list[Message]:
        """
        Handle the battle’s conclusion, including switching Pokémon or reviving if available.
        Finalizes and cleans up battle state.
        """
        bag_data = self.__player.get_state("bag")
        bag = Bag.from_dict(bag_data)
        available = bag.pokemon.get_available_pokemon()

        if self.__player_pokemon.is_fainted():
            # Try to revive with a revive potion
            revive_keys = ["small_revive", "medium_revive", "large_revive"]
            for key in revive_keys:
                if bag.potions._has_item(key):
                    revive_potion = bag.potions.remove(key)
                    success = revive_potion.use(self.__player_pokemon)
                    if success:
                        self.__player.set_state("active_pokemon", self.__player_pokemon.to_list())
                        self.__player.set_state("bag", bag.to_dict())
                        self.__turn_stage = TurnStage.ENEMY_WAIT
                        return [
                            ServerMessage(self.__player, f"{self.__player_pokemon.name} was revived with a {revive_potion.get_name()}!"),
                            self._make_battle_message()
                        ]
                      

        if self.__player_pokemon.is_fainted() and available:
            index, new_ball = random.choice(available)
            new_active = bag.pokemon.switch_pokemon(self.__player_pokemon, index)

            if new_active:
                self.__player.set_state("active_pokemon", new_active.to_list())
                self.__player.set_state("bag", bag.to_dict())
                self.__player_pokemon = new_active
                if len(self.__player_pokemon._observers) == 0:
                    self.__player_pokemon.add_observer(BattleMessageNotifier(self.__player, self.__battle_messages))
                self.__turn_stage = TurnStage.PLAYER_TURN

                return [
                    ServerMessage(self.__player, f"Your Pokémon fainted, but you have more! Switching to {new_active.name}..."),
                    self._make_battle_message()
                ]

        messages = [
            ServerMessage(self.__player, "The battle has ended!"),
            OptionsMessage(self.__player, self.__player, [], destroy=True),
            PokemonBattleMessage(self.__player, self.__player, {}, {}, destroy=True)
        ]
        self.__turn_stage = TurnStage.CLEANUP
        return messages

