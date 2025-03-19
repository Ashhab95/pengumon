# Pokemon.py
from pokedex import pokedex, PokemonType

# Abstract Component interface
class BasePokemon:
    def is_fainted(self):
        pass
    
    def take_damage(self, damage):
        pass
    
    def attack(self, attack_index, target):
        pass
    
    def level_up_check(self):
        pass

# Concrete Component
class Pokemon(BasePokemon):
    def __init__(self, name):
        data = pokedex.get(name)
        if not data:
            raise ValueError(f"{name} not found in the Pokedex.")

        self.name = data['name']
        self.max_health = int(data['max_health'])
        self.current_health = self.max_health
        self.p_type = data['type']
        self.level = int(data['level'])
        self.xp = int(data['xp'])
        self.all_attacks = data['attacks']
        self.known_attacks = self.all_attacks[:]

    def is_fainted(self):
        return self.current_health <= 0

    def take_damage(self, damage):
        self.current_health -= damage
        if self.current_health < 0:
            self.current_health = 0

    def attack(self, attack_index, target):
        if self.is_fainted():
            return {"success": False, "message": f"{self.name} is fainted and cannot attack!"}

        attack = self.known_attacks[attack_index]
        base_damage = attack["damage"]

        multiplier = 1.0
        if self.p_type == PokemonType.FIRE and target.p_type == PokemonType.GRASS:
            multiplier = 1.4
        elif self.p_type == PokemonType.WATER and target.p_type == PokemonType.FIRE:
            multiplier = 1.4
        elif self.p_type == PokemonType.GRASS and target.p_type == PokemonType.WATER:
            multiplier = 1.4
        elif self.p_type == target.p_type:
            multiplier = 1.0

        final_damage = int(base_damage * multiplier)
        target.take_damage(final_damage)

        result = {
            "success": True,
            "message": f"{self.name} used {attack['name']} on {target.name}!",
            "damage": final_damage,
            "target_fainted": target.is_fainted(),
            "evolved": None
        }

        if target.is_fainted():
            self.xp += 10
            evolved = self.level_up_check()
            if evolved:
                result["evolved"] = evolved
        return result

    def level_up_check(self):
        if self.xp >= 30:
            self.xp = 0
            self.level += 1
            if self.level < 4:
                self.max_health += 10
                self.current_health = self.max_health
                for attack in self.known_attacks:
                    attack["damage"] += 5
            elif self.level == 4:
                if self.name == "Charmander":
                    return PokeEvolve2(self, "Charmeleon")
                elif self.name == "Squirtle":
                    return PokeEvolve2(self, "Wartortle")
                elif self.name == "Bulbasaur":
                    return PokeEvolve2(self, "Ivysaur")
        return None

# Base Decorator class
class PokemonDecorator(BasePokemon):
    def __init__(self, base_pokemon):
        self.base = base_pokemon


# Concrete Decorators
class PokeEvolve2(PokemonDecorator):
    def __init__(self, base_pokemon, decorated_name):
        super().__init__(base_pokemon)
        decorated_data = pokedex.get(decorated_name)
        if not decorated_data:
            raise ValueError(f"{decorated_name} not found in the Pokedex.")

        # Store evolved Pokemon attributes
        self.name = decorated_data['name']
        self.p_type = decorated_data['type']
        self.max_health = int(decorated_data['max_health'])
        self.current_health = self.max_health
        self.level = 1  # Start at level 1 for the evolved form
        self.xp = 0     # Reset XP for the evolved form
        self.known_attacks = decorated_data['attacks']
    
    def is_fainted(self):
        return self.current_health <= 0  #tried to delegate it to the base pokemon but not sure 
    
    def take_damage(self, damage):
        self.current_health -= damage
        if self.current_health < 0:
            self.current_health = 0
    
    def attack(self, attack_index, target):
        if self.is_fainted():
            return {"success": False, "message": f"{self.name} is fainted and cannot attack!"}

        attack = self.known_attacks[attack_index]
        base_damage = attack["damage"]
        
        multiplier = 1.0
        if self.p_type == PokemonType.FIRE and target.p_type == PokemonType.GRASS:
            multiplier = 1.75
        elif self.p_type == PokemonType.WATER and target.p_type == PokemonType.FIRE:
            multiplier = 1.75
        elif self.p_type == PokemonType.GRASS and target.p_type == PokemonType.WATER:
            multiplier = 1.75
        elif self.p_type == target.p_type:
            multiplier = 1.0

        final_damage = int(base_damage * multiplier)
        target.take_damage(final_damage)

        result = {
            "success": True,
            "message": f"{self.name} used {attack['name']} on {target.name}!",
            "damage": final_damage,
            "target_fainted": target.is_fainted(),
            "evolved": None
        }

        if target.is_fainted():
            self.xp += 10
            evolved = self.level_up_check()
            if evolved:
                result["evolved"] = evolved
        return result
    
    def level_up_check(self):
        if self.xp >= 30:
            self.xp = 0
            self.level += 1
            if self.level < 4:
                self.max_health += 15
                self.current_health = self.max_health
                for attack in self.known_attacks:
                    attack["damage"] += 4
            elif self.level == 4:
                if self.name == "Charmeleon":
                    return PokeEvolve3(self, "Charizard")
                elif self.name == "Wartortle":
                    return PokeEvolve3(self, "Blastoise")
                elif self.name == "Ivysaur":
                    return PokeEvolve3(self, "Venusaur")
        return None


class PokeEvolve3(PokemonDecorator):
    def __init__(self, base_pokemon, decorated_name):
        super().__init__(base_pokemon)
        decorated_data = pokedex.get(decorated_name)
        if not decorated_data:
            raise ValueError(f"{decorated_name} not found in the Pokedex.")

        # Store evolved Pokemon attributes
        self.name = decorated_data['name']
        self.p_type = decorated_data['type']
        self.max_health = int(decorated_data['max_health'])
        self.current_health = self.max_health
        self.level = 1  # Start at level 1 for the evolved form
        self.xp = 0     # Reset XP for the evolved form
        self.known_attacks = decorated_data['attacks']
    
    def is_fainted(self):
        return self.current_health <= 0
    
    def take_damage(self, damage):
        self.current_health -= damage
        if self.current_health < 0:
            self.current_health = 0
    
    def attack(self, attack_index, target):
        if self.is_fainted():
            return {"success": False, "message": f"{self.name} is fainted and cannot attack!"}

        attack = self.known_attacks[attack_index]
        base_damage = attack["damage"]

        multiplier = 1.0
        if self.p_type == PokemonType.FIRE and target.p_type == PokemonType.GRASS:
            multiplier = 2.0
        elif self.p_type == PokemonType.WATER and target.p_type == PokemonType.FIRE:
            multiplier = 2.0
        elif self.p_type == PokemonType.GRASS and target.p_type == PokemonType.WATER:
            multiplier = 2.0
        elif self.p_type == target.p_type:
            multiplier = 1.0

        final_damage = int(base_damage * multiplier)
        target.take_damage(final_damage)

        result = {
            "success": True,
            "message": f"{self.name} used {attack['name']} on {target.name}!",
            "damage": final_damage,
            "target_fainted": target.is_fainted(),
            "evolved": None
        }

        if target.is_fainted():
            self.xp += 10
            self.level_up_check()
        return result
    
    def level_up_check(self):
        if self.xp >= 30:
            self.xp = 0
            self.level += 1
            self.max_health += 15
            self.current_health = self.max_health
            for attack in self.known_attacks:
                attack["damage"] += 4
        return None