from typing import List, Dict, Any, Optional, Tuple
from .items import Item, Potion, SmallPotion, MediumPotion, LargePotion, RevivePotion
from .pokeball import Pokeball, RegularPokeball, GreatBall, UltraBall, MasterBall
from .pokemon import Pokemon

class ItemCompartment:
    """Base class for organizing and managing item quantities in a compartment."""
    def __init__(self, name: str):
        self.name = name

    def add(self, item: Item):
        key = self.get_item_key(item)
        self._increment(key)

    def remove(self, key: str) -> Optional[Item]:
        if self._has_item(key):
            self._decrement(key)
            return self._make_item(key)
        return None

    def list_items(self) -> List[str]:
        return [f"{key.replace('_', ' ').title()} x{count}" for key, count in self._get_counts().items() if count > 0]

    def count(self) -> int:
        return sum(self._get_counts().values())

    def __str__(self) -> str:
        return f"{self.name} compartment"

    def get_item_key(self, item: Item) -> str:
        raise NotImplementedError

    def _increment(self, key: str):
        raise NotImplementedError

    def _decrement(self, key: str):
        raise NotImplementedError

    def _has_item(self, key: str) -> bool:
        raise NotImplementedError

    def _make_item(self, key: str) -> Optional[Item]:
        raise NotImplementedError

    def _get_counts(self) -> Dict[str, int]:
        raise NotImplementedError

    def to_dict(self) -> Dict[str, int]:
        return self._get_counts().copy()

    def from_dict(self, data: Dict[str, int]):
        for key in self._get_counts().keys():
            self._get_counts()[key] = data.get(key, 0)


class PotionCompartment(ItemCompartment):
    """Stores healing and revive potions and tracks their quantities."""
    def __init__(self):
        super().__init__("Potions")
        self._counts = {
            "small": 0,
            "medium": 0,
            "large": 0,
            "small_revive": 0,
            "medium_revive": 0,
            "large_revive": 0
        }

    def get_item_key(self, item: Item) -> str:
        # Handle RevivePotion first
        if isinstance(item, RevivePotion):
            base = item.potion
            if isinstance(base, SmallPotion): return "small_revive"
            elif isinstance(base, MediumPotion): return "medium_revive"
            elif isinstance(base, LargePotion): return "large_revive"
        
        # Regular health potions
        if isinstance(item, SmallPotion): return "small"
        elif isinstance(item, MediumPotion): return "medium"
        elif isinstance(item, LargePotion): return "large"
        
        raise ValueError("Unsupported potion type")


    def _increment(self, key: str): self._counts[key] += 1
    def _decrement(self, key: str): self._counts[key] -= 1
    def _has_item(self, key: str) -> bool: return self._counts.get(key, 0) > 0

    def _make_item(self, key: str) -> Optional[Potion]:
        potion_map = {
            "small": SmallPotion,
            "medium": MediumPotion,
            "large": LargePotion,
        }

        revive_map = {
            "small_revive": SmallPotion,
            "medium_revive": MediumPotion,
            "large_revive": LargePotion,
        }

        if key in potion_map:
            return potion_map[key]()
        elif key in revive_map:
            return RevivePotion(revive_map[key]())

        return None


    def _get_counts(self) -> Dict[str, int]:
        return self._counts


class PokeballCompartment(ItemCompartment):
    """Holds and manages different types of empty Pokéballs."""
    def __init__(self):
        super().__init__("Empty Pokeballs")
        self._counts = {"pokeball": 0, "greatball": 0, "ultraball": 0, "masterball": 0}

    # Idk how useful this function will be
    def get_item_key(self, item: Item) -> str:
        if isinstance(item, RegularPokeball): return "pokeball"
        elif isinstance(item, GreatBall): return "greatball"
        elif isinstance(item, UltraBall): return "ultraball"
        elif isinstance(item, MasterBall): return "masterball"
        raise ValueError("Unsupported pokeball type")

    def _increment(self, key: str) -> None: 
        self._counts[key] += 1 
        
    def _decrement(self, key: str) -> None: 
        self._counts[key] -= 1
        
    def _has_item(self, key: str) -> bool: 
        return self._counts[key] > 0

    def _make_item(self, key: str) -> Optional[Pokeball]:
        if key == "pokeball": return RegularPokeball()
        elif key == "greatball": return GreatBall()
        elif key == "ultraball": return UltraBall()
        elif key == "masterball": return MasterBall()
        return None

    def _get_counts(self) -> Dict[str, int]:
        return self._counts


class PokemonRoster:
    class PokemonRoster:
     """Handles the storage and switching of the player's captured Pokémon."""
    MAX_CAPACITY = 5 # 5 in the roster in pokeballs + user gets one active pokemon

    def __init__(self):
        self.stored_pokemon: List[Pokeball] = []

    def add(self, pokeball: Pokeball) -> bool:
        """ Add a captured Pokémon to the compartment."""
        if pokeball.is_empty():
            return False # empty Pokeball cannot be added to this compartment
        
        if self.is_full():
            return False  # at capacity
        
        self.stored_pokemon.append(pokeball)
        return True

    def is_full(self) -> bool:
        """Returns True if the compartment is full."""
        return len(self.stored_pokemon) >= self.MAX_CAPACITY

    def remove(self, index: int) -> Optional[Pokeball]:
        """Remove a Pokémon from the compartment by index."""
        if 0 <= index < len(self.stored_pokemon):
            return self.stored_pokemon.pop(index)
        return None # if index is out of range
    
    def list_pokemon(self) -> List[Tuple[int, str]]:
        """
        List all stored Pokémon in the compartment along with their attributes.

        Returns:
            A list of tuples where each tuple contains:
                - the index of the pokeball
                - a string description of pokemon inside:
                    - Name, HP, Level, Type
        """
        detailed_list = []

        for i, ball in enumerate(self.stored_pokemon):
            name = ball.get_name()
            health = ball.get_health()
            level = ball.get_level()
            ptype = ball.get_type()

            description = f"{name} | HP: {health} | Lv: {level} | Type: {ptype}"
            detailed_list.append((i, description))

        return detailed_list
    
    def get_available_pokemon(self) -> Optional[List[Tuple[int, Pokeball]]]:
        """
        Returns:
            A list of tuples (index, Pokéball) where each Pokéball contains a
            non-fainted Pokémon, or None if there are no available Pokémon.
        """
        available = []

        for i, ball in enumerate(self.stored_pokemon):
            if not ball.is_pokemon_fainted():
                available.append((i, ball))

        return available if available else None
    
    def switch_pokemon(self, pokemon: Pokemon, index: int) -> Optional[Pokemon]:
        """
        Swap the given Pokémon with the Pokémon in Pokéball at specified index.

        Returns:
            Pokémon that was previously stored at that index,
            or None if the index is invalid.
        """
        if 0 <= index < len(self.stored_pokemon):
            return self.stored_pokemon[index].switch_pokemon(pokemon)
        return None

    def to_list(self) -> List[List[Any]]:
        return [ball.captured_pokemon.to_list() for ball in self.stored_pokemon if not ball.is_empty()]

    def from_list(self, data: List[List[Any]]):
        self.stored_pokemon = []
        for pmon_data in data:
            pmon = Pokemon.from_list(pmon_data)
            ball = RegularPokeball()
            ball.add(pmon)
            self.stored_pokemon.append(ball)


class Bag:
    """Main inventory class that stores potions, Pokéballs, and captured Pokémon."""
    def __init__(self):
        self.potions = PotionCompartment()
        self.pokeballs = PokeballCompartment()
        self.pokemon = PokemonRoster()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "potions": self.potions.to_dict(),
            "pokeballs": self.pokeballs.to_dict(),
            "pokemon": self.pokemon.to_list()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Bag":
        bag = Bag()
        bag.potions.from_dict(data.get("potions", {}))
        bag.pokeballs.from_dict(data.get("pokeballs", {}))
        bag.pokemon.from_list(data.get("pokemon", []))
        return bag
        