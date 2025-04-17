import pytest
import random
from .enemyAI import EasyAI, MediumAI, HardAI

# Define a dummy Pokemon for unit testing
@pytest.fixture
def dummy_pokemon():
    """Returns dummy pokemon."""
    class DummyPokemon:
        def __init__(self):
            self.known_attacks = [
                {"name": "Ember", "damage": 10},
                {"name": "Flame Wheel", "damage": 30},
                {"name": "Fire Blast", "damage": 60}
            ]
            self.current_health = 50
            self.max_health = 100
    return DummyPokemon()

def test_easy_ai_dodge_chance(monkeypatch, dummy_pokemon):
    """Ensure EasyAI dodges ~ 20% of the time."""
    ai = EasyAI()
    monkeypatch.setattr(random, "random", lambda: 0.1)
    assert ai.choose_action(dummy_pokemon, dummy_pokemon) == "Dodge"

    monkeypatch.setattr(random, "random", lambda: 0.9)
    action = ai.choose_action(dummy_pokemon, dummy_pokemon)
    assert action.isdigit()

def test_easy_ai_favors_weaker_attacks(dummy_pokemon):
    """Ensure EasyAI favers weaker attacks more often than stronger ones."""
    ai = EasyAI()
    random.seed(1)
    actions = [ai.choose_action(dummy_pokemon, dummy_pokemon) for _ in range(100)]
    action_counts = {str(i): actions.count(str(i)) for i in range(len(dummy_pokemon.known_attacks))}
    assert action_counts['0'] > action_counts['2']  # weakest attack used more than strongest one

def test_medium_ai_balanced_behavior(monkeypatch, dummy_pokemon):
    """Ensure MediumAI can dodge and randomly select attacks."""
    ai = MediumAI()
    monkeypatch.setattr(random, "random", lambda: 0.2)
    assert ai.choose_action(dummy_pokemon, dummy_pokemon) == "Dodge"

    monkeypatch.setattr(random, "random", lambda: 0.9)
    action = ai.choose_action(dummy_pokemon, dummy_pokemon)
    assert action.isdigit()

def test_hard_ai_low_hp_dodge(monkeypatch, dummy_pokemon):
    """Ensure HardAI dodges more when health is low."""
    ai = HardAI()
    dummy_pokemon.current_health = 5  # low HP
    monkeypatch.setattr(random, "random", lambda: 0.35)
    assert ai.choose_action(dummy_pokemon, dummy_pokemon) == "Dodge"

def test_hard_ai_favors_strong_attacks(dummy_pokemon):
    """Ensure HardAI favers stronger attacks more freqeuntly."""
    ai = HardAI()
    dummy_pokemon.current_health = 50
    random.seed(3)
    actions = [ai.choose_action(dummy_pokemon, dummy_pokemon) for _ in range(100)]
    action_counts = {str(i): actions.count(str(i)) for i in range(len(dummy_pokemon.known_attacks))}
    assert action_counts['2'] > action_counts['0']  # strongest attack preferred

def test_all_ai_return_valid_action(dummy_pokemon):
    """Check all AI subclasses return either a valid index or 'Dodge'."""
    for ai_cls in [EasyAI, MediumAI, HardAI]:
        ai = ai_cls()
        action = ai.choose_action(dummy_pokemon, dummy_pokemon)
        assert action == "Dodge" or (action.isdigit() and int(action) in range(len(dummy_pokemon.known_attacks)))