from typing import List, Dict, Any, Optional, Tuple
from .items import Item, Potion
from .pokeball import Pokeball
from .pokemon import Pokemon

class ItemCompartment:
    
    def __init__(self, name: str):
        self.name = name
        self.items: List[Item] = []
    
    def add(self, item: Item) -> None:
        self.items.append(item)
    
    def remove(self, index: int) -> Optional[Item]:
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None
    
    def get(self, index: int) -> Optional[Item]:
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def count(self) -> int:
        return len(self.items)
    
    def list_items(self) -> List[Tuple[int, Item]]:
        return [(i, item) for i, item in enumerate(self.items)]
    
    def __str__(self) -> str:
        if not self.items:
            return f"{self.name}: Empty"
        
        result = f"{self.name} ({len(self.items)}):\n"
        for i, item in enumerate(self.items):
            result += f"  {i+1}. {item.get_name()}\n"
        return result

class Bag:
    def __init__(self):
        self.compartments: Dict[str, ItemCompartment] = {
            "potion": ItemCompartment("potion"),
            "pokeballs": ItemCompartment("Empty Pokeballs"),
            "pokemon": ItemCompartment("Your Pokemon")
        }
    
    def _has_active_pokemon(self) -> bool:
        """Check if there is an active Pokemon in the bag"""
        return any(isinstance(ball, Pokeball) and ball.is_active_pokemon() 
                  for ball in self.compartments["pokemon"].items)
    
    def add_item(self, item: Item) -> None:
        if isinstance(item, Potion):
            self.compartments["potion"].add(item)
        elif isinstance(item, Pokeball):
            if item.is_empty():
                self.compartments["pokeballs"].add(item)
            else:
                self.compartments["pokemon"].add(item)
                
                # If this is our first Pokemon, make it the active one
                if not self._has_active_pokemon():
                    item.set_active(True)

    
    def open_bag(self) -> Dict[str, List[Tuple[int, Item]]]:
        result = {}
        for name, compartment in self.compartments.items():
            result[name] = compartment.list_items()
        return result
    
    def select_item(self, compartment_name: str, index: int) -> Optional[Item]:
        if compartment_name in self.compartments:
            return self.compartments[compartment_name].get(index)
        return None
    
    def remove_item(self, compartment_name: str, index: int) -> Optional[Item]:
        if compartment_name in self.compartments:
            return self.compartments[compartment_name].remove(index)
        return None
    
    def use_potion(self, index: int, target_pokemon: Pokemon) -> Dict[str, Any]:
        item = self.select_item("potion", index)
        if item and isinstance(item, Potion):
            result = item.use(target_pokemon)
            if result["success"]:
                self.remove_item("potion", index)
            return result
        return {
            "success": False,
            "message": "Invalid potion item."
        }
    
    def use_pokeball(self, index: int, wild_pokemon: Pokemon) -> Dict[str, Any]:
        pokeball = self.select_item("pokeballs", index)
        if pokeball and isinstance(pokeball, Pokeball):
            result = pokeball.use(wild_pokemon)
            if result["success"]:
                self.remove_item("pokeballs", index)
                self.compartments["pokemon"].add(pokeball)
                
                if not self._has_active_pokemon():
                    pokeball.set_active(True)
            return result
        return {
            "success": False,
            "message": "Invalid Pokeball."
        }
    
    def switch_pokemon(self, index: int) -> Dict[str, Any]:
        pokeball = self.select_item("pokemon", index)
        if pokeball and isinstance(pokeball, Pokeball) and not pokeball.is_empty():
            for ball in self.compartments["pokemon"].items:
                if isinstance(ball, Pokeball) and ball.is_active_pokemon():
                    ball.set_active(False)
            
            pokeball.set_active(True)
            
            pokemon = pokeball.get_pokemon()
            if pokemon:
                return {
                    "success": True,
                    "message": f"Switched active Pokemon to {pokemon.name}!",
                    "pokemon": pokemon
                }
            else:
                return {
                    "success": False,
                    "message": "The selected Pokeball doesn't contain a Pokemon!"
                }
        return {
            "success": False,
            "message": "Invalid Pokemon selection."
        }
    
    def get_active_pokemon(self) -> Optional[Pokemon]:
        for ball in self.compartments["pokemon"].items:
            if isinstance(ball, Pokeball) and ball.is_active_pokemon():
                return ball.get_pokemon()
        return None
    
    def get_all_pokemon(self) -> List[Pokemon]:
        pokemon_list = []
        for item in self.compartments["pokemon"].items:
            if isinstance(item, Pokeball) and not item.is_empty():
                pokemon = item.get_pokemon()
                if pokemon:
                    pokemon_list.append(pokemon)
        return pokemon_list
    
    def count_items(self, compartment_name: str) -> int:
        if compartment_name in self.compartments:
            return self.compartments[compartment_name].count()
        return 0
    
    def __str__(self) -> str:
        result = "Bag Contents:\n"
        for compartment in self.compartments.items():
            result += str(compartment) + "\n"
        
        active_pokemon = self.get_active_pokemon()
        if active_pokemon:
            result += f"Active Pokemon: {active_pokemon.name} (HP: {active_pokemon.current_health}/{active_pokemon.max_health})\n"
        else:
            result += "Active Pokemon: None\n"
            
        return result
    


    