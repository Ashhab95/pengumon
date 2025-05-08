import pytest
from types import SimpleNamespace
from .battle_manager import *
from .bag import Bag
from .pokemon import PokemonFactory
from .pokeball import *
from .items import *
from .observers import BattleMessageNotifier

# ---------- Dummy Classes ----------

class DummyPokemon:
    def __init__(self, name="Dummy", current_hp=30, max_hp=50, level=5, attacks=None):
        self.name = name
        self.current_health = current_hp
        self.max_health = max_hp
        self.level = level
        self.known_attacks = attacks if attacks is not None else [{"name": "DummyAttack", "damage": 1}]
        self._observers = []
        self.p_type = SimpleNamespace(name="WATER")
        
    def attack(self, index, target):
        old_hp = target.current_health
        damage = self.known_attacks[index]["damage"]
        target.current_health = max(0, old_hp - damage)

        # Notify observers of health change
        for obs in target._observers:
            obs.on_health_changed(target, old_hp, target.current_health)

        return {
            "message": f"{self.name} used {self.known_attacks[index]['name']} for {damage} damage!",
            "damage": damage,
            "evolved": None
        }

    def is_fainted(self):
        return self.current_health <= 0

    def to_list(self):
        return [
            self.name,
            self.max_health,
            self.current_health,
            self.p_type.name,
            self.level,
            0,
            self.known_attacks,
            "BaseEvolutionState"
        ]

    @staticmethod
    def from_list(data):
        name, max_hp, current_hp, type_name, level, _, attacks, _ = data
        return DummyPokemon(name=name, max_hp=max_hp, current_hp=current_hp, level=level, attacks=attacks)

    def add_observer(self, observer):
        self._observers.append(observer)

class DummyPlayer:
    def __init__(self):
        self.state = {}
        self.name = "Ash"

    def set_state(self, key, value):
        self.state[key] = value

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_current_menu(self, menu):
        pass

    def get_name(self):
        return self.name

# ---------- Fixtures ----------

@pytest.fixture
def dummy_player():
    return DummyPlayer()

@pytest.fixture
def dummy_pokemon():
    return DummyPokemon()





# --- Battle Initialization ---

def test_intro_stage_generates_correct_messages(dummy_player, dummy_pokemon, monkeypatch):
    """Test that the intro stage generates the correct messages."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())

    # Patch things to avoid actual game logic
    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon.from_list", lambda data: dummy_pokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    messages = manager.update() # intro stage
    assert any("You encountered a wild" in msg._get_data()["text"] for msg in messages)
    
def test_clear_option_resets_value(monkeypatch, dummy_player, dummy_pokemon):
    """Test that clear_option resets the selected option."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())
    
    # Patch things to avoid actual game logic
    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.set_selected_option("Dodge")
    assert manager._PokemonBattleManager__current_option == "Dodge"
    manager.clear_option()
    assert manager._PokemonBattleManager__current_option is None
    





# --- Player Turn: Action Options ---
      
def test_player_turn_options_include_attacks_and_utilities(monkeypatch, dummy_player, dummy_pokemon):
    """Ensure that player turn presents attack, dodge, run, and bag options."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())

    # Patch things to avoid actual game logic
    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # progress to PLAYER_TURN
    options = manager.update()  # manager transitions to AWAIT_INPUT and returns option messages

    # Finding OptionsMessage
    opts_msg = next((m for m in options if isinstance(m, OptionsMessage)), None)
    assert opts_msg is not None, "Expected an OptionsMessage"
    data = opts_msg._get_data()

    choices = data["options"]
    assert any("Dodge" in o for o in choices)
    assert any("Run" in o for o in choices)
    assert any("Bag" in o for o in choices)
    assert any("0:" in o for o in choices)  # there should be at least one attack option
    
def test_player_turn_shows_switch_when_roster_available(monkeypatch, dummy_player, dummy_pokemon):
    """Ensure that player turn shows switch option when roster is available."""
    bag = Bag()
    ball = RegularPokeball()
    ball.captured_pokemon = DummyPokemon(name="Switchy")
    bag.pokemon.add(ball)

    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", bag.to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.bag.Pokemon", DummyPokemon) 

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  
    messages = manager.update()  

    opts_msg = next((m for m in messages if isinstance(m, OptionsMessage)), None)
    assert opts_msg is not None
    options = opts_msg._get_data()["options"]
    assert "Switch Pokemon" in options
    
    




# --- Bag Interaction ---

def test_bag_option_with_empty_bag(monkeypatch, dummy_player, dummy_pokemon):
    """Test that selecting Bag with an empty bag shows appropriate message."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    manager.set_selected_option("Bag")
    messages = manager.update()  # bag interaction

    assert any("bag is empty" in m._get_data()["text"].lower() for m in messages)
    assert manager._PokemonBattleManager__turn_stage == TurnStage.PLAYER_TURN
    
