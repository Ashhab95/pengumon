from enum import Enum

class PokemonType(Enum):
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"


pokedex = {
    "Charmander": {
        "name": "Charmander",
        "max_health": 50,
        "type": PokemonType.FIRE,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Scratch", "damage": 10},
            {"name": "Ember", "damage": 15},
        ]
    },
    "Squirtle": {
        "name": "Squirtle",
        "max_health": 50,
        "type": PokemonType.WATER,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Tackle", "damage": 10},
            {"name": "Water Gun", "damage": 15},
        ]
    },
    "Bulbasaur": {
        "name": "Bulbasaur",
        "max_health": 50,
        "type": PokemonType.GRASS,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Vine Whip", "damage": 12},
            {"name": "Tackle", "damage": 10},
        ]
    },
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
        ]
    },
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
    },
    "Turtwig": {
        "name": "Turtwig",
        "max_health": 50,
        "type": PokemonType.GRASS,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Tackle", "damage": 10},
            {"name": "Leafage", "damage": 15},
        ]
    },
    "Grotle": {
        "name": "Grotle",
        "max_health": 100,
        "type": PokemonType.GRASS,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Razor Leaf", "damage": 20},
            {"name": "Bite", "damage": 25},
            {"name": "Energy Ball", "damage": 30},
        ]
    },
    "Torterra": {
        "name": "Torterra",
        "max_health": 200,
        "type": PokemonType.GRASS,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Earthquake", "damage": 30},
            {"name": "Crunch", "damage": 35},
            {"name": "Giga Drain", "damage": 40},
            {"name": "Frenzy Plant", "damage": 70}
        ]
    },
    "Chimchar": {
        "name": "Chimchar",
        "max_health": 50,
        "type": PokemonType.FIRE,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Scratch", "damage": 10},
            {"name": "Fury Swipes", "damage": 15},
        ]
    },
    "Monferno": {
        "name": "Monferno",
        "max_health": 100,
        "type": PokemonType.FIRE,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Flame Wheel", "damage": 20},
            {"name": "Mach Punch", "damage": 25},
            {"name": "Fire Spin", "damage": 30},
        ]
    },
    "Infernape": {
        "name": "Infernape",
        "max_health": 200,
        "type": PokemonType.FIRE,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Close Combat", "damage": 30},
            {"name": "Fire Punch", "damage": 35},
            {"name": "Acrobatics", "damage": 40},
            {"name": "Flare Blitz", "damage": 70}
        ]
    },
    "Piplup": {
        "name": "Piplup",
        "max_health": 50,
        "type": PokemonType.WATER,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Pound", "damage": 10},
            {"name": "Bubble", "damage": 15},
        ]
    },
    "Prinplup": {
        "name": "Prinplup",
        "max_health": 100,
        "type": PokemonType.WATER,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Peck", "damage": 20},
            {"name": "Bubble Beam", "damage": 25},
            {"name": "Metal Claw", "damage": 30},
        ]
    },
    "Empoleon": {
        "name": "Empoleon",
        "max_health": 200,
        "type": PokemonType.WATER,
        "level": 1,
        "xp": 0,
        "attacks": [
            {"name": "Drill Peck", "damage": 30},
            {"name": "Surf", "damage": 35},
            {"name": "Flash Cannon", "damage": 40},
            {"name": "Hydro Cannon", "damage": 70}
        ]
    }
}
