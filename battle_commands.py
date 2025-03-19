from typing import List
from command import ChatCommand
from message import DialogueMessage, ServerMessage
from .pokemon import PokemonType, create_starter, Pokemon, Attack

class AttackCommand(ChatCommand):
    name = 'attack'
    desc = 'Use an attack in battle'
    
    @classmethod
    def matches(cls, command_text: str) -> bool:
        return command_text.startswith('attack') or command_text.startswith('use')
    
    def execute(self, command_text: str, context, player) -> List:
        # Check if player is in battle
        if not player.get_state("in_battle", False):
            return [ServerMessage(player, "You're not in a battle!")]
        
        # Parse attack index from command
        parts = command_text.split()
        attack_index = 0  # Default to first attack
        
        if len(parts) > 1:
            try:
                attack_index = int(parts[1]) - 1  # Convert to 0-based index
            except ValueError:
                # Try to find attack by name
                attack_name = ' '.join(parts[1:]).lower()
                
                # Get player's Pokemon from state
                starter_type = player.get_state("starter_type", "FIRE")
                pokemon = create_starter(PokemonType[starter_type])
                
                # Find attack by name
                for i, attack in enumerate(pokemon.attacks):
                    if attack.name.lower() == attack_name:
                        attack_index = i
                        break
        
        # Store the attack choice in player state
        player.set_state("battle_attack_index", attack_index)
        
        return [ServerMessage(player, f"Using attack {attack_index + 1}")]

class PotionCommand(ChatCommand):
    name = 'potion'
    desc = 'Use a health potion in battle'
    
    @classmethod
    def matches(cls, command_text: str) -> bool:
        return command_text.startswith('potion') or command_text.startswith('heal')
    
    def execute(self, command_text: str, context, player) -> List:
        # Check if player is in battle
        if not player.get_state("in_battle", False):
            return [ServerMessage(player, "You're not in a battle!")]
        
        # Check if player has potions
        potions = player.get_state("potions", 0)
        if potions <= 0:
            return [ServerMessage(player, "You don't have any potions!")]
        
        # Mark that player wants to use a potion
        player.set_state("battle_use_potion", True)
        
        return [ServerMessage(player, "Using a health potion!")]

class RunCommand(ChatCommand):
    name = 'run'
    desc = 'Attempt to flee from battle'
    
    @classmethod
    def matches(cls, command_text: str) -> bool:
        return command_text.startswith('run') or command_text.startswith('flee')
    
    def execute(self, command_text: str, context, player) -> List:
        # Check if player is in battle
        if not player.get_state("in_battle", False):
            return [ServerMessage(player, "You're not in a battle!")]
        
        # Mark that player wants to run
        player.set_state("battle_run", True)
        
        return [ServerMessage(player, "Attempting to run from battle!")]

# Battle commands defined directly in server_local.py
class AttackCommand(ChatCommand):
    name = 'attack'
    desc = 'Use an attack in battle'
    
    @classmethod
    def matches(cls, command_text: str) -> bool:
        return command_text.startswith('attack') or command_text.startswith('use')
    
    def execute(self, command_text: str, context, player) -> list[Message]:
        # Check if player is in battle
        if not player.get_state("in_battle", False):
            return [ServerMessage(player, "You're not in a battle!")]
        
        # Parse attack index from command
        parts = command_text.split()
        attack_index = 0  # Default to first attack
        
        if len(parts) > 1:
            try:
                attack_index = int(parts[1]) - 1  # Convert to 0-based index
            except ValueError:
                # Handle attack by name if needed
                pass
        
        # Store the attack choice in player state
        player.set_state("battle_attack_index", attack_index)
        
        return [ServerMessage(player, f"Using attack {attack_index + 1}")]

class PotionCommand(ChatCommand):
    name = 'potion'
    desc = 'Use a health potion in battle'
    
    @classmethod
    def matches(cls, command_text: str) -> bool:
        return command_text.startswith('potion') or command_text.startswith('heal')
    
    def execute(self, command_text: str, context, player) -> list[Message]:
        # Check if player is in battle
        if not player.get_state("in_battle", False):
            return [ServerMessage(player, "You're not in a battle!")]
        
        # Check if player has potions
        potions = player.get_state("potions", 0)
        if potions <= 0:
            return [ServerMessage(player, "You don't have any potions!")]
        
        # Mark that player wants to use a potion
        player.set_state("battle_use_potion", True)
        
        return [ServerMessage(player, "Using a health potion!")]

class RunCommand(ChatCommand):
    name = 'run'
    desc = 'Attempt to flee from battle'
    
    @classmethod
    def matches(cls, command_text: str) -> bool:
        return command_text.startswith('run') or command_text.startswith('flee')
    
    def execute(self, command_text: str, context, player) -> list[Message]:
        # Check if player is in battle
        if not player.get