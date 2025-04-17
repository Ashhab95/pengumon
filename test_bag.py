import pytest
from types import SimpleNamespace
from .bag import *
from .items import *
from .pokeball import *

# Dummy Pokemon class
class DummyPokemon:
    def __init__(self, name="Dummy", current_hp=30, max_hp=50, level=5, p_type="WATER"):
        self.name = name
        self.current_health = current_hp
        self.max_health = max_hp
        self.level = level
        self.p_type = SimpleNamespace(name=p_type)

    def is_fainted(self) -> bool:
        return self.current_health == 0

    def to_list(self) -> list:
        return [self.name, self.max_health, self.current_health, self.p_type.name, self.level, 0, [], "BaseEvolutionState"]

    @staticmethod
    def from_list(data):
        return DummyPokemon(name=data[0], max_hp=data[1], current_hp=data[2], p_type=data[3], level=data[4])

@pytest.fixture
def dummy_pokemon():
    return DummyPokemon()



#=============== Unit Tests ===============#

def test_potion_compartment_add_and_remove():
    """Test adding and removing various potions from compartment."""
    potions = PotionCompartment()
    potions.add(SmallPotion())
    potions.add(MediumPotion())
    potions.add(RevivePotion(SmallPotion()))
    assert potions.count() == 3
    assert isinstance(potions.remove("small"), SmallPotion)
    assert isinstance(potions.remove("medium"), MediumPotion)
    assert isinstance(potions.remove("small_revive"), RevivePotion)
    assert potions.count() == 0

def test_pokeball_compartment_add_and_remove():
    """Test adding and removing all types of Pokebals."""
    pokeballs = PokeballCompartment()
    pokeballs.add(RegularPokeball())
    pokeballs.add(GreatBall())
    pokeballs.add(UltraBall())
    pokeballs.add(MasterBall())
    assert pokeballs.count() == 4
    assert isinstance(pokeballs.remove("pokeball"), RegularPokeball)
    assert isinstance(pokeballs.remove("greatball"), GreatBall)
    assert isinstance(pokeballs.remove("ultraball"), UltraBall)
    assert isinstance(pokeballs.remove("masterball"), MasterBall)
    assert pokeballs.count() == 0

def test_pokemon_roster_add_and_list(dummy_pokemon):
    """Test adding a Pokemon to the roster and listing it."""
    roster = PokemonRoster()
    ball = RegularPokeball()
    ball.add(dummy_pokemon)
    assert roster.add(ball) is True
    assert len(roster.list_pokemon()) == 1

def test_pokemon_roster_switch(dummy_pokemon):
    """Test swapping the active Pokwmon with one in the roster."""
    roster = PokemonRoster()
    pokemon1 = DummyPokemon("A")
    pokemon2 = DummyPokemon("B")
    ball = RegularPokeball()
    ball.add(pokemon1)
    roster.add(ball)
    old = roster.switch_pokemon(pokemon2, 0)
    assert old.name == "A"
    assert ball.captured_pokemon.name == "B"

def test_bag_serialization(dummy_pokemon, monkeypatch):
    """Test serializing and deseriallizing a full bag."""
    bag = Bag()
    ball = RegularPokeball()
    ball.add(dummy_pokemon)
    bag.pokemon.add(ball)
    bag.potions.add(SmallPotion())
    bag.pokeballs.add(RegularPokeball())

    # Patch Pokemon.from_list to return dummy_pokemon
    monkeypatch.setattr("pengumon.pokemon.Pokemon.from_list", lambda data: dummy_pokemon)

    data = bag.to_dict()
    restored = Bag.from_dict(data)

    assert isinstance(restored, Bag)
    assert restored.pokemon.stored_pokemon[0].get_name() == "Dummy"
    
    
def test_item_compartment_str():
    """Test the string representation."""
    pc = PotionCompartment()
    assert str(pc) == "Potions compartment"

def test_potion_compartment_list_items():
    """Test that PotionCompartment returns correct formatted item list."""
    pc = PotionCompartment()
    pc._counts["small"] = 2
    pc._counts["medium"] = 1
    items = pc.list_items()
    assert "Small x2" in items
    assert "Medium x1" in items

def test_pokeball_compartment_list_items():
    """Test that PokeballCompartment returns correct formatted item list."""
    pb = PokeballCompartment()
    pb._counts["ultraball"] = 3
    result = pb.list_items()
    assert result == ["Ultraball x3"]

def test_pokemon_roster_remove(dummy_pokemon):
    """Test removing Pokemon from roster by index, including out-of-bounds."""
    roster = PokemonRoster()
    ball = RegularPokeball()
    roster.stored_pokemon.append(ball)
    removed = roster.remove(0)
    assert removed is ball
    assert roster.remove(99) is None

def test_pokemon_roster_full(dummy_pokemon):
    """Test that roster correctly identifies being full and rejects extra entries."""
    roster = PokemonRoster()
    for _ in range(roster.MAX_CAPACITY):
        b = RegularPokeball()
        b.add(dummy_pokemon)
        assert roster.add(b) is True
    assert roster.is_full() is True
    b = RegularPokeball()
    b.add(dummy_pokemon)
    assert roster.add(b) is False

def test_pokemon_roster_available(dummy_pokemon):
    """Test that get_available_pokemon returns only healthy pokemon."""
    roster = PokemonRoster()
    b = RegularPokeball()
    b.add(dummy_pokemon)
    roster.stored_pokemon.append(b)
    available = roster.get_available_pokemon()
    assert len(available) == 1

def test_roster_list_pokemon():
    """Test that the roster lists pokemon descriptions properly."""
    roster = PokemonRoster()
    roster.stored_pokemon.append(RegularPokeball())
    desc = roster.list_pokemon()
    assert isinstance(desc[0][1], str)

def test_roster_switch_invalid_index():
    """Test that switching pokemon with invalid index returns None."""
    roster = PokemonRoster()
    assert roster.switch_pokemon(DummyPokemon(), 5) is None

def test_potion_compartment_from_dict():
    """Test restoring potion counts from a dictionary."""
    pc = PotionCompartment()
    pc.from_dict({"small": 3, "medium": 2})
    assert pc._counts["small"] == 3
    assert pc._counts["medium"] == 2

def test_pokeball_compartment_from_dict():
    """Test restoring pokeball counts from dictionary."""
    pb = PokeballCompartment()
    pb.from_dict({"pokeball": 1, "greatball": 2})
    assert pb._counts["greatball"] == 2
    
def test_remove_nonexistent_item_returns_none():
    """Removing item that doesn't exist should return None."""
    pc = PotionCompartment()
    assert pc.remove("nonexistent") is None

def test_get_item_key_invalid_raises():
    """Passing unsupported item should raise ValueError."""
    class DummyItem(Item):
        def get_name(self): return "Test"
        def get_value(self): return 1
        def use(self, t): return True
        def to_list(self): return []
    with pytest.raises(ValueError):
        PotionCompartment().get_item_key(DummyItem())
