
## UNIT TESTS

To run all unit tests, `cd` into the `pengumon` directory and use the following command:

```bash
pytest
```

This will automatically discover and run all test files (`test_*.py`) inside the `pengumon/` directory.
All tests use `pytest` and are designed to be self-contained and reproducible.

To run tests for a specific module (e.g., `enemyAI`), use:

```bash
pytest test_enemyAI.py
```

---

## RUNNING

If the game crashes, you may not have the required version of `303MUD`. To fix this, `cd` into the `303MUD` directory and run:

```bash
git pull upstream main
```

This should ensure compatibility and allow the game to run correctly.

---

## SPECIAL KEYBINDS

- `b` — View bag contents
- `h` — Get a random hint about the game
- `v` — View your current active Pokémon
- `s` — Switch your active Pokémon

---

## SPECIAL PRESSURE PLATES

- **Choose Difficulty Plate**: Located next to Professor Oak. It's a black tile with a red light. Step on it to set the game difficulty manually (default is Medium).
- **Reset Plate**: Located to the right of the difficulty plate. It's a red tile with a gold down arrow. Step on it to reset your game progress. This clears your progress from the database.

---

## GAME MECHANICS

### Battle System

- Turn-based: You and your opponent AI alternate actions each round.
- Player actions include:
  - Attacking (uses one of four preset moves per Pokémon)
  - Using an item (e.g., health or revive potions)
  - Switching Pokémon (uses a turn unless a special item is used)
  - Attempting to catch wild Pokémon
- You win when you defeat the opponent AI pokemon, or catch them

### Enemy AI

- Makes decisions based on difficulty level and predefined strategies.

### Battle Flow

- Health bars are updated after each move using observer logic.
- Type effectiveness applies:
  - Fire > Grass
  - Grass > Water
  - Water > Fire

### Progression

- Pokémon gain XP from battles.
- They level up and evolve once specific thresholds are reached.

### Healing & Recovery

- The **Pokémon Center** is a healing station where all your Pokémon are fully restored.
- To heal all your Pokemon, simply go to the **Pokemon Center** and talk with Nurse Joy. 
