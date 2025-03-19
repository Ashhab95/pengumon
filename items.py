# items.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

# Abstract Component for items
class Item(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_value(self) -> int:
        pass
    
    @abstractmethod
    def use(self, target) -> Dict[str, Any]:
        pass

# Base Potion class (replaced the decorator pattern)
class Potion(Item):
    def __init__(self, name: str, heal_value: int):
        self.name = name
        self.heal_value = heal_value
    
    def get_name(self) -> str:
        return self.name
    
    def get_value(self) -> int:
        return self.heal_value
    
    def use(self, pokemon) -> Dict[str, Any]:
        if pokemon.current_health == pokemon.max_health:
            return {
                "success": False,
                "message": f"{pokemon.name} already has full health!"
            }
        
        old_health = pokemon.current_health
        pokemon.current_health = min(pokemon.max_health, pokemon.current_health + self.heal_value)
        amount_healed = pokemon.current_health - old_health
        
        return {
            "success": True,
            "message": f"{self.name} restored {amount_healed} HP to {pokemon.name}!",
            "amount_healed": amount_healed
        }

# Concrete Potion classes
class SmallPotion(Potion):
    def __init__(self):
        super().__init__("Small Potion", 20)

class MediumPotion(Potion):
    def __init__(self):
        super().__init__("Medium Potion", 40)

class LargePotion(Potion):
    def __init__(self):
        super().__init__("Large Potion", 70)

# Flyweight Factory - Manages flyweight objects
class PotionFlyweightFactory:
    # Shared class-level dictionary to store flyweight instances
    _flyweights = {}
    
    @classmethod
    def get_small_potion(cls) -> Potion:
        """Get or create a small potion flyweight object"""
        key = "small_potion"
        if key not in cls._flyweights:
            cls._flyweights[key] = SmallPotion()
        return cls._flyweights[key]
    
    @classmethod
    def get_medium_potion(cls) -> Potion:
        """Get or create a medium potion flyweight object"""
        key = "medium_potion"
        if key not in cls._flyweights:
            cls._flyweights[key] = MediumPotion()
        return cls._flyweights[key]
    
    @classmethod
    def get_large_potion(cls) -> Potion:
        """Get or create a large potion flyweight object"""
        key = "large_potion"
        if key not in cls._flyweights:
            cls._flyweights[key] = LargePotion()
        return cls._flyweights[key]
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional[Potion]:
        """Get a flyweight by its name"""
        name_lower = name.lower()
        if name_lower == "small potion":
            return cls.get_small_potion()
        elif name_lower == "medium potion":
            return cls.get_medium_potion()
        elif name_lower == "large potion":
            return cls.get_large_potion()
        return None
    
    @classmethod
    def get_flyweight_count(cls) -> int:
        """Return the number of flyweight instances"""
        return len(cls._flyweights)