def test_successful_potion_use(monkeypatch, dummy_player, dummy_pokemon):
    """Test that using a potion successfully heals the Pokemon."""
    dummy_pokemon.current_health = 20  # simulate damage
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())

    bag = Bag()
    potion = SmallPotion()  
    bag.potions.add(potion)
    dummy_player.set_state("bag", bag.to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    manager.set_selected_option("Bag")
    manager.update()  # open bag
    manager.set_selected_option("Potion: Small") # simulate selecting potion
    messages = manager.update()

    assert any("was healed" in m._get_data()["text"] for m in messages)
    
def test_return_from_bag_menu(monkeypatch, dummy_player, dummy_pokemon):
    """Player selects 'Return' from Bag menu and is sent back to PLAYER_TURN."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())

    # Add an item so bag menu shows
    bag = Bag()
    bag.potions.add(SmallPotion())  # allows entering AWAIT_BAG
    dummy_player.set_state("bag", bag.to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    manager.set_selected_option("Bag")
    manager.update()  # open bag
    manager.set_selected_option("Return") # simulate selecting return
    messages = manager.update()

    assert any(
        isinstance(m, ServerMessage) and "Returning" in m._get_data()["text"]
        for m in messages
    )
    
def test_revive_potion_used_on_end(monkeypatch, dummy_player, dummy_pokemon):
    """
    Test that a RevivePotion is automatically used during END stage if active Pokemon has fainted.

    Expected behavior:
    - The RevivePotion should revive the fainted Pokémon.
    - A message should indicate the revival.
    - The battle should continue with the enemy's turn (ENEMY_WAIT).
    """

    dummy_pokemon.current_health = 0 # simulate fainted state
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())

    # set up bag withg a RevivePotion
    revive = RevivePotion(SmallPotion())
    bag = Bag()
    bag.potions.add(revive)
    dummy_player.set_state("bag", bag.to_dict())

    # Patching
    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon.from_list", lambda data: dummy_pokemon)

    # Initialize manager and set turn stage to END
    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager._PokemonBattleManager__turn_stage = TurnStage.END

    messages = manager.update() # this should trigger revive logic
    
    assert any("revived" in m._get_data()["text"].lower() for m in messages)
    assert manager._PokemonBattleManager__turn_stage == TurnStage.ENEMY_WAIT
    
    
    
    

# --- Dodge & Run ---
    
def test_player_dodge_successfully_avoids_enemy_attack(monkeypatch, dummy_player, dummy_pokemon):
    """Player selects dodge, enemy attacks, but dodge succeeds and avoids damage."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())
    dummy_player.set_state("enemy_ai", "medium")

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.battle_manager.MediumAI.choose_action", lambda self, e, p: "0")
    monkeypatch.setattr("random.random", lambda: 0.1)  # ensure dodge succeeds

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    manager.set_selected_option("Dodge")
    manager.update()  # process dodge
    manager._PokemonBattleManager__last_action_time -= ENEMY_RESPONSE_TIME
    manager.update()  # enemy turn
    messages = manager.update()

    assert any("dodged" in m._get_data()["text"].lower() for m in messages), "Expected a dodge message."
    
def test_player_dodge_fails_and_takes_damage(monkeypatch, dummy_player, dummy_pokemon):
    """Player tries to dodge, but dodge fails and they get hit by enemy attack."""
    dummy_pokemon.current_health = 50
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())
    dummy_player.set_state("enemy_ai", "medium")

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.battle_manager.MediumAI.choose_action", lambda self, e, p: "0")  # enemy attacks
    monkeypatch.setattr("random.random", lambda: 0.9)  # dodge fails (> 0.5)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # into
    manager.update()  # player turn

    manager.set_selected_option("Dodge")
    manager.update()
    manager._PokemonBattleManager__last_action_time -= ENEMY_RESPONSE_TIME
    manager.update()  # enemy turn
    messages = manager.update()

    # Expect a message saying dodge failed or showing damage taken
    text_messages = [m._get_data()["text"] for m in messages if isinstance(m, ServerMessage)]
    assert any("dodge failed" in t.lower() or "took" in t.lower() for t in text_messages), "Expected damage or dodge failure message."
    
def test_successful_run_ends_battle(monkeypatch, dummy_player, dummy_pokemon):
    """Player runs successfully from battle and ends it."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("random.random", lambda: 0.5)  # success when < 0.7

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    manager.set_selected_option("Run")
    messages = manager.update()

    assert any("ran away" in m._get_data()["text"].lower() for m in messages)
    assert manager._PokemonBattleManager__turn_stage == TurnStage.END
    
def test_failed_run_triggers_enemy_turn(monkeypatch, dummy_player, dummy_pokemon):
    """Player fails to run and the game advances to enemy's turn."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("random.random", lambda: 0.9)  # fail when > 0.7

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # into
    manager.update()  # player turn

    manager.set_selected_option("Run")
    messages = manager.update()

    assert any("couldn't escape" in m._get_data()["text"].lower() for m in messages)
    assert manager._PokemonBattleManager__turn_stage == TurnStage.ENEMY_WAIT
    
    
    
    

# --- Pokemon Switching ---
    
def test_switch_pokemon_shows_options_and_switches_successfully(monkeypatch, dummy_player, dummy_pokemon):
    """Player chooses to switch and selects another Pokemon successfully."""
    # Create a second Pokemon to switch to
    second_pokemon = DummyPokemon(name="Squirtle", current_hp=40)

    # Setup player roster with a second Pokemon
    bag = Bag()
    ball = RegularPokeball()
    ball.captured_pokemon = second_pokemon
    bag.pokemon.add(ball)

    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", bag.to_dict())
    dummy_player.set_state("enemy_ai", "easy")

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.bag.Pokemon", DummyPokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    manager.set_selected_option("Switch Pokemon") # simulate selecting switch
    switch_menu = manager.update()

    # Finging OptionsMessage
    opts_msg = next((m for m in switch_menu if isinstance(m, OptionsMessage)), None)
    assert opts_msg is not None
    switch_label = next(o for o in opts_msg._get_data()["options"] if "HP" in o and "Return" not in o)

    manager.set_selected_option(switch_label)
    confirm_msgs = manager.update()

    # Should see a message about switching
    assert any("switched to" in m._get_data()["text"].lower() for m in confirm_msgs)

    # Check the new active Pokemon
    active = manager.get_player_pokemon()
    assert active.name == "Squirtle"

def test_return_from_switch_menu(monkeypatch, dummy_player, dummy_pokemon):
    """Player selects 'Return' from the Switch Pokemon menu and is sent back to PLAYER_TURN."""
    # Create a second Pokemon to switch to
    second_pokemon = DummyPokemon(name="Squirtle", current_hp=40)

    # Setup player roster with a second Pokemon
    bag = Bag()
    ball = RegularPokeball()
    ball.captured_pokemon = second_pokemon
    bag.pokemon.add(ball)

    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", bag.to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon.from_list", lambda data: dummy_pokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    manager.set_selected_option("Switch Pokemon") # simulate selecting switch
    manager.update()  # opens switch menu

    manager.set_selected_option("Return") # simulate selecting return
    messages = manager.update()

    assert any(
        isinstance(m, ServerMessage) and "Returning" in m._get_data()["text"]
        for m in messages
    )
    assert manager._PokemonBattleManager__turn_stage == TurnStage.PLAYER_TURN
    
    
    
    
    
# --- Player Pokemon Faints ---   
    
