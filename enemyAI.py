from abc import ABC, abstractmethod
from .pokemon import *
import random

class EnemyAI:
    """Base enemy AI class"""
    def choose_action(self, enemy_pokemon, player_pokemon) -> str:
        raise NotImplementedError("This should be implemented by subclasses.")
    
class EnemyAI(ABC):
    """Abstract class for enemy AI"""

    @abstractmethod
    def choose_action(self, enemy_pokemon, player_pokemon) -> str:
        """Decides action: return an attack index as string or 'dodge'."""
        pass


class EasyAI(EnemyAI):
    def choose_action(self, enemy_pokemon, player_pokemon) -> str:
        if random.random() < 0.2:
            return "Dodge"

        attack_indices = []
        weights = []

        for i, attack in enumerate(enemy_pokemon.known_attacks):
            attack_indices.append(i)
            weights.append(1 / attack['damage'])  # favor weaker attacks

        total_weight = sum(weights)
        probabilities = []
        for w in weights:
            probabilities.append(w / total_weight)

        chosen_index = random.choices(attack_indices, weights=probabilities)[0]
        return str(chosen_index)


class MediumAI(EnemyAI):
    def choose_action(self, enemy_pokemon, player_pokemon) -> str:
        if random.random() < 0.3:
            return "Dodge"

        attack_indices = [i for i in range(len(enemy_pokemon.known_attacks))]
        chosen_index = random.choice(attack_indices)
        return str(chosen_index)


class HardAI(EnemyAI):
    def choose_action(self, enemy_pokemon, player_pokemon) -> str:
        hp_ratio = enemy_pokemon.current_health / enemy_pokemon.max_health
        if hp_ratio < 0.3 and random.random() < 0.4:
            return "Dodge"
        if random.random() < 0.15:
            return "Dodge"

        attack_indices = []
        weights = []

        for i, attack in enumerate(enemy_pokemon.known_attacks):
            attack_indices.append(i)
            weights.append(attack['damage'])  # favor stronger attacks

        total_weight = sum(weights)
        probabilities = []
        for w in weights:
            probabilities.append(w / total_weight)

        chosen_index = random.choices(attack_indices, weights=probabilities)[0]
        return str(chosen_index)