import pytest
from unittest.mock import MagicMock
from .custom_keybinds import get_keybinds
from typing import List, Tuple, Dict, Union, Any

from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from tiles.buildings import Building

class DummyPokemon:
    def __init__(self, name: str = "Dummy", level: int = 5, current_hp: int = 30, max_hp: int = 50, p_type: str = "WATER", xp: int = 10):
        self.name = name
        self.level = level
        self.current_health = current_hp
        self.max_health = max_hp
        self.p_type = type("DummyType", (), {"name": p_type})()
        self.xp = xp
        self.evolution_state = type("DummyEvoState", (), {"get_evo_level": lambda s: 1})()
        self.known_attacks: List[Dict[str, Union[str, int]]] = [
            {"name": "Splash", "damage": 5},
            {"name": "Tackle", "damage": 10},
        ]

    def to_list(self) -> List[Union[str, int, List[Dict[str, Union[str, int]]]]]:
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


class DummyPokeball:
    def __init__(self, pokemon: DummyPokemon):
        self.pokemon = pokemon

    def is_empty(self) -> bool:
        return False

    def get_name(self) -> str:
        return self.pokemon.name

    def get_health(self) -> str:
        return f"{self.pokemon.current_health}/{self.pokemon.max_health}"

    def get_level(self) -> str:
        return str(self.pokemon.level)

    def get_type(self) -> str:
        return self.pokemon.p_type.name

    def is_pokemon_fainted(self) -> bool:
        return self.pokemon.current_health == 0

    def switch_pokemon(self, _: DummyPokemon) -> DummyPokemon:
        return self.pokemon


class DummyPokemonRoster:
    def __init__(self, pokeballs: List[DummyPokeball]):
        self.stored_pokemon = pokeballs

    def get_available_pokemon(self) -> List[Tuple[int, DummyPokeball]]:
        return [(i, ball) for i, ball in enumerate(self.stored_pokemon)]

    def switch_pokemon(self, _: DummyPokemon, index: int) -> DummyPokemon:
        return self.stored_pokemon[index].pokemon

    def to_list(self) -> List[List[Union[str, int, List[Dict[str, Union[str, int]]]]]]:
        return [ball.pokemon.to_list() for ball in self.stored_pokemon]


class DummyBag:
    def __init__(self, pokeballs: List[DummyPokeball] = None):
        pokeballs = pokeballs or []
        self.pokemon = DummyPokemonRoster(pokeballs)
        self.potions = type("DummyPotions", (), {
            "_get_counts": lambda s: {"small": 1}
        })()
        self.pokeballs = type("DummyPokeballs", (), {
            "_get_counts": lambda s: {"pokeball": len(pokeballs)}
        })()

    def to_dict(self) -> Dict[str, List[List[Union[str, int, List[Dict[str, Union[str, int]]]]]]]:
        return {"pokemon": self.pokemon.to_list()}

    
        
        

@pytest.fixture
def mock_player():
    player = MagicMock()
    player.get_state = MagicMock()
    player.set_state = MagicMock()
    player.set_current_menu = MagicMock()
    return player

@pytest.fixture
def keybinds():
    return get_keybinds(MagicMock())

def test_view_active_pokemon_with_data(mock_player, keybinds):
    """Test displaying stats for a valid active Pokemon."""
    charmander = DummyPokemon("Charmander")
    mock_player.get_state.return_value = charmander.to_list()
    messages = keybinds["v"](mock_player)
    assert len(messages) == 1
    assert isinstance(messages[0], DisplayStatsMessage)
    assert "Charmander" in "\n".join(messages[0]._get_data()['stats'])

def test_view_active_pokemon_no_data(mock_player, keybinds):
    """Test behavior when no active Pokemon is set."""
    mock_player.get_state.return_value = None
    messages = keybinds["v"](mock_player)
    assert len(messages) == 1
    assert isinstance(messages[0], ServerMessage)
    assert "No active" in messages[0]._get_data()["text"]

def test_give_hint_structure(mock_player, keybinds):
    """Test hint message format and structure."""
    messages = keybinds["h"](mock_player)
    assert len(messages) == 1
    assert isinstance(messages[0], DisplayStatsMessage)
    stats = messages[0]._get_data()['stats']
    assert isinstance(stats, list)
    assert len(stats) == 2

def test_switch_active_pokemon_no_bag(mock_player, keybinds):
    """Test switch menu behavior when player has no bag yet."""
    mock_player.get_state.return_value = None
    messages = keybinds["s"](mock_player)
    assert len(messages) == 1
    assert isinstance(messages[0], ServerMessage)
    assert "don't have a bag" in messages[0]._get_data()["text"]

def test_switch_active_pokemon_no_available(mock_player, keybinds):
    """Test switch menu behevior when player has no healthy Pokemon."""
    empty_bag = DummyBag([])
    mock_player.get_state.side_effect = [empty_bag.to_dict()]
    messages = keybinds["s"](mock_player)
    assert len(messages) == 1
    assert isinstance(messages[0], ServerMessage)
    assert "don't have any healthy" in messages[0]._get_data()["text"]

def test_switch_active_pokemon_available(mock_player, keybinds):
    """Test full switch menu interaction when at least one healthy Pokemon exists."""
    squirtle = DummyPokemon("Squirtle")
    ball = DummyPokeball(squirtle)
    bag = DummyBag([ball])
    mock_player.get_state.side_effect = [bag.to_dict()]
    messages = keybinds["s"](mock_player)
    assert len(messages) == 2
    assert isinstance(messages[0], ServerMessage)
    assert isinstance(messages[1], OptionsMessage)
    assert any("Squirtle" in opt for opt in messages[1]._get_data()['options'])

def test_show_bag_contents(mock_player, keybinds):
    """Test showing bag contents including potions and Pokeballs."""
    bulbasaur = DummyPokemon("Bulbasaur")
    ball = DummyPokeball(bulbasaur)
    bag = DummyBag([ball])
    mock_player.get_state.return_value = bag.to_dict()
    messages = keybinds["b"](mock_player)
    assert len(messages) == 1
    assert isinstance(messages[0], DisplayStatsMessage)
    lines = messages[0]._get_data()['stats']
    assert any("Pokéball" in line or "Potion" in line for line in lines)
