# pokemon_ai.py
import random
from abc import ABC, abstractmethod

class PokemonBattleStrategy(ABC):
    """Abstract base class for Pokemon battle AI strategies"""
    
    @abstractmethod
    def choose_action(self, pokemon, opponent, battle_state=None):
        """
        Choose an action for the AI to take
        
        Args:
            pokemon: The AI's Pokemon
            opponent: The opponent Pokemon
            battle_state: Optional dictionary containing battle state information
            
        Returns:
            Dictionary with action type and details
        """
        pass
    
    @abstractmethod
    def get_difficulty(self):
        """Return the difficulty level of this strategy"""
        pass

class EasyBattleStrategy(PokemonBattleStrategy):
    """
    Easy difficulty AI strategy
    - Prefers weaker attacks
    - Never dodges
    - Makes predictable decisions
    """
    
    def choose_action(self, pokemon, opponent, battle_state=None):
        # Easy AI always attacks and prefers the weakest attack
        attacks = sorted(pokemon.known_attacks, key=lambda x: x['damage'])
        
        # 80% chance to use the weakest attack, 20% chance for a random attack
        if random.random() < 0.8 and len(attacks) > 0:
            chosen_attack = attacks[0]  # Choose the weakest attack
        else:
            chosen_attack = random.choice(pokemon.known_attacks)
            
        return {
            'action_type': 'attack',
            'attack_index': pokemon.known_attacks.index(chosen_attack),
            'attack_name': chosen_attack['name']
        }
    
    def get_difficulty(self):
        return "Easy"

class MediumBattleStrategy(PokemonBattleStrategy):
    """
    Medium difficulty AI strategy
    - Uses a mix of weak and strong attacks
    - Occasionally dodges (25% chance)
    - Makes somewhat intelligent decisions based on health
    """
    
    def choose_action(self, pokemon, opponent, battle_state=None):
        # Calculate health percentage
        health_percentage = pokemon.current_health / pokemon.max_health
        
        # Medium AI has a 25% chance to dodge
        if random.random() < 0.25:
            return {
                'action_type': 'dodge'
            }
        
        # Medium AI uses stronger attacks when health is lower
        if health_percentage < 0.5:
            # Prefer stronger attacks when health is low
            attacks = sorted(pokemon.known_attacks, key=lambda x: x['damage'], reverse=True)
            chosen_attack = attacks[0] if len(attacks) > 0 else random.choice(pokemon.known_attacks)
        else:
            # Mix of random attacks when health is high
            chosen_attack = random.choice(pokemon.known_attacks)
        
        return {
            'action_type': 'attack',
            'attack_index': pokemon.known_attacks.index(chosen_attack),
            'attack_name': chosen_attack['name']
        }
    
    def get_difficulty(self):
        return "Medium"

class HardBattleStrategy(PokemonBattleStrategy):
    """
    Hard difficulty AI strategy
    - Intelligently selects attacks based on type advantage
    - Frequently dodges, especially when health is low
    - Makes strategic decisions throughout the battle
    """
    
    def choose_action(self, pokemon, opponent, battle_state=None):
        # Calculate health percentage
        health_percentage = pokemon.current_health / pokemon.max_health
        
        # Hard AI increasingly dodges as health decreases
        dodge_chance = 0.3 + (0.4 * (1 - health_percentage))  # 30% base, up to 70% at low health
        
        if random.random() < dodge_chance:
            return {
                'action_type': 'dodge'
            }
        
        # Hard AI prioritizes strongest attacks and considers type advantages
        if len(pokemon.known_attacks) > 0:
            # In a more complex implementation, you could calculate type effectiveness here
            # For now, just sort by damage and slightly randomize
            attacks = sorted(pokemon.known_attacks, key=lambda x: x['damage'], reverse=True)
            
            # Use strongest attack 70% of the time, otherwise use a random attack for unpredictability
            if random.random() < 0.7:
                chosen_attack = attacks[0]
            else:
                chosen_attack = random.choice(pokemon.known_attacks)
        else:
            chosen_attack = random.choice(pokemon.known_attacks)
        
        return {
            'action_type': 'attack',
            'attack_index': pokemon.known_attacks.index(chosen_attack),
            'attack_name': chosen_attack['name']
        }
    
    def get_difficulty(self):
        return "Hard"

class WildPokemonAI:
    """
    Wild Pokemon AI controller that uses a strategy pattern
    to determine battle behavior based on difficulty
    """
    
    def __init__(self, difficulty="medium"):
        """
        Initialize the AI with a strategy based on the requested difficulty
        
        Args:
            difficulty: "easy", "medium", or "hard"
        """
        self.set_difficulty(difficulty)
        self.battle_state = {
            'turns': 0,
            'successful_dodges': 0,
            'failed_dodges': 0
        }
    
    def set_difficulty(self, difficulty):
        """
        Set the AI difficulty/strategy
        
        Args:
            difficulty: "easy", "medium", or "hard"
        """
        difficulty = difficulty.lower()
        
        if difficulty == "easy":
            self.strategy = EasyBattleStrategy()
        elif difficulty == "medium":
            self.strategy = MediumBattleStrategy()
        elif difficulty == "hard":
            self.strategy = HardBattleStrategy()
        else:
            # Default to medium if invalid difficulty provided
            self.strategy = MediumBattleStrategy()
    
    def choose_action(self, pokemon, opponent):
        """
        Choose an action for the wild Pokemon to take
        
        Args:
            pokemon: The wild Pokemon
            opponent: The player's Pokemon
            
        Returns:
            Dictionary with action type and details
        """
        self.battle_state['turns'] += 1
        return self.strategy.choose_action(pokemon, opponent, self.battle_state)
    
    def record_dodge_result(self, success):
        """Record the result of a dodge attempt"""
        if success:
            self.battle_state['successful_dodges'] += 1
        else:
            self.battle_state['failed_dodges'] += 1
    
    def get_difficulty(self):
        """Return the current difficulty level"""
        return self.strategy.get_difficulty()


# Factory for creating different AI difficulty levels
class PokemonAIFactory:
    @staticmethod
    def create_wild_pokemon_ai(difficulty="medium"):
        """Create a wild Pokemon AI with the specified difficulty"""
        return WildPokemonAI(difficulty)
    
    @staticmethod
    def create_random_difficulty_ai():
        """Create a wild Pokemon AI with a random difficulty"""
        difficulty = random.choice(["easy", "medium", "hard"])
        return WildPokemonAI(difficulty)