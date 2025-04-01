from .imports import *
from collections.abc import Callable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
   

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

class Nurse(NPC):
    def __init__(self, encounter_text: str, staring_distance: int = 3) -> None:
        super().__init__(
            name="Nurse Joy",
            image='joy3',
            encounter_text=encounter_text,
            facing_direction='down',
            staring_distance=staring_distance
        )
    def player_interacted(self, player: HumanPlayer) -> list[Message]:
        messages: list[Message] = []

        # Initial dialogue
        messages.append(DialogueMessage(self, player, self._NPC__encounter_text, self.get_image_name()))

        # Get active Pokémon
        active_pokemon = player.get_state("active_pokemon", None)
        if active_pokemon is None:
            messages.append(DialogueMessage(self, player, "You don’t have a Pokémon to heal.", ""))
            return messages

        if active_pokemon.current_health == active_pokemon.max_health:
            messages.append(DialogueMessage(self, player, "Your Pokémon is already at full health.", ""))
            return messages

        # Heal the Pokémon
        active_pokemon.current_health = active_pokemon.max_health
        player.set_state("active_pokemon", active_pokemon)
        messages.append(DialogueMessage(self, player, f"{active_pokemon.name} was fully healed!", ""))

        return messages



class PokemonCenter(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Pokemon Center",
            description="Welcome to the Pokemon Center",
            size=(15, 15),
            entry_point=Coord(13, 7),
            background_tile_image='wood_brown',
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
        door = Door('int_entrance', linked_room="Pokemon House")
        objects.append((door, Coord(14, 7)))

        objects.append((HealActivePokemonPlate(), Coord(3, 8)))

        objects.append((MapObject.get_obj('counter_l'), Coord(0, 1)))
        objects.append((MapObject.get_obj('counter_r'), Coord(0, 7)))

        objects.append((MapObject.get_obj('counter_u'), Coord(4, 0)))
        objects.append((MapObject.get_obj('counter_d'), Coord(8, 0)))
        objects.append((MapObject.get_obj('sofa'), Coord(5, 11)))
        objects.append((MapObject.get_obj('table'), Coord(6, 12)))
        objects.append((MapObject.get_obj('sofa'), Coord(7, 11)))

        objects.append((MapObject.get_obj('sofa'), Coord(9, 11)))
        objects.append((MapObject.get_obj('table'), Coord(10, 12)))
        objects.append((MapObject.get_obj('sofa'), Coord(11, 11)))
        
        nurse = Nurse(
            encounter_text="Hello I am Nurse Joy, Please allow me to heal your active pokemon!",
            staring_distance=3,
        )
        nurse1 = Nurse(
            encounter_text="Did you know that water type has a type advantage of fire type?",
            staring_distance=3,
        )
        nurse2 = Nurse(
            encounter_text="Always make sure to carry potions in order to take care of your pokemon during battles!",
            staring_distance=3,
        )
        objects.append((nurse, Coord(2, 5)))
        objects.append((nurse1, Coord(7, 3)))
        objects.append((nurse2, Coord(10, 3)))
        

        #need to fix nurse facing
        
        


        return objects

