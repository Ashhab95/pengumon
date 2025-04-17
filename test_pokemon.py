import pytest
from types import SimpleNamespace
from .pokemon import *
from .pokedex import PokemonType

#====================Test Pokemon========================

# Fixtures for various evolution states
@pytest.fixture
def starter():
    return PokemonFactory.create_pokemon("Charmander")  # base evolution

@pytest.fixture
def evolved():
    return PokemonFactory.create_pokemon("Charmeleon")  # second evolution

@pytest.fixture
def final():
    return PokemonFactory.create_pokemon("Charizard")  # final evolution

def test_pokemon_initialization(starter):
    """Ensure Pokémon is initialized correctly with expected stats."""
    assert starter.name == "Charmander"
    assert starter.max_health == 50
    assert starter.current_health == 50
    assert starter.p_type == PokemonType.FIRE
    assert isinstance(starter.evolution_state, BaseEvolutionState)

def test_is_fainted_logic(starter):
    """Test if Pokémon correctly detects fainting."""
    starter.current_health = 0
    assert starter.is_fainted()

    starter.current_health = 10
    assert not starter.is_fainted()

def test_take_damage_and_observer_notification(starter):
    """Test if damage is applied and observers are called properly."""
    mock_observer = SimpleNamespace(on_health_changed=lambda p, old, new: setattr(p, "notified", (old, new)))
    starter.add_observer(mock_observer)

    starter.take_damage(30)
    assert starter.current_health == 20
    assert hasattr(starter, "notified")
    assert starter.notified == (50, 20)

def test_attack_mechanics(starter):
    """Test a successful attack on a target Pokémon."""
    target = PokemonFactory.create_pokemon("Bulbasaur")
    result = starter.attack(0, target)

    assert result["success"]
    assert result["message"].startswith("Charmander used")
    assert result["damage"] > 0
    assert not result["target_fainted"]

def test_attack_when_fainted(starter):
    """Test that a fainted Pokémon cannot attack."""
    starter.current_health = 0
    target = PokemonFactory.create_pokemon("Bulbasaur")
    result = starter.attack(0, target)
    assert not result["success"]
    assert "fainted" in result["message"]

def test_level_up_and_evolution(starter):
    """Test that leveling and evolving works correctly."""
    starter.xp = GameConstants.BASE_XP_THRESHOLDD
    starter.level = 3
    evolved = starter.level_up_check()

    assert starter.level == 4
    assert evolved is not None
    assert evolved.name == "Charmeleon"
    assert isinstance(evolved.evolution_state, SecondEvolutionState)

def test_final_evolution_does_not_evolve(final):
    """Ensure final evolution Pokémon does not evolve."""
    final.xp = 999
    final.level = 99
    result = final.level_up_check()
    assert result is None

def test_to_list_and_from_list_roundtrip(starter):
    """Test Pokémon can be serialized and restored properly."""
    data = starter.to_list()
    restored = Pokemon.from_list(data)

    assert restored.name == starter.name
    assert restored.max_health == starter.max_health
    assert restored.current_health == starter.current_health
    assert restored.p_type == starter.p_type
    assert restored.known_attacks == starter.known_attacks
    
    
    
    
    
#====================Test Pokemon Factory========================

def test_create_specific_pokemon():
    """Test that specific Pokémon can be created from the Pokedex."""
    poke = PokemonFactory.create_pokemon("Charizard")
    assert poke.name == "Charizard"
    assert poke.level == 1
    assert isinstance(poke.evolution_state, FinalEvolutionState)

def test_create_starter_pokemon():
    """Test that all three starter Pokémon are created correctly."""
    starters = PokemonFactory.create_starter_pokemon()
    names = [p.name for p in starters]
    assert set(names) == {"Charmander", "Squirtle", "Bulbasaur"}
    for p in starters:
        assert isinstance(p.evolution_state, BaseEvolutionState)






#====================Test Type Adavantages========================

def test_type_advantage():
    assert TypeAdvantageCalculator.calculate_multiplier(PokemonType.FIRE, PokemonType.GRASS, 1) == 1.4
    assert TypeAdvantageCalculator.calculate_multiplier(PokemonType.GRASS, PokemonType.FIRE, 2) == 1.0
    assert TypeAdvantageCalculator.calculate_multiplier(PokemonType.WATER, PokemonType.FIRE, 3) == 2.0





#====================Test Evolution Logics========================

def test_base_evolution_state():
    state = BaseEvolutionState()
    assert state.get_evo_level() == 1
    assert state.get_xp_threshold() == GameConstants.BASE_XP_THRESHOLDD
    assert state.hp_increase() == GameConstants.BASE_HEALTH_INCREASE
    assert state.attack_increase() == GameConstants.BASE_ATTACK_INCREASE
    assert state.get_next_evolution("Charmander") == "Charmeleon"

def test_second_evolution_state():
    state = SecondEvolutionState()
    assert state.get_evo_level() == 2
    assert state.get_xp_threshold() == GameConstants.SECOND_XP_THRESHOLD
    assert state.hp_increase() == GameConstants.SECOND_HEALTH_INCREASE
    assert state.attack_increase() == GameConstants.SECOND_ATTACK_INCREASE
    assert state.get_next_evolution("Charmeleon") == "Charizard"

def test_final_evolution_state():
    state = FinalEvolutionState()
    assert state.get_evo_level() == 3
    assert state.get_next_evolution("Charizard") is None
    assert state.hp_increase() == GameConstants.SECOND_HEALTH_INCREASE
    assert state.attack_increase() == GameConstants.SECOND_ATTACK_INCREASE