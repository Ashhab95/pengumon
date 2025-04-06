from typing import Dict, List, Optional, Any
from .pokedex import *
from .observers import HealthObserver

# Constants
class GameConstants:
    BASE_XP_THRESHOLDD = 30
    SECOND_XP_THRESHOLD = 60
    
    BASE_HEALTH_INCREASE = 10
    SECOND_HEALTH_INCREASE = 15
    
    BASE_ATTACK_INCREASE = 5
    SECOND_ATTACK_INCREASE = 4
    
    EVOLUTION_LEVEL_THRESHOLD = 4

class TypeAdvantageCalculator:
    @staticmethod
    def calculate_multiplier(attacker_type, defender_type, evolution_level: int = 1):
        if evolution_level == 1:  
            advantage = 1.4
        elif evolution_level == 2: 
            advantage = 1.65
        elif evolution_level == 3: 
            advantage = 2.0
            
        if ((attacker_type == PokemonType.FIRE and defender_type == PokemonType.GRASS) or
            (attacker_type == PokemonType.WATER and defender_type == PokemonType.FIRE) or
            (attacker_type == PokemonType.GRASS and defender_type == PokemonType.WATER)):
            return advantage
        
        return 1.0

#Using state pattern for handing evolution  
class EvolutionState:
    """Base class for Pokemon evolution states"""
    def __init__(self, level: int):
        self.evolution_level = level
    
    def get_evo_level(self):
        return self.evolution_level
    
    def get_xp_threshold(self) -> int:
        return GameConstants.BASE_XP_THRESHOLDD
    
    def get_type_multiplier(self, attacker_type, defender_type):
        return TypeAdvantageCalculator.calculate_multiplier(
            attacker_type, defender_type, self.evolution_level)
    
    def hp_increase(self):
        return GameConstants.BASE_HEALTH_INCREASE
    
    def attack_increase(self):
        return GameConstants.BASE_ATTACK_INCREASE
    
    def get_next_evolution(self, pokemon_name: str) -> Optional[str]:
        return None 

# First evolution state
class BaseEvolutionState(EvolutionState):
    def __init__(self):
        super().__init__(level=1)
    
    def get_next_evolution(self, pokemon_name):
        return first_evolution_map.get(pokemon_name)


class SecondEvolutionState(EvolutionState):
    def __init__(self):
        super().__init__(level=2)
    
    def hp_increase(self):
        return GameConstants.SECOND_HEALTH_INCREASE
    
    def attack_increase(self):
        return GameConstants.SECOND_ATTACK_INCREASE
    
    def get_xp_threshold(self):
        return GameConstants.SECOND_XP_THRESHOLD
    
    def get_next_evolution(self, pokemon_name: str) -> Optional[str]:
        return second_evolution_map.get(pokemon_name)

# Final evolution state
class FinalEvolutionState(EvolutionState):
    def __init__(self):
        super().__init__(level=3)
    
    def hp_increase(self) -> int:
        return GameConstants.SECOND_HEALTH_INCREASE
    
    def attack_increase(self) -> int:
        return GameConstants.SECOND_ATTACK_INCREASE
    
    def get_next_evolution(self, pokemon_name: str) -> Optional[str]:
        # Final evolution, so no next evolution
        return None

class Pokemon:
    def __init__(self, name: str):
        data = pokedex.get(name)
        if not data:
            raise ValueError(f"{name} not found in the Pokedex.")

        self.name = data['name']
        self.max_health = int(data['max_health'])
        self.current_health = self.max_health
        self.p_type = data['type']
        self.level = int(data['level'])
        self.xp = int(data['xp'])
        self.known_attacks = data['attacks'][:]
        self._observers: list[HealthObserver] = []  # Health observer list

        if name in ["Charmander", "Squirtle", "Bulbasaur", "Chimchar", "Piplup", "Turtwig"]:
            self.evolution_state = BaseEvolutionState()
        elif name in ["Charmeleon", "Wartortle", "Ivysaur", "Monferno", "Prinplup", "Grotle"]:
            self.evolution_state = SecondEvolutionState()
        elif name in ["Charizard", "Blastoise", "Venusaur", "Infernape", "Empoleon", "Torterra"]:
            self.evolution_state = FinalEvolutionState()


    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('_observers', None)  # Remove unpickleable observers
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._observers = []  # Restore empty observer list

    def add_observer(self, observer: HealthObserver):
        """Register a new observer that will be notified on health changes."""
        self._observers.append(observer)

    def notify_observers(self, old_hp: int, new_hp: int):
        """Notify all registered observers of a health change."""
        for observer in self._observers:
            observer.on_health_changed(self, old_hp, new_hp)

    def is_fainted(self):
        return self.current_health <= 0

    def take_damage(self, damage):
        old_hp = self.current_health
        self.current_health = max(0, self.current_health - damage)
        self.notify_observers(old_hp, self.current_health)

    def attack(self, attack_index, target):
        # Template method pattern
        if self.is_fainted():
            return {"success": False, "message": f"{self.name} is fainted and cannot attack!"}

        attack = self.known_attacks[attack_index]
        base_damage = attack["damage"]

        # Calculate damage multiplier based on evolution state
        multiplier = self.evolution_state.get_type_multiplier(self.p_type, target.p_type)
        final_damage = int(base_damage * multiplier)

        target.take_damage(final_damage)

        result = {
            "success": True,
            "message": f"{self.name} used {attack['name']} on {target.name}!",
            "damage": final_damage,
            "target_fainted": target.is_fainted(),
            "evolved": None
        }

        if target.is_fainted():
            self.xp += 10
            evolved_pokemon = self.level_up_check()
            if evolved_pokemon:
                result["evolved"] = evolved_pokemon

        return result

    def level_up_check(self):
        if isinstance(self.evolution_state, FinalEvolutionState):
            # Final form — no more level-ups
            return None

        if self.xp >= self.evolution_state.get_xp_threshold():
            self.xp = 0
            self.level += 1

            hp_increase = self.evolution_state.hp_increase()
            attack_increase = self.evolution_state.attack_increase()

            self.max_health += hp_increase
            self.current_health = self.max_health
            for attack in self.known_attacks:
                attack["damage"] += attack_increase

            if self.level == GameConstants.EVOLUTION_LEVEL_THRESHOLD:
                next_evolution = self.evolution_state.get_next_evolution(self.name)
                if next_evolution:
                    return self.evolve(next_evolution)

        return None

    def evolve(self, evolution_name: str) -> 'Pokemon':
        """Evolve this Pokemon to the next form"""
        evolved_pokemon = Pokemon(evolution_name)

        # Update evolution state based on current state
        if isinstance(self.evolution_state, BaseEvolutionState):
            evolved_pokemon.evolution_state = SecondEvolutionState()
        elif isinstance(self.evolution_state, SecondEvolutionState):
            evolved_pokemon.evolution_state = FinalEvolutionState()

        return evolved_pokemon
    
    def to_list(self) -> list:
        print(self.p_type.name)
        print(type(self.p_type.name))
        return [
            self.name,
            self.max_health,
            self.current_health,
            self.p_type.name,
            self.level,
            self.xp,
            self.known_attacks,
            self.evolution_state.__class__.__name__
        ]

    @staticmethod
    def from_list(data: list) -> 'Pokemon':
        name, max_health, current_health, p_type, level, xp, known_attacks, evo_class = data
        poke = Pokemon(name)
        poke.max_health = max_health
        poke.current_health = current_health
        # Manually assign enum based on string
        if p_type == "FIRE":
            poke.p_type = PokemonType.FIRE
        elif p_type == "WATER":
            poke.p_type = PokemonType.WATER
        elif p_type == "GRASS":
            poke.p_type = PokemonType.GRASS
        poke.level = level
        poke.xp = xp
        poke.known_attacks = known_attacks
        if evo_class == "BaseEvolutionState":
            poke.evolution_state = BaseEvolutionState()
        elif evo_class == "SecondEvolutionState":
            poke.evolution_state = SecondEvolutionState()
        elif evo_class == "FinalEvolutionState":
            poke.evolution_state = FinalEvolutionState()
            
        return poke


# Pokemon Factory
class PokemonFactory:
    @staticmethod
    def create_pokemon(name: str) -> Pokemon:
        return Pokemon(name)
    
    @staticmethod
    def create_starter_pokemon() -> List[Pokemon]:
        """Create the three starter Pokemon"""
        return [
            PokemonFactory.create_pokemon("Charmander"),
            PokemonFactory.create_pokemon("Squirtle"),
            PokemonFactory.create_pokemon("Bulbasaur")
        ]
    
    @staticmethod 
    def create_random_wild_pokemon(level):
        import random
        
        # Choose a random Pokemon type
        starter_options = [ "Charmander", "Squirtle", "Bulbasaur", "Chimchar", "Piplup", "Turtwig"]

        pokemon = PokemonFactory.create_pokemon(random.choice(starter_options))
        
        # Get target level
        target_level = random.randint(*level)
        
        # Properly level up the Pokemon to reach the target level
        while pokemon.level < level:
            pokemon.xp = GameConstants.BASE_XP_THRESHOLDD
            evolved = pokemon.level_up_check()
            if evolved:
                pokemon = evolved
        
        return pokemon