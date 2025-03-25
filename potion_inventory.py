# Player's inventory that stores references to flyweight potions
from .items import Potion,PotionFlyweightFactory 
from typing import Dict, Any, Optional, List

class PlayerInventory:
    def __init__(self):
        self.items = []
    
    def add_item(self, potion_type: str):
        """Add a potion to the inventory by its type name"""
        potion = PotionFlyweightFactory.get_by_name(potion_type)
        if potion:
            self.items.append(potion)
    
    def remove_item(self, index: int) -> Optional[Potion]:
        """Remove and return a potion from the inventory by index"""
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None
    
    def get_items(self) -> List[Potion]:
        """Get all potions in the inventory"""
        return self.items
    
    def use_item(self, index: int, target) -> Dict[str, Any]:
        """Use a potion on a target and remove it from inventory"""
        if 0 <= index < len(self.items):
            potion = self.items[index]
            result = potion.use(target)
            if result["success"]:
                self.items.pop(index)
            return result
        return {
            "success": False,
            "message": "Invalid item index"
        }
    
    def __str__(self) -> str:
        """String representation of the inventory"""
        if not self.items:
            return "Inventory is empty"
        
        result = "Inventory:\n"
        for i, item in enumerate(self.items):
            result += f"{i+1}. {item.get_name()} (Heals {item.get_value()} HP)\n"
        return result

