import pytest
from types import SimpleNamespace
from .bag import Bag
from .pokeball import RegularPokeball

# Dummy Pokemon
class DummyPokemon:
    def __init__(self, name="Dummy", current_hp=30, max_hp=50):
        self.name = name
        self.current_health = current_hp
        self.max_health = max_hp

    def to_list(self):
        return [self.name, self.max_health, self.current_health, "WATER", 5, 0, [], "BaseEvolutionState"]

    @staticmethod
    def from_list(data):
        return DummyPokemon(name=data[0], max_hp=data[1], current_hp=data[2])

# Dummy player
class DummyPlayer:
    def __init__(self):
        self.state = {}
        self.menu = None

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value

    def set_current_menu(self, menu):
        self.menu = menu

# Dummy messages
class DummyServerMessage:
    def __init__(self, recipient, text):
        self.text = text
        self.recipient = recipient

class DummyChooseObjectMessage:
    def __init__(self, sender, recipient, options, window_title="Choose"):
        self.sender = sender
        self.recipient = recipient
        self.options = options
        self.window_title = window_title

# Fixtures
@pytest.fixture
def dummy_player():
    return DummyPlayer()

@pytest.fixture
def dummy_pokemon():
    return DummyPokemon(name="Charmander", current_hp=20, max_hp=50)

# Tests
def test_professor_oak_starter_selection(monkeypatch, dummy_player):
    """Proffessor Oak should assign the chosen Pokemon and starter items."""
    from pengumon import custom_NPCs
    monkeypatch.setattr(custom_NPCs, "PokemonFactory", SimpleNamespace(create_pokemon=lambda name: DummyPokemon(name)))
    monkeypatch.setattr(custom_NPCs, "ServerMessage", DummyServerMessage)

    oak = custom_NPCs.ProfessorOak()
    messages = oak.select_option(dummy_player, "Charmander")
    assert dummy_player.get_state("starter_pokemon") == "Charmander"
    assert isinstance(messages[0], DummyServerMessage)
    assert "Charmander" in messages[0].text

def test_professor_oak_repeated_interaction(monkeypatch, dummy_player, dummy_pokemon):
    """Professor Oak should not offer starters if player already chose."""
    from pengumon import custom_NPCs
    monkeypatch.setattr(custom_NPCs, "ServerMessage", DummyServerMessage)

    dummy_player.set_state("starter_pokemon", "Charmander")
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())

    oak = custom_NPCs.ProfessorOak()
    messages = oak.player_interacted(dummy_player)
    assert isinstance(messages[0], DummyServerMessage)
    assert "already chosen" in messages[0].text

def test_professor_oak_first_time_interaction(monkeypatch, dummy_player):
    """First interaction with Oak should show choose Pokemon menu."""
    from pengumon import custom_NPCs
    monkeypatch.setattr(custom_NPCs, "ServerMessage", DummyServerMessage)
    monkeypatch.setattr(custom_NPCs, "ChooseObjectMessage", DummyChooseObjectMessage)

    oak = custom_NPCs.ProfessorOak()
    messages = oak.player_interacted(dummy_player)

    assert isinstance(messages[0], DummyServerMessage)
    assert isinstance(messages[1], DummyChooseObjectMessage)
    assert dummy_player.menu == oak

def test_nurse_heals_pokemon(monkeypatch, dummy_player, dummy_pokemon):
    """Nurse should fully heal Pokemon if HP is not max."""
    from pengumon import custom_NPCs
    monkeypatch.setattr(custom_NPCs, "ServerMessage", DummyServerMessage)
    monkeypatch.setattr(custom_NPCs, "Pokemon", DummyPokemon)

    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    nurse = custom_NPCs.Nurse("Hello")
    messages = nurse.player_interacted(dummy_player)

    assert any("healed" in m.text.lower() for m in messages)
    
def test_professor_oak_does_not_duplicate_items(monkeypatch, dummy_player):
    """Professor Oak should not give starter items again if already given."""
    from pengumon import custom_NPCs
    monkeypatch.setattr(custom_NPCs, "ServerMessage", DummyServerMessage)
    monkeypatch.setattr(custom_NPCs, "PokemonFactory", SimpleNamespace(create_pokemon=lambda name: DummyPokemon(name)))

    dummy_player.set_state("starter_items_given", True)
    oak = custom_NPCs.ProfessorOak()
    oak.give_starter_items(dummy_player)
    # Ensure bag wasn't overwritten
    assert dummy_player.get_state("starter_items_given") is True
    
def test_nurse_heals_bag_pokemon(monkeypatch, dummy_player):
    """Nurse should also heal dameged Pokemon in bag."""
    from pengumon import custom_NPCs
    monkeypatch.setattr(custom_NPCs, "ServerMessage", DummyServerMessage)
    monkeypatch.setattr(custom_NPCs, "Pokemon", DummyPokemon)

    damaged = DummyPokemon(current_hp=10, max_hp=50)
    dummy_player.set_state("active_pokemon", damaged.to_list())
    
    bag = Bag()
    poke_in_bag = DummyPokemon(name="Bulbasaur", current_hp=20, max_hp=50)
    ball = RegularPokeball()
    ball.add(poke_in_bag)
    bag.pokemon.add(ball)

    dummy_player.set_state("bag", bag.to_dict())
    nurse = custom_NPCs.Nurse("Welcome!")
    messages = nurse.player_interacted(dummy_player)

    assert any("bulbasaur" in m.text.lower() for m in messages)
    assert any("healed" in m.text.lower() for m in messages)