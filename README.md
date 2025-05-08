
## UNIT TESTS

To run all unit tests, `cd` into the `pengumon` directory and use the following command:

```bash
pytest
```

This will automatically discover and run all test files (`test_*.py`) inside the `pengumon/` directory.
All tests use `pytest` and are designed to be self-contained and reproducible.

To run tests for a specific module (e.g. `enemyAI`), use:

```bash
pytest test_enemyAI.py
```

---

## RUNNING

If the game crashes, it may be due to an outdated version of `303MUD`. To ensure compatibility, navigate to the `303MUD` directory and run:

```bash
git pull upstream main
```

Note: We found that origin/main was too far behind for much of the time we were coding. 
This fix should ensure compatibility and allow the game to run correctly. 

---

## CLASS DIAGRAM

You can find it under classdiagram.png

---

## MAP

- Located in myhouse.py

---

## SPECIAL KEYBINDS

- `b` — View bag contents
- `h` — Get a random hint about the game
- `v` — View your active Pokémon and its stats
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
  - Attacking (uses one of 2 ~ 4 preset moves per Pokémon)
  - Using an item (e.g. health potions or Pokeballs)
  - Run (running away from the fight, you fail to run away 30% of the time)
  - Dodging (gives you a 50% chance to dodge next enemy turn attack)
  - Switching Pokémon (uses a turn)
- You win when you defeat the opponent AI pokemon, or catch them

### Enemy AI

- Makes decisions based on difficulty level and predefined strategies.

### Type Advantages

- Type effectiveness applies:
  - Fire > Grass
  - Grass > Water
  - Water > Fire

### Progression

- Pokémon gain XP by defeating enemy Pokémon. (catching them won't give you XP)
  - XP gained from defeating enemy Pokémom scales with enemy evolution.
- You can also catch enemy Pokémon using a Pokeball.
  - Using a Pokeball will not always catch enemy Pokémon. (e.g. the opponent needs to be low health)
  - Some Pokeballs have a greater chance of catching than others.
  - If you fail to catch the Pokémon, you still lose the Pokeball, so make sure it's at low health!!!
- Pokémon level up and evolve once specific thresholds are reached.

### Healing & Recovery

- The **Pokémon Center** is a healing station where all your Pokémon are fully restored.
- To heal all your Pokemon, simply go to the **Pokemon Center** and talk with Nurse Joy.

---
## 📸 Screenshots

### 🌳 Game Map View  
![Map View](stock%20images/test-1.png)

### 🏥 Pokémon Center Interaction  
![Pokémon Center](stock%20images/test-2.png)

### ⚔️ Battle System  
![Battle](stock%20images/test-3.png)

### 🔄 Starter Pokémon Selection  
![Choose Starter](stock%20images/test-4.png)

### 🎮 Pressure Plate & Movement  
![Pressure Plate](stock%20images/test-5.png)

