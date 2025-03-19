from enum import Enum

class PokemonType(Enum):
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"


pokedex = {
    "Charmander": {
        "name": "Charmander",
        "max_health": 40,
        "type": PokemonType.FIRE,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Scratch", "damage": 10},
            {"name": "Ember", "damage": 15},
            {"name": "Flame Tail", "damage": 20},
            {"name": "Flamethrower", "damage": 25}
        ]
    },
    "Squirtle": {
        "name": "Squirtle",
        "max_health": 40,
        "type": PokemonType.WATER,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Tackle", "damage": 10},
            {"name": "Water Gun", "damage": 15},
            {"name": "Bubble", "damage": 20},
            {"name": "Aqua Tail", "damage": 25}
        ]
    },
    "Bulbasaur": {
        "name": "Bulbasaur",
        "max_health": 40,
        "type": PokemonType.GRASS,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Vine Whip", "damage": 12},
            {"name": "Tackle", "damage": 10},
            {"name": "Razor Leaf", "damage": 18},
            {"name": "Solar Beam", "damage": 25}
        ]
    },
    # Evolved Forms
    "Charmeleon": {
        "name": "Charmeleon",
        "max_health": 100,
        "type": PokemonType.FIRE,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Slash", "damage": 20},
            {"name": "Fire Fang", "damage": 25},
            {"name": "Flamethrower", "damage": 30},
            {"name": "Fire Blast", "damage": 40}
        ]
    },
    "Wartortle": {
        "name": "Wartortle",
        "max_health": 100,
        "type": PokemonType.WATER,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Bite", "damage": 20},
            {"name": "Water Pulse", "damage": 25},
            {"name": "Hydro Pump", "damage": 30},
            {"name": "Skull Bash", "damage": 40}
        ]
    },
    "Ivysaur": {
        "name": "Ivysaur",
        "max_health": 100,
        "type": PokemonType.GRASS,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Seed Bomb", "damage": 20},
            {"name": "Razor Leaf", "damage": 25},
            {"name": "Solar Beam", "damage": 30},
            {"name": "Petal Dance", "damage": 40}
        ]
    },

    #final form 
    
     "Charizard": {
        "name": "Charizard",
        "max_health": 200,
        "type": PokemonType.FIRE,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Wing Attack", "damage": 30},
            {"name": "Fire Spin", "damage": 35},
            {"name": "Flamethrower", "damage": 40},
            {"name": "Inferno", "damage": 70}
        ]
    },
    "Blastoise": {
        "name": "Blastoise",
        "max_health": 200,
        "type": PokemonType.WATER,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Water Pulse", "damage": 30},
            {"name": "Hydro Pump", "damage": 35},
            {"name": "Skull Bash", "damage": 40},
            {"name": "Hydro Cannon", "damage": 70}
        ]
    },
    "Venusaur": {
        "name": "Venusaur",
        "max_health": 200,
        "type": PokemonType.GRASS,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Seed Bomb", "damage": 30},
            {"name": "Solar Beam", "damage": 35},
            {"name": "Petal Blizzard", "damage": 40},
            {"name": "Frenzy Plant", "damage": 70}
        ]
    }
}


