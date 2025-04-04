import random
from typing import Optional, Dict, Any
from .pokemon import Pokemon
from .items import Item

class Pokeball(Item):
    
    def __init__(self, name: str, catch_rate: float):
        self.name = name
        self.catch_rate = catch_rate
        self.captured_pokemon: Optional[Pokemon] = None

    def get_name(self) -> str:
        """Peak the name of the Pokémon inside the Pokéball"""
        if self.is_empty():
            return "Empty"
        return self.captured_pokemon.name

    def get_value(self) -> int:
        """Get the catch rate of the Pokéball"""
        return int(self.catch_rate * 100)
    
    def use(self, pokemon) -> bool:
        """Using pokeball to catch a wild pokemon
        Returns: true if the pokemon is caught, false otherwise
        """
        health_factor = pokemon.current_health / pokemon.max_health
        success = random.random() < self.catch_rate * (1 - health_factor)
        if success:
            self.captured_pokemon = pokemon
            return True
        return False
    
    def add(self, pokemon: Pokemon) -> bool:
        """Add a Pokémon to the Pokéball, used for testing purposes"""
        if self.is_empty():
            self.captured_pokemon = pokemon
            return True
        return False

    # Methods we are not overriding
    def get_health(self) -> str:
        """Get the health of the Pokémon inside the Pokéball"""
        if self.is_empty():
            return "Empty"
        return f"{self.captured_pokemon.current_health}/{self.captured_pokemon.max_health}"
    
    def get_level(self) -> str:
        """Get the level of the Pokémon inside the Pokéball"""
        if self.is_empty():
            return "Empty"
        return f"{self.captured_pokemon.level}"
    
    def get_type(self) -> str:
        """Get the type of the Pokémon inside the Pokéball"""
        if self.is_empty():
            return "Empty"
        return self.captured_pokemon.p_type
    
    def is_empty(self) -> bool:
        return self.captured_pokemon is None

    def switch_pokemon(self, pokemon: Pokemon) -> Pokemon:
        """Swap the current captured Pokémon with another one."""
        old_pokemon = self.captured_pokemon
        self.captured_pokemon = pokemon
        return old_pokemon

    def is_pokemon_fainted(self) -> bool:
        """Check if the Pokémon inside has fainted"""
        return self.captured_pokemon.is_fainted()


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
