import pytest
from .items import *

class DummyPokemon:
    def __init__(self, name: str = "Dummy", level: int = 3, current_hp: int = 30, max_hp: int = 50, p_type: str = "WATER", xp: int = 10):
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

    def is_fainted(self) -> bool:
        return self.current_health == 0

def test_small_potion_use():
    """SmallPotion should heal a non-fainted Pokemon."""
    potion = SmallPotion()
    pokemon = DummyPokemon(current_hp=30, max_hp=50)
    result = potion.use(pokemon)
    assert result is True
    assert pokemon.current_health == 40

def test_small_potion_full_health():
    """Using a potion on a fuly healed Pokemon should fail."""
    potion = SmallPotion()
    pokemon = DummyPokemon(current_hp=50, max_hp=50)
    result = potion.use(pokemon)
    assert result is False

def test_small_potion_on_fainted():
    """Potion should not heal a fainted Pokemon."""
    potion = SmallPotion()
    pokemon = DummyPokemon(current_hp=0, max_hp=50)
    result = potion.use(pokemon)
    assert result is False

def test_large_potion_caps_to_max():
    """LargePotion should not overheal a Pokemon beyond max HP."""
    potion = LargePotion()
    pokemon = DummyPokemon(current_hp=45, max_hp=50)
    result = potion.use(pokemon)
    assert result is True
    assert pokemon.current_health == 50

def test_revive_potion_revives_and_heals():
    """RevivePotion should revive fainted Pokemon and apply healing."""
    revive = RevivePotion(SmallPotion())
    pokemon = DummyPokemon(current_hp=0, max_hp=50)
    result = revive.use(pokemon)
    assert result is True
    assert pokemon.current_health > 1

def test_revive_potion_on_non_fainted():
    """RevivePotion behaves as normal potion if Pokemon is not fainted."""
    revive = RevivePotion(SmallPotion())
    pokemon = DummyPokemon(current_hp=10, max_hp=50)
    result = revive.use(pokemon)
    assert result is True
    assert pokemon.current_health == 20

def test_revive_potion_serialization():
    """Test serialization and deserialization of revive potion."""
    revive = RevivePotion(SmallPotion())
    data = revive.to_list()
    new_potion = RevivePotion.from_list(data)
    assert isinstance(new_potion, RevivePotion)
    assert new_potion.get_name() == "Revive Small Potion"

def test_flyweight_reuse():
    """Flyweight factery should reuse potion instances."""
    a = PotionFlyweightFactory.get_small_potion()
    b = PotionFlyweightFactory.get_potion("small potion")
    assert a is b

def test_flyweight_revive_medium():
    """Flyweight factory should return revive potion instance correctly."""
    revive = PotionFlyweightFactory.get_revive_medium_potion()
    assert isinstance(revive, RevivePotion)
    assert revive.get_name() == "Revive Medium Potion"