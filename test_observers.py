import pytest
from pengumon.observers import BattleMessageNotifier

from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from tiles.buildings import Building

# Dummy classes for testing
class DummyPlayer:
    def __init__(self, name="TestPlayer"):
        self.name = name

class DummyPokemon:
    def __init__(self, name="Mewtwo"): # mewtwo is a legendary pokemon but is not in our game, just a dummy
        self.name = name

@pytest.fixture
def dummy_player():
    return DummyPlayer()

@pytest.fixture
def dummy_pokemon():
    return DummyPokemon()

@pytest.fixture
def message_buffer():
    return []

def test_battle_message_notifier_damage(dummy_player, dummy_pokemon, message_buffer):
    """Test that damage triggers a message."""
    observer = BattleMessageNotifier(dummy_player, message_buffer)
    observer.on_health_changed(dummy_pokemon, 100, 75)
    assert len(message_buffer) == 1
    assert "took damage" in message_buffer[0]._get_data()["text"]

def test_battle_message_notifier_heal(dummy_player, dummy_pokemon, message_buffer):
    """Test that healing triggers a message."""
    observer = BattleMessageNotifier(dummy_player, message_buffer)
    observer.on_health_changed(dummy_pokemon, 40, 60)
    assert len(message_buffer) == 1
    assert "was healed" in message_buffer[0]._get_data()["text"]

def test_battle_message_notifier_no_change(dummy_player, dummy_pokemon, message_buffer):
    """Test that no message is sent if health doesn't change."""
    observer = BattleMessageNotifier(dummy_player, message_buffer)
    observer.on_health_changed(dummy_pokemon, 80, 80)
    assert len(message_buffer) == 0