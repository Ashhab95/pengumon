from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

# Constants
class PotionConstants:
    SMALL_HEAL = 10
    MEDIUM_HEAL = 20
    LARGE_HEAL = 1000  

# ---- Base Item Class ----
class Item(ABC):
    """Abstract base class for items."""
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the item."""
        pass

    @abstractmethod
    def get_value(self) -> int:
        """Return the item's effect value (e.g., healing)."""
        pass

    @abstractmethod
    def use(self, target) -> bool:
        """Apply the item effect to a target."""
        pass

# ---- Potion Base Class ----
class Potion(Item):
    """Basic healing potion."""
    def __init__(self, name: str, heal_value: int):
        """Initialize potion with name and healing value."""
        self.name = name
        self.heal_value = heal_value

    def get_name(self) -> str:
        """Return the name of the potion."""
        return self.name

    def get_value(self) -> int:
        """Return the healing value of the potion."""
        return self.heal_value

    def use(self, pokemon) -> bool:
        """Heal the Pokémon if it's not fainted or at full health."""
        if pokemon.is_fainted():
            return False

        if pokemon.current_health == pokemon.max_health:
            return False

        old_health = pokemon.current_health
        pokemon.current_health = min(pokemon.max_health, pokemon.current_health + self.heal_value)
        amount_healed = pokemon.current_health - old_health

        return True

    def is_revive(self) -> bool:
        """Check if this is a revive potion."""
        return False

    def to_list(self) -> list:
        """Serialize potion for saving."""
        return ["potion", self.name]

    @staticmethod
    def from_list(data: list) -> 'Potion':
        """Deserialize potion from saved data."""
        return PotionFlyweightFactory.get_potion(data[1])

# ---- Concrete Potions ----
class SmallPotion(Potion):
    """Small healing potion."""
    def __init__(self):
        super().__init__("Small Potion", PotionConstants.SMALL_HEAL)

class MediumPotion(Potion):
    """Medium healing potion."""
    def __init__(self):
        super().__init__("Medium Potion", PotionConstants.MEDIUM_HEAL)

class LargePotion(Potion):
    """Large healing potion."""
    def __init__(self):
        super().__init__("Large Potion", PotionConstants.LARGE_HEAL)

# ---- Abstract Decorator ----
class PotionDecorator(Potion, ABC):
    def __init__(self, health_potion: Potion):
        """Wrap a potion to extend its functionality."""
        if isinstance(health_potion, RevivePotion):
            raise ValueError("Cannot decorate a revive potion")
        self.health_potion = health_potion
        super().__init__(health_potion.get_name(), health_potion.get_value())

    def get_name(self) -> str:
        """Return the name of the decorated potion."""
        return self.health_potion.get_name()

    def get_value(self) -> int:
        """Return the healing value of the decorated potion."""
        return self.health_potion.get_value()

    def use(self, pokemon) -> bool:
        """Apply the decorated potion effect."""
        return self.health_potion.use(pokemon)

# ---- Revive Decorator ----
class RevivePotion(PotionDecorator):
    def __init__(self, health_potion: Potion):
        super().__init__(health_potion)

    def get_name(self) -> str:
        return f"Revive {self.health_potion.get_name()}"

    def is_revive(self) -> bool:
        return True

    def use(self, pokemon) -> Dict[str, Any]:
        """Revive the Pokémon if fainted, then heal."""
        if pokemon.is_fainted():
            pokemon.current_health = 1
        return self.health_potion.use(pokemon)

    def to_list(self) -> list:
        return ["revive_potion", self.health_potion.get_name()]

    @staticmethod
    def from_list(data: list) -> 'RevivePotion':
        base_potion = PotionFlyweightFactory.get_potion(data[1])
        return RevivePotion(base_potion)

# ---- Flyweight Factory ----
class PotionFlyweightFactory:
    _flyweights = {}

    @classmethod
    def get_potion(cls, potion_type: str) -> Potion:
        """Return a shared potion instance based on type."""
        key = potion_type.lower()

        if key not in cls._flyweights:
            if key == "small potion":
                cls._flyweights[key] = SmallPotion()
            elif key == "medium potion":
                cls._flyweights[key] = MediumPotion()
            elif key == "large potion":
                cls._flyweights[key] = LargePotion()
            elif key == "revive small potion":
                health_potion = cls.get_potion("small potion")
                cls._flyweights[key] = RevivePotion(health_potion)
            elif key == "revive medium potion":
                health_potion = cls.get_potion("medium potion")
                cls._flyweights[key] = RevivePotion(health_potion)
            elif key == "revive large potion":
                health_potion = cls.get_potion("large potion")
                cls._flyweights[key] = RevivePotion(health_potion)
            else:
                raise ValueError(f"Unknown potion type: {potion_type}")

        return cls._flyweights[key]

    # Accessors
    @classmethod
    def get_small_potion(cls) -> Potion:
        return cls.get_potion("small potion")

    @classmethod
    def get_medium_potion(cls) -> Potion:
        return cls.get_potion("medium potion")

    @classmethod
    def get_large_potion(cls) -> Potion:
        return cls.get_potion("large potion")

    @classmethod
    def get_revive_small_potion(cls) -> Potion:
        return cls.get_potion("revive small potion")

    @classmethod
    def get_revive_medium_potion(cls) -> Potion:
        return cls.get_potion("revive medium potion")

    @classmethod
    def get_revive_large_potion(cls) -> Potion:
        return cls.get_potion("revive large potion")

    @classmethod
    def get_max_revive(cls) -> Potion:
        return cls.get_revive_large_potion()
