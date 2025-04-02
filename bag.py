from typing import List, Dict, Any, Optional, Tuple
from .items import Item, Potion, SmallPotion, MediumPotion, LargePotion, RevivePotion
from .pokeball import Pokeball, RegularPokeball, GreatBall, UltraBall, MasterBall
from .pokemon import Pokemon

class ItemCompartment:
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


class PotionCompartment(ItemCompartment):
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
        if isinstance(item, SmallPotion) and item.is_revive(): return "small_revive"
        elif isinstance(item, MediumPotion) and item.is_revive(): return "medium_revive"
        elif isinstance(item, LargePotion) and item.is_revive(): return "large_revive"
        elif isinstance(item, SmallPotion): return "small"
        elif isinstance(item, MediumPotion): return "medium"
        elif isinstance(item, LargePotion): return "large"
        raise ValueError("Unsupported potion type")

    def _increment(self, key: str): self._counts[key] += 1
    def _decrement(self, key: str): self._counts[key] -= 1
    def _has_item(self, key: str) -> bool: return self._counts.get(key, 0) > 0

    def _make_item(self, key: str) -> Optional[Potion]:
        if key == "small": return SmallPotion()
        elif key == "medium": return MediumPotion()
        elif key == "large": return LargePotion()
        elif key == "small_revive": return SmallPotion(revive=True)
        elif key == "medium_revive": return MediumPotion(revive=True)
        elif key == "large_revive": return LargePotion(revive=True)
        return None

    def _get_counts(self) -> Dict[str, int]:
        return self._counts


class PokeballCompartment(ItemCompartment):
    def __init__(self):
        super().__init__("Empty Pokeballs")
        self._counts = {"pokeball": 0, "greatball": 0, "ultraball": 0, "masterball": 0}

    def get_item_key(self, item: Item) -> str:
        if isinstance(item, RegularPokeball): return "pokeball"
        elif isinstance(item, GreatBall): return "greatball"
        elif isinstance(item, UltraBall): return "ultraball"
        elif isinstance(item, MasterBall): return "masterball"
        raise ValueError("Unsupported pokeball type")

    def _increment(self, key: str): self._counts[key] += 1
    def _decrement(self, key: str): self._counts[key] -= 1
    def _has_item(self, key: str) -> bool: return self._counts.get(key, 0) > 0

    def _make_item(self, key: str) -> Optional[Pokeball]:
        if key == "pokeball": return RegularPokeball()
        elif key == "greatball": return GreatBall()
        elif key == "ultraball": return UltraBall()
        elif key == "masterball": return MasterBall()
        return None

    def _get_counts(self) -> Dict[str, int]:
        return self._counts


class PokemonCompartment:
    def __init__(self):
        self.name = "Your Pokemon"
        self.pokemon_balls: List[Pokeball] = []

    def add(self, pokeball: Pokeball):
        self.pokemon_balls.append(pokeball)

    def remove(self, index: int) -> Optional[Pokeball]:
        if 0 <= index < len(self.pokemon_balls):
            return self.pokemon_balls.pop(index)
        return None

    def get(self, index: int) -> Optional[Pokeball]:
        if 0 <= index < len(self.pokemon_balls):
            return self.pokemon_balls[index]
        return None

    def list_items(self) -> List[Tuple[int, Pokeball]]:
        return [(i, ball) for i, ball in enumerate(self.pokemon_balls)]

    def count(self) -> int:
        return len(self.pokemon_balls)

    def __str__(self):
        return f"{self.name} compartment"


class Bag:
    def __init__(self):
        self.potions = PotionCompartment()
        self.pokeballs = PokeballCompartment()
        self.pokemon = PokemonCompartment()

    def __str__(self):
        parts = [
            str(self.potions),
            str(self.pokeballs),
            str(self.pokemon)
        ]
        return "Bag Contents:\n" + "\n".join(parts)

    def list_all_items(self) -> Dict[str, List[str]]:
        return {
            "potions": self.potions.list_items(),
            "pokeballs": self.pokeballs.list_items(),
            "pokemon": [f"{i}: {ball}" for i, ball in self.pokemon.list_items()]
        }