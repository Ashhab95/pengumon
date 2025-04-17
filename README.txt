
UNIT TESTS:
    To run all unit tests, cd into pengumon directory and use the following command:

    pytest 

    This will automatically discover and run all test files (test_*.py) inside the pengumon/ directory. 
    All tests use pytest and are designed to be self-contained and reproducible.

    If you only want to run tests for a specific module, (for example, enemyAI) run:

    pytest test_enemyAI.py


RUNNING:
    If game is crashing, you may not have the version of 303MUD needed to run the game. cd into 303MUD and run:

    git pull upstream main

    This should allow you to run the game without issues.


SPECIAL KEYBINDS YOU CAN USE IN THE GAME:
    ["b"] = Shows bag contents
    ["h"] = Gives a random hint about the game
    ["v"] = Shows your current active Pokemon
    ["s"] = Allows you to switch your active Pokemon


SPECIAL PRESSURE PLATES YOU CAN USE:
    - Next to pProfessor Oak, there is a black tile with a red light in the middle.
      This is the choose difficulty plate where can manually set the difficulty of the game by stepping on it.
      The game will just use medium difficulty unless if difficulty is not set.

    - To the right of choose difficulty plate is a red plate with a gold down arrow.
      This is the reset plate where you can reset your progress in the game.
      It will clear the database of all your progress in the game.


GAME:


