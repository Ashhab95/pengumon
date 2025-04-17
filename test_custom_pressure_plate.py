import pytest
from types import SimpleNamespace
from .custom_pressure_plates import *
from .bag import Bag

# ---------------------- Dummy Classes ------------------------

class DummyPokemon:
    def __init__(self, name="Dummy", current_hp=30, max_hp=50):
        self.name = name
        self.current_health = current_hp
        self.max_health = max_hp
        self.level = 5
        self.p_type = SimpleNamespace(name="WATER")

    def to_list(self):
        return [self.name, self.max_health, self.current_health, self.p_type.name, self.level, 0, [], "BaseEvolutionState"]

    @staticmethod
    def from_list(data):
        return DummyPokemon(name=data[0], max_hp=data[1], current_hp=data[2])

    def is_fainted(self):
        return self.current_health == 0

class DummyPlayer:
    def __init__(self):
        self.state = {}
        self.menu = None
        self.room = SimpleNamespace(remove_from_grid=lambda map_obj, start_pos: None)

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value

    def set_current_menu(self, menu):
        self.menu = menu

    def get_current_room(self):
        return self.room

# ---------------------- Fixtures ------------------------

@pytest.fixture
def dummy_player():
    return DummyPlayer()

@pytest.fixture
def dummy_pokemon():
    return DummyPokemon()

# ---------------------- PokemonBattlePressurePlate ------------------------

def test_battle_plate_no_pokemon(dummy_player):
    """Player without Pokemon should be blocked from battle."""
    plate = PokemonBattlePressurePlate("Charmander")
    result = plate.player_entered(dummy_player)
    assert "You don't have a Pokémon" in result[0]._get_data()["text"]
    
def test_battle_plate_fainted_pokemon(monkeypatch, dummy_player):
    """Player with a fainnted Pokemon should be blocked from battle."""
    fainted = DummyPokemon(current_hp=0)
    dummy_player.set_state("active_pokemon", fainted.to_list())

    # Patch Pokemon.from_list to return   dummy
    monkeypatch.setattr("pengumon.custom_pressure_plates.Pokemon", DummyPokemon)
    plate = PokemonBattlePressurePlate("Charmander")
    result = plate.player_entered(dummy_player)
    assert "fainted" in result[0]._get_data()["text"]
    
def test_battle_plate_sets_up_battle_manager(monkeypatch, dummy_player):
    """Test that battle manager is set up correctly."""
    dummy_player.set_state("active_pokemon", DummyPokemon(current_hp=30).to_list())

    # Fake battle manager
    dummy_battle = SimpleNamespace(
        set_selected_option=lambda opt: setattr(dummy_battle, "option", opt),
        clear_option=lambda: setattr(dummy_battle, "option", None),
        update=lambda: [],
        is_over=lambda: False
    )

    # Patch battle manager class constructor
    monkeypatch.setattr("pengumon.custom_pressure_plates.PokemonBattleManager", lambda player, name: dummy_battle)
    monkeypatch.setattr("pengumon.custom_pressure_plates.Pokemon.from_list", lambda data: DummyPokemon(current_hp=30))

    plate = PokemonBattlePressurePlate("Charmander")
    result = plate.player_entered(dummy_player)
    assert result == []
    assert dummy_player.menu is plate
    
def test_battle_plate_select_and_clear_option(monkeypatch, dummy_player):
    """Test that selecting and clearing options works as intended."""
    dummy_battle = SimpleNamespace(
        set_selected_option=lambda opt: setattr(dummy_battle, "last_option", opt),
        clear_option=lambda: setattr(dummy_battle, "last_option", None),
        update=lambda: [],
        is_over=lambda: False
    )

    dummy_player.set_state("active_pokemon", DummyPokemon(current_hp=30).to_list())
    monkeypatch.setattr("pengumon.custom_pressure_plates.PokemonBattleManager", lambda player, name: dummy_battle)
    monkeypatch.setattr("pengumon.custom_pressure_plates.Pokemon.from_list", lambda data: DummyPokemon(current_hp=30))

    plate = PokemonBattlePressurePlate("Charmander")
    plate.player_entered(dummy_player)

    # Simulate selection
    plate.select_option(dummy_player, "Attack")
    assert dummy_battle.last_option == "Attack"

    # Simulate clearing
    plate.clear_option()
    assert dummy_battle.last_option is None
    
def test_battle_plate_update_when_battle_is_none():
    """Test that update returns an empty list when battle is None."""
    plate = PokemonBattlePressurePlate("Charmander")
    assert plate.update() == []
    
# ---------------------- ChooseDifficultyPlate ------------------------

def test_difficulty_plate_initial_prompt(dummy_player):
    """Test that initial prompt is shown correctly."""
    dummy_player.set_state("enemy_ai", "medium")
    plate = ChooseDifficultyPlate()
    result = plate.player_entered(dummy_player)
    assert "Medium" in result[0]._get_data()["text"]

def test_difficulty_plate_valid_selection(dummy_player):
    """Test that valid difficulty selection updates state correctly."""
    plate = ChooseDifficultyPlate()
    result = plate.select_option(dummy_player, "Hard")
    assert "Difficulty set to Hard" in result[0]._get_data()["text"]
    assert dummy_player.get_state("enemy_ai") == "hard"

def test_difficulty_plate_invalid_selection(dummy_player):
    """Test that invalid difficulty selection shows error message."""
    plate = ChooseDifficultyPlate()
    result = plate.select_option(dummy_player, "Impossible")
    assert "Invalid" in result[0]._get_data()["text"]

# ---------------------- PotionPressurePlate ------------------------

def test_potion_plate_adds_healing_potion(dummy_player):
    """Test that healrh potion is added to bag."""
    dummy_player.set_state("bag", Bag().to_dict())
    plate = PotionPressurePlate(position=(0,0), is_revive=False)
    result = plate.player_entered(dummy_player)
    assert "added to your bag" in result[0]._get_data()["text"]

def test_potion_plate_adds_revive_potion(dummy_player):
    """Test that revive potion is added to bag."""
    dummy_player.set_state("bag", Bag().to_dict())
    plate = PotionPressurePlate(position=(0,0), is_revive=True)
    result = plate.player_entered(dummy_player)
    assert "added to your bag" in result[0]._get_data()["text"]

# ---------------------- PokeballPressurePlate ------------------------

def test_pokeball_plate_adds_pokeball(dummy_player):
    """Test that ookeball is added to bag."""
    dummy_player.set_state("bag", Bag().to_dict())
    plate = PokeballPressurePlate(position=(0,0))
    result = plate.player_entered(dummy_player)
    assert "added to your bag" in result[0]._get_data()["text"]

# ---------------------- ResetPlate ------------------------

def test_reset_plate_clears_state(dummy_player):
    """Test that reset plate clears player states."""
    dummy_player.set_state("starter_pokemon", "Charmander")
    dummy_player.set_state("bag", {"potions": {}, "pokeballs": {}, "pokemon": []})
    plate = ResetPlate()
    result = plate.player_entered(dummy_player)
    assert dummy_player.get_state("starter_pokemon") is None
    assert "reset" in result[0]._get_data()["text"]