# simple_battle.py
import random
from .pokemon import Pokemon

def battle_loop(player_pokemon, wild_pokemon):
    """
    Simple battle loop between player's Pokemon and a wild Pokemon
    
    Args:
        player_pokemon: Player's Pokemon instance
        wild_pokemon: Wild Pokemon instance
        
    Returns:
        True if player won, False if player lost
    """
    print(f"\nA wild {wild_pokemon.name} appeared!")
    print(f"Go, {player_pokemon.name}!")
    
    turn = 0  # 0 for player's turn, 1 for wild Pokemon's turn
    
    while True:
        # Print current status
        print("\n" + "="*40)
        print(f"Your {player_pokemon.name}: {player_pokemon.current_health}/{player_pokemon.max_health} HP")
        print(f"Wild {wild_pokemon.name}: {wild_pokemon.current_health}/{wild_pokemon.max_health} HP")
        print("="*40)
        
        if turn == 0:  # Player's turn
            print("\nYour turn!")
            print("Choose an attack:")
            for i, attack in enumerate(player_pokemon.known_attacks):
                print(f"{i+1}. {attack['name']} (Damage: {attack['damage']})")
            print("5. Run away")
            
            choice = input("Enter your choice (1-5): ")
            
            if choice == "5":
                # Try to run away (70% chance)
                if random.random() < 0.7:
                    print("You successfully ran away!")
                    return False  # Neither win nor loss
                else:
                    print("You couldn't escape!")
                    turn = 1  # Wild Pokemon's turn
                    continue
            
            try:
                attack_index = int(choice) - 1
                if attack_index < 0 or attack_index >= len(player_pokemon.known_attacks):
                    print("Invalid choice. Try again.")
                    continue
                
                # Perform attack
                result = player_pokemon.attack(attack_index, wild_pokemon)
                print(result["message"])
                print(f"Dealt {result['damage']} damage!")
                
                if wild_pokemon.is_fainted():
                    print(f"Wild {wild_pokemon.name} fainted!")
                    print(f"Your {player_pokemon.name} gained 10 XP!")
                    
                    # Check for evolution
                    if result.get("evolved"):
                        print(f"Your {player_pokemon.name} evolved into {result['evolved'].name}!")
                        player_pokemon = result["evolved"]
                    
                    return True  # Player won
                
                turn = 1  # Wild Pokemon's turn
                
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
                
        else:  # Wild Pokemon's turn
            print(f"\nWild {wild_pokemon.name}'s turn!")
            
            # Wild Pokemon randomly selects an attack
            attack_index = random.randint(0, len(wild_pokemon.known_attacks) - 1)
            
            # Perform attack
            result = wild_pokemon.attack(attack_index, player_pokemon)
            print(result["message"])
            print(f"Took {result['damage']} damage!")
            
            if player_pokemon.is_fainted():
                print(f"Your {player_pokemon.name} fainted!")
                return False  # Player lost
            
            turn = 0  # Player's turn

def main():
    # Create player's Pokemon
    print("Welcome to Pokemon Battle Simulator!")
    print("Choose your starter Pokemon:")
    print("1. Charmander (Fire)")
    print("2. Squirtle (Water)")
    print("3. Bulbasaur (Grass)")
    
    while True:
        starter_choice = input("Enter your choice (1-3): ")
        if starter_choice == "1":
            player_pokemon = Pokemon("Charmander")
            break
        elif starter_choice == "2":
            player_pokemon = Pokemon("Squirtle")
            break
        elif starter_choice == "3":
            player_pokemon = Pokemon("Bulbasaur")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    print(f"You chose {player_pokemon.name}!")
    
    # Game loop
    battling = True
    battle_count = 0
    
    while battling:
        # Generate random wild Pokemon
        wild_options = ["Charmander", "Squirtle", "Bulbasaur"]
        wild_pokemon = Pokemon(random.choice(wild_options))
        
        # Start battle
        result = battle_loop(player_pokemon, wild_pokemon)
        battle_count += 1
        
        if result:  # Player won
            print("\nYou won the battle!")
            
            # Check if player's Pokemon evolved and update
            if hasattr(player_pokemon, "base") and player_pokemon.base != player_pokemon:
                player_pokemon = player_pokemon
                
            # Heal player's Pokemon a bit for the next battle
            heal_amount = player_pokemon.max_health // 4
            player_pokemon.current_health = min(player_pokemon.current_health + heal_amount, player_pokemon.max_health)
            print(f"Your {player_pokemon.name} recovered some HP! ({player_pokemon.current_health}/{player_pokemon.max_health})")
        else:
            print("\nYou lost the battle!")
            # Partially heal Pokemon after a loss
            player_pokemon.current_health = player_pokemon.max_health // 2
            print(f"Your {player_pokemon.name} was healed at a Pokemon Center! ({player_pokemon.current_health}/{player_pokemon.max_health})")
        
        if battle_count >= 3:
            print(f"\nYour {player_pokemon.name}'s stats:")
            print(f"Level: {player_pokemon.level}")
            print(f"HP: {player_pokemon.current_health}/{player_pokemon.max_health}")
            print(f"XP: {player_pokemon.xp}/30")
            
            if player_pokemon.level >= 4:
                print(f"Your {player_pokemon.name} has reached max level in this demo!")
        
        choice = input("\nBattle again? (y/n): ")
        if choice.lower() != "y":
            battling = False
    
    print("Thanks for playing!")

if __name__ == "__main__":
    main()