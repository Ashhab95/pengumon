# pokeball.py
import random
from typing import Optional, Dict, Any
from .pokemon import Pokemon
from .items import Item

class Pokeball(Item):
    
    def __init__(self, name: str, catch_rate: float):
        self.name = name
        self.catch_rate = catch_rate
        self.captured_pokemon: Optional[Pokemon] = None
        self.is_active = False
    
    def is_empty(self) -> bool:
        return self.captured_pokemon is None
    
    def get_name(self) -> str:
        if self.is_empty():
            return self.name
        return f"{self.captured_pokemon.name}"
    
    def get_value(self) -> int:
        return int(self.catch_rate * 100)
    
    def get_pokemon(self) -> Optional[Pokemon]:
        return self.captured_pokemon
    
    def set_active(self, active: bool) -> None:
        """Set whether this Pokemon is currently active"""
        self.is_active = active
    
    def is_active_pokemon(self) -> bool:
        """Check if this Pokeball contains the active Pokemon"""
        return self.is_active
    
    def use(self, pokemon) -> Dict[str, Any]:
        return self.catch(pokemon)
    
    def calculate_catch_probability(self, pokemon: Pokemon) -> float:
        health_factor = 1 - (pokemon.current_health / pokemon.max_health)
        return self.catch_rate * (0.5 + health_factor)
    
    def catch(self, pokemon: Pokemon) -> Dict[str, Any]:
        if not self.is_empty():
            return {
                "success": False,
                "message": f"This {self.name} already contains {self.captured_pokemon.name}!"
            }
        
        catch_probability = self.calculate_catch_probability(pokemon)
        success = random.random() < catch_probability
        
        if success:
            self.captured_pokemon = pokemon
            return {
                "success": True,
                "message": f"Gotcha! {pokemon.name} was caught in the {self.name}!",
                "pokemon": pokemon
            }
        else:
            return {
                "success": False,
                "message": f"{pokemon.name} broke free from the {self.name}!"
            }
    
    '''
    may implement this if we plan on releasing pokemon out in the wild
    def release(self) -> Dict[str, Any]:
        """
        Release the captured Pokemon
        
        Returns:
            A dictionary with the result of the release attempt
        """
        if self.is_empty():
            return {
                "success": False,
                "message": f"This {self.name} is already empty!"
            }
        
        pokemon = self.captured_pokemon
        self.captured_pokemon = None
        self.is_active = False
        
        return {
            "success": True,
            "message": f"{pokemon.name} was released from the {self.name}!",
            "pokemon": pokemon
        }
    
    def __str__(self) -> str:
        """String representation of the Pokeball"""
        active_marker = " (ACTIVE)" if self.is_active else ""
        if self.is_empty():
            return f"{self.name} (Empty){active_marker}"
        return f"{self.name} ({self.captured_pokemon.name}){active_marker}" 
    '''


class RegularPokeball(Pokeball):
    """Standard Pokeball with basic catch rate"""
    def __init__(self):
        super().__init__("Pokeball", 0.5)


class GreatBall(Pokeball):
    """Great Ball with improved catch rate"""
    def __init__(self):
        super().__init__("Great Ball", 0.7)


class UltraBall(Pokeball):
    """Ultra Ball with high catch rate"""
    def __init__(self):
        super().__init__("Ultra Ball", 0.85)


class MasterBall(Pokeball):
    """Master Ball with 100% catch rate"""
    def __init__(self):
        super().__init__("Master Ball", 1.0)
    
    def calculate_catch_probability(self, pokemon: Pokemon) -> float:
        """Master Ball always has 100% catch probability"""
        return 1.0