def test_player_pokemon_faints_and_is_revived(monkeypatch, dummy_player, dummy_pokemon):
    """Test that a RevivePotion is used when the active pokemon faints."""
    dummy_pokemon.current_health = 0  # simulate fainted state
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    
    bag = Bag()
    revive = RevivePotion(SmallPotion())
    bag.potions.add(revive)
    dummy_player.set_state("bag", bag.to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    
    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager._PokemonBattleManager__turn_stage = TurnStage.END
    messages = manager.update()

    assert any("revived" in m._get_data()["text"].lower() for m in messages)
    assert manager._PokemonBattleManager__turn_stage == TurnStage.ENEMY_WAIT

def test_player_pokemon_faints_and_switches(monkeypatch, dummy_player, dummy_pokemon):
    """Test that if active pokemon faints, game switches to a backup Pokemon."""
    dummy_pokemon.current_health = 0 # simulate fainted state
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())

    # Set up a Bag with a backup Pokemon
    bag = Bag()
    ball = RegularPokeball()
    backup = DummyPokemon(name="Squirtle", current_hp=30)
    ball.captured_pokemon = backup
    bag.pokemon.add(ball)
    dummy_player.set_state("bag", bag.to_dict())

    # Patching
    dummy_from_list = lambda data: DummyPokemon(name=data[0], max_hp=data[1], current_hp=data[2])
    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon.from_list", dummy_from_list)
    monkeypatch.setattr("pengumon.bag.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.bag.Pokemon.from_list", dummy_from_list)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager._PokemonBattleManager__turn_stage = TurnStage.END
    messages = manager.update()

    assert any(
        isinstance(m, ServerMessage) and "switching to squirtle" in m._get_data()["text"].lower()
        for m in messages
    )
    assert manager._PokemonBattleManager__turn_stage == TurnStage.PLAYER_TURN
    
def test_player_pokemon_faints_no_backup(monkeypatch, dummy_player, dummy_pokemon):
    """Test that if active pkokemon faints and player has no revives or backups, battle ends."""
    dummy_pokemon.current_health = 0
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())  # no revive or backups

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager._PokemonBattleManager__turn_stage = TurnStage.END
    messages = manager.update()

    assert any(isinstance(m, PokemonBattleMessage) and m._get_data().get("destroy") for m in messages)
    assert manager.is_over()





# --- Enemy Pokemon Faints ---

def test_enemy_pokemon_faints(monkeypatch, dummy_player, dummy_pokemon):
    """Test that if enemy pokemon faints, battle ends."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())

    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: dummy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon.from_list", lambda data: dummy_pokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    # Simulate attack that knocks out the enemy
    manager.set_selected_option("0: DummyAttack (20)")
    manager._PokemonBattleManager__enemy_pokemon.current_health = 10
    dummy_pokemon.attack = lambda idx, target: {"message": "used DummyAttack!", "damage": 10}
    manager._PokemonBattleManager__enemy_pokemon.is_fainted = lambda: True

    messages = manager.update()
    assert any(
        isinstance(m, ServerMessage) and "has fainted" in m._get_data()["text"].lower()
        for m in messages
    )
    assert manager._PokemonBattleManager__turn_stage == TurnStage.END
    

    
    
    
# --- Observers and Messaging ---

def test_observer_sends_battle_message(monkeypatch, dummy_player, dummy_pokemon):
    """Test that observer sends a ServerMessage when damage is dealt."""
    dummy_player.set_state("active_pokemon", dummy_pokemon.to_list())
    dummy_player.set_state("bag", Bag().to_dict())

    # Set up enemy dummy
    enemy_pokemon = DummyPokemon(name="Enemy", current_hp=50, max_hp=50)

    # Patching
    monkeypatch.setattr("pengumon.battle_manager.PokemonFactory.create_pokemon", lambda name: enemy_pokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon", DummyPokemon)
    monkeypatch.setattr("pengumon.battle_manager.Pokemon.from_list", lambda data: dummy_pokemon)

    manager = PokemonBattleManager(dummy_player, "Charmander")
    manager.update()  # intro
    manager.update()  # player turn

    # Set up player attack
    manager.set_selected_option("0: DummyAttack (1)") 
    messages = manager.update()  # process attack
    messages += manager.update()  # flush observer messages

    # Look for damage message sent by the observer
    assert any(
        isinstance(m, ServerMessage) and "took damage" in m._get_data()["text"].lower()
        for m in messages
    )

