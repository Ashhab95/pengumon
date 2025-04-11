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


def get_keybinds(map_instance) -> dict[str, Callable[["HumanPlayer"], list[Message]]]:
    """
    Registers keybinds for player interaction. Pass in the map instance using this function.
    (view stats, switch Pokémon, show bag, hints)
    """
    keybinds = {}

    def view_active_pokemon(player: HumanPlayer) -> list[Message]:
        """Display detailed stats and attacks of the active Pokémon."""
        data = player.get_state("active_pokemon", None)
        if not data:
            return [ServerMessage(player, "No active Pokémon found.")]

        active_pokemon = Pokemon.from_list(data)

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
                sender=player,  # keybind-triggered messages use player as sender
                recipient=player,
                stats=stats_lines,
                top_image_path=f"image/Pokemon/{name}_front.png",
                bottom_image_path=f"image/Pokemon/{name}_back.png",
                scale=1.5,
                window_title="Pokémon Stats"
            )
        ]

    def give_hint(player: HumanPlayer) -> list[Message]:
        """Show a random helpful hint to the player."""
        hints_pool = [
            ["Visit Professor Oak", "to get your first Pokémon and bag!"],
            ["You can dodge during battles", "to avoid taking damage!"],
            ["Use potions from your bag", "to heal your Pokémon."],
            ["Catch fainted wild Pokémon", "with a Pokéball!"],
            ["Press 's' to switch", "your active Pokémon."],
            ["Pokémon can evolve", "after gaining enough XP."],
            ["You can run from battles,", "but it's not always successful!"],
            ["Press 'v' to view stats", "of your active Pokémon!"],
            ["Fire types are strong", "against grass types."],
            ["Water types are strong", "against fire types."],
            ["Grass types are strong", "against water types."],
            ["Heal your Pokémons", "at the Pokémon Center!"],
            ["Use potions wisely", "to gain an advantage!"]
        ]

        hint_lines = random.choice(hints_pool)

        return [
            DisplayStatsMessage(
                sender=player,
                recipient=player,
                stats=hint_lines,
                top_image_path="image/tile/utility/Empty.png",
                bottom_image_path="image/tile/utility/Empty.png",
                window_title="Hint",
                scale=0.5
            )
        ]

    def switch_active_pokemon(player: HumanPlayer) -> list[Message]:
        """Let the player select a healthy Pokémon to set as the active one."""
        bag_data = player.get_state("bag", None)
        if not bag_data:
            return [ServerMessage(player, "You don't have a bag yet! Please visit Professor Oak.")]

        bag = Bag.from_dict(bag_data)
        available = bag.pokemon.get_available_pokemon()
        if not available:
            return [ServerMessage(player, "You don't have any healthy Pokémon to switch to!")]

        options_map = {}
        options = []
        for index, ball in available:
            label = f"{ball.get_name()} HP: {ball.get_health()}"
            options_map[label] = index
            options.append(label)

        options.append("Exit")

        class SwitchMenu:
            def get_name(self):
                return "SwitchMenu"

            def select_option(self, player, selected_option: str) -> list[Message]:
                if selected_option == "Exit":
                    player.set_current_menu(None)
                    return [
                        ServerMessage(player, "You chose not to switch active Pokémon."),
                        OptionsMessage(self, player, [], destroy=True)
                    ]
                index = options_map.get(selected_option)
                if index is not None:
                    active_data = player.get_state("active_pokemon", None)
                    old_active = Pokemon.from_list(active_data)
                    new_active = bag.pokemon.switch_pokemon(old_active, index)
                    if new_active:
                        player.set_state("active_pokemon", new_active.to_list())
                        player.set_state("bag", bag.to_dict())
                        player.set_current_menu(None)
                        return [
                            ServerMessage(player, f"{new_active.name} is now your active Pokémon!"),
                            OptionsMessage(self, player, [], destroy=True)
                        ]
                return []

        switch_menu = SwitchMenu()
        player.set_current_menu(switch_menu)

        return [
            ServerMessage(player, "Choose a Pokémon to set as your active Pokémon:"),
            OptionsMessage(switch_menu, player, options)
        ]
        
    def show_bag_contents(player: HumanPlayer) -> list[Message]:
        bag_data = player.get_state("bag", {})
        bag = Bag.from_dict(bag_data)

        # Get potion and pokeball counts
        potion_counts = bag.potions._get_counts()
        pokeball_counts = bag.pokeballs._get_counts()

        lines = ["Potion Compartment:"]
        for key, count in potion_counts.items():
            if count > 0:
                lines.append(f"  {key.replace('_', ' ').title()}: {count}")

        lines.append("")  # Add a blank line between sections
        lines.append("Pokéball Compartment:")
        for key, count in pokeball_counts.items():
            if count > 0:
                lines.append(f"  {key.replace('_', ' ').title()}: {count}")

        return [
            DisplayStatsMessage(
                sender=player,  
                recipient=player,
                stats=lines,
                top_image_path="image/tile/utility/Empty.png",
                bottom_image_path="image/tile/utility/Empty.png",
                window_title="Bag Contents",
                scale=0.75
            )
        ]

    keybinds["b"] = show_bag_contents
    keybinds["h"] = give_hint
    keybinds["v"] = view_active_pokemon
    keybinds["s"] = switch_active_pokemon

    return keybinds