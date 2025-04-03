from .imports import *
from collections.abc import Callable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
   
from .custom_NPCs import Nurse


class PokeCounter(Counter):
    def __init__(self, npc: "NPC") -> None:
        super().__init__("f", npc)


class PokemonCenter(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Pokemon Center",
            description="Welcome to the Pokémon Center",
            size=(15, 15),
            entry_point=Coord(13, 7),
            background_tile_image='poke_center_tile',
        )
    def _get_keybinds(self) -> dict[str, Callable[["HumanPlayer"], list[Message]]]:
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

        # add a door
        door = Door('mat', linked_room="Pokemon House")
        objects.append((door, Coord(14, 7)))
        objects.append((MapObject.get_obj('wall'), Coord(0, 0)))
        objects.append((MapObject.get_obj('wall'), Coord(0, 1)))
        objects.append((MapObject.get_obj('wall'), Coord(0, 2)))
        objects.append((MapObject.get_obj('wall'), Coord(0, 3)))
        objects.append((MapObject.get_obj('wall'), Coord(0, 11)))
        objects.append((MapObject.get_obj('wall'), Coord(0, 12)))
        objects.append((MapObject.get_obj('wall'), Coord(0, 13)))
        objects.append((MapObject.get_obj('wall'), Coord(0, 14)))
        #objects.append((MapObject.get_obj('l'), Coord(0, 4)))


        nurse = Nurse(
            encounter_text="Hello, I am Nurse Joy, Allow me to heal your active Pokémon!",
            staring_distance=1,
        )
        objects.append((nurse, Coord(1, 7)))
        main_counter = PokeCounter(nurse)
        objects.append((main_counter, Coord(0, 4)))
        objects.append((MapObject.get_obj('c_l'), Coord(6, 0)))
        objects.append((MapObject.get_obj('sofa_table'), Coord(5, 11)))
        objects.append((MapObject.get_obj('sofa_table'), Coord(10, 11)))
        objects.append((MapObject.get_obj('sofa_table_2'), Coord(11, 0)))
        objects.append((MapObject.get_obj('bookshelf'), Coord(1, 0)))
        objects.append(((MapObject('poke_floor', passable=True)), Coord(7,6)))
        objects.append(((MapObject('shadow', passable=True)), Coord(4,4)))
        
        
        
       
        
        

        return objects

