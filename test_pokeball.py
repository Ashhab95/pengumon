import pytest
import random
from .pokeball import Pokeball, RegularPokeball, GreatBall, UltraBall, MasterBall

class DummyPokemon:
    """A minimal Pokemon class for testing purposes."""
    def __init__(self, name="Dummy", current_health=20, max_health=50, level=3, p_type="FIRE"):
        self.name = name
        self.current_health = current_health
        self.max_health = max_health
        self.level = level
        self.p_type = p_type

    def take_damage(self, damage):
        self.current_health = max(0, self.current_health - damage)

    def is_fainted(self):
        return self.current_health == 0

    def to_list(self):
        return [
            self.name,
            self.max_health,
            self.current_health,
            self.p_type,
            self.level,
            0,  # XP (unused)
            [],  # attacks (unused)
            "BaseEvolutionState"
        ]

    @staticmethod
    def from_list(data):
        name, max_health, current_health, p_type, level, *_ = data
        return DummyPokemon(name, current_health, max_health, level, p_type)

@pytest.fixture
def dummy_pokemon():
    return DummyPokemon()

def test_pokeball_get_name_and_empty_behavior(dummy_pokemon):
    """Test the name and empty behavior of the Pokeball."""
    ball = Pokeball("Test Ball", 0.5)
    assert ball.get_name() == "Empty"
    assert ball.is_empty() is True
    ball.add(dummy_pokemon)
    assert ball.get_name() == "Dummy"
    assert ball.is_empty() is False

def test_pokeball_get_value():
    """Test the value of the Pokeball based on its catch rate."""
    ball = Pokeball("Test Ball", 0.3)
    assert ball.get_value() == 30

def test_pokeball_use_success(monkeypatch, dummy_pokemon):
    """Test successful capture due to high catch rate and low health."""
    dummy_pokemon.current_health = 1
    ball = Pokeball("Test Ball", 1.0)
    monkeypatch.setattr(random, "random", lambda: 0.01)
    assert ball.use(dummy_pokemon) is True
    assert ball.get_name() == "Dummy"

def test_pokeball_use_fail(monkeypatch, dummy_pokemon):
    """Test failed capture due to full health and low catch rate."""
    dummy_pokemon.current_health = dummy_pokemon.max_health
    ball = Pokeball("Test Ball", 0.1)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    assert ball.use(dummy_pokemon) is False
    assert ball.is_empty()

def test_add_only_if_empty(dummy_pokemon):
    """Test that a Pokeball can only add a Pokemon if empty."""
    ball = Pokeball("Test Ball", 0.5)
    assert ball.add(dummy_pokemon) is True
    second = DummyPokemon("Other")
    assert ball.add(second) is False

def test_get_stats_methods(dummy_pokemon):
    """Test the stats retrieval methods of Pokeball."""
    ball = Pokeball("Test Ball", 0.5)
    ball.add(dummy_pokemon)
    assert ball.get_health() == f"{dummy_pokemon.current_health}/{dummy_pokemon.max_health}"
    assert ball.get_level() == str(dummy_pokemon.level)
    assert ball.get_type() == dummy_pokemon.p_type

def test_switch_pokemon_behavior(dummy_pokemon):
    """Test the behavior of switching pokemon in Pokeball."""
    ball = Pokeball("Test Ball", 0.5)
    ball.add(dummy_pokemon)
    new_pokemon = DummyPokemon("Other")
    old = ball.switch_pokemon(new_pokemon)
    assert ball.get_name() == "Other"
    assert old.name == "Dummy"

def test_is_pokemon_fainted(dummy_pokemon):
    """Test the fainted state of the pokemon in Pokeball."""
    ball = Pokeball("Test Ball", 0.5)
    dummy_pokemon.take_damage(dummy_pokemon.max_health)
    ball.add(dummy_pokemon)
    assert ball.is_pokemon_fainted() is True

def test_to_from_list_serialization(dummy_pokemon, monkeypatch):
    """Test serialization and deserialization of Pokeball."""
    ball = Pokeball("Test Ball", 0.5)
    ball.add(dummy_pokemon)
    data = ball.to_list()

    # Overriding from_list method to use DummyPokemon for testing
    monkeypatch.setattr("pengumon.pokeball.Pokemon", DummyPokemon)
    
    restored = Pokeball.from_list(data)
    assert isinstance(restored, Pokeball)
    assert restored.get_name() == "Dummy"
    assert restored.get_type() == dummy_pokemon.p_type

def test_ball_types_inherit_properly():
    """Test that all Pokeball types inherit from base Pokeball class."""
    assert isinstance(RegularPokeball(), Pokeball)
    assert RegularPokeball().catch_rate == 0.5
    assert GreatBall().catch_rate == 0.7
    assert UltraBall().catch_rate == 0.85
    assert MasterBall().catch_rate == 1.0