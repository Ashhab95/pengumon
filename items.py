from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

# Constants
class PotionConstants:
    SMALL_HEAL = 10
    MEDIUM_HEAL = 20
    LARGE_HEAL = 1000  

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

class Potion(Item):
    def __init__(self, name: str, heal_value: int):
        self.name = name
        self.heal_value = heal_value
    
    def get_name(self) -> str:
        return self.name
    
    def get_value(self) -> int:
        return self.heal_value
    
    def use(self, pokemon) -> Dict[str, Any]:
        if pokemon.is_fainted():
            return {
                "success": False,
                "message": f"{pokemon.name} is fainted and cannot use a potion!"
            }
            
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

class SmallPotion(Potion):
    def __init__(self):
        super().__init__("Small Potion", PotionConstants.SMALL_HEAL)

class MediumPotion(Potion):
    def __init__(self):
        super().__init__("Medium Potion", PotionConstants.MEDIUM_HEAL)

class LargePotion(Potion):
    def __init__(self):
        super().__init__("Large Potion", PotionConstants.LARGE_HEAL)


class PotionDecorator(Potion):
    def __init__(self, base_potion: Potion):
        self.base_potion = base_potion
        super().__init__(f"Enhanced {base_potion.name}", base_potion.heal_value)
    
    def get_name(self) -> str:
        return self.name
    
    def get_value(self) -> int:
        return self.heal_value
    
    def use(self, pokemon) -> Dict[str, Any]:
        return self.base_potion.use(pokemon)

class RevivePotion(PotionDecorator):
    
    def __init__(self, base_potion: Potion):
        super().__init__(base_potion)
        self.name = f"Revive {base_potion.name}"
    
    def use(self, pokemon) -> Dict[str, Any]:
        was_fainted = pokemon.is_fainted()
        
        if was_fainted:
            pokemon.current_health = 1

        result = self.base_potion.use(pokemon)
        
        if was_fainted and result["success"]:
            result["message"] = f"{self.name} revived {pokemon.name} and restored {result['amount_healed']} HP!"
            result["revived"] = True
        
        return result

class PotionFlyweightFactory:
    # Flyweight store
    _flyweights = {}
    
    @classmethod
    def get_potion(cls, potion_type: str) -> Potion:
        key = potion_type.lower()
        
        if key not in cls._flyweights:
            if key == "small potion":
                cls._flyweights[key] = SmallPotion()
            elif key == "medium potion":
                cls._flyweights[key] = MediumPotion()
            elif key == "large potion":
                cls._flyweights[key] = LargePotion()
            elif key == "revive small potion":
                base_potion = cls.get_potion("small potion")
                cls._flyweights[key] = RevivePotion(base_potion)
            elif key == "revive medium potion":
                base_potion = cls.get_potion("medium potion")
                cls._flyweights[key] = RevivePotion(base_potion)
            elif key == "revive large potion":
                base_potion = cls.get_potion("large potion")
                cls._flyweights[key] = RevivePotion(base_potion)
            else:
                raise ValueError(f"Unknown potion type: {potion_type}")
        
        return cls._flyweights[key]
    
    #accessors
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
    
#can add attack potions and defense potions
#attack potion - increases your attack multiplier 