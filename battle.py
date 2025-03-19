# battle_with_healing.py
import random
from .pokemon import Pokemon
from .items import PotionFlyweightFactory

def battle_loop(player_pokemon, wild_pokemon):
    """
    Battle loop between player's Pokemon and a wild Pokemon, with healing options
    
    Args:
        player_pokemon: Player's Pokemon instance
        wild_pokemon: Wild Pokemon instance
        
    Returns:
        True if player won
        False if player lost
        None if player ran away
    """
    print(f"\nA wild {wild_pokemon.name} appeared!")
    print(f"Go, {player_pokemon.name}!")
    
    # Get potions using the flyweight factory
    player_potion = PotionFlyweightFactory.get_medium_potion()
    ai_potion = PotionFlyweightFactory.get_small_potion()
    player_has_potion = True
    ai_has_potion = True
    
    turn = 0  # 0 for player's turn, 1 for wild Pokemon's turn
    
    while True:
        # Print current status
        print("\n" + "="*40)
        print(f"Your {player_pokemon.name}: {player_pokemon.current_health}/{player_pokemon.max_health} HP")
        print(f"Wild {wild_pokemon.name}: {wild_pokemon.current_health}/{wild_pokemon.max_health} HP")
        print("="*40)
        
        if turn == 0:  # Player's turn
            # Print menu options based on available actions
            print("\nYour turn!")
            print("Choose an action:")
            for i, attack in enumerate(player_pokemon.known_attacks):
                print(f"{i+1}. {attack['name']} (Damage: {attack['damage']})")
            
            # Add healing option if potion is available
            heal_option_num = len(player_pokemon.known_attacks) + 1
            run_option_num = len(player_pokemon.known_attacks) + (2 if player_has_potion else 1)
            
            if player_has_potion:
                print(f"{heal_option_num}. Use {player_potion.get_name()} (Heals {player_potion.get_value()} HP)")
                
            # Always add run away option as the last option
            print(f"{run_option_num}. Run away")
            
            # Prompt with the correct range
            max_choice = run_option_num
            choice = input(f"Enter your choice (1-{max_choice}): ")
            
            # Handle running away
            if int(choice) == run_option_num:
                # Try to run away (70% chance)
                if random.random() < 0.7:
                    print("You successfully ran away!")
                    return None  # Player ran away - distinct from losing
                else:
                    print("You couldn't escape!")
                    turn = 1  # Wild Pokemon's turn
                    continue
            
            # Handle healing
            if player_has_potion and int(choice) == heal_option_num:
                result = player_potion.use(player_pokemon)
                print(result["message"])
                print(f"Your {player_pokemon.name} now has {player_pokemon.current_health}/{player_pokemon.max_health} HP.")
                player_has_potion = False
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
            
            # AI logic for healing:
            # Heal if health is below 30% and has potion
            should_heal = (wild_pokemon.current_health < wild_pokemon.max_health * 0.3) and ai_has_potion
            
            if should_heal:
                result = ai_potion.use(wild_pokemon)
                print(f"Wild {wild_pokemon.name} used a potion!")
                print(f"Wild {wild_pokemon.name} restored {result['amount_healed']} HP!")
                print(f"Wild {wild_pokemon.name} now has {wild_pokemon.current_health}/{wild_pokemon.max_health} HP.")
                ai_has_potion = False
                
            else:
                # Wild Pokemon attacks
                attack_index = random.randint(0, len(wild_pokemon.known_attacks) - 1)
                
                # Perform attack
                result = wild_pokemon.attack(attack_index, player_pokemon)
                print(result["message"])
                print(f"You took {result['damage']} damage!")
                
                if player_pokemon.is_fainted():
                    print(f"Your {player_pokemon.name} fainted!")
                    return False  # Player lost
            
            turn = 0  # Player's turn

def main():
    # Create player's Pokemon
    print("Welcome to Pokemon Battle Simulator with Healing!")
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
    wins = 0
    losses = 0
    escapes = 0
    
    while battling:
        # Generate random wild Pokemon
        wild_options = ["Charmander", "Squirtle", "Bulbasaur"]
        wild_pokemon = Pokemon(random.choice(wild_options))
        
        # Start battle
        result = battle_loop(player_pokemon, wild_pokemon)
        battle_count += 1
        
        if result is True:  # Player won
            print("\nYou won the battle!")
            wins += 1
            
            # Check if player's Pokemon evolved and update
            if hasattr(player_pokemon, "base") and player_pokemon.base != player_pokemon:
                player_pokemon = player_pokemon
                
            # Heal player's Pokemon a bit for the next battle
            heal_amount = player_pokemon.max_health // 4
            player_pokemon.current_health = min(player_pokemon.current_health + heal_amount, player_pokemon.max_health)
            print(f"Your {player_pokemon.name} recovered some HP! ({player_pokemon.current_health}/{player_pokemon.max_health})")
        elif result is False:  # Player lost
            print("\nYou lost the battle!")
            losses += 1
            # Partially heal Pokemon after a loss
            player_pokemon.current_health = player_pokemon.max_health // 2
            print(f"Your {player_pokemon.name} was healed at a Pokemon Center! ({player_pokemon.current_health}/{player_pokemon.max_health})")
        elif result is None:  # Player ran away
            print("\nYou escaped from the battle.")
            escapes += 1
            # Minor recovery after running
            heal_amount = player_pokemon.max_health // 10
            player_pokemon.current_health = min(player_pokemon.current_health + heal_amount, player_pokemon.max_health)
            print(f"Your {player_pokemon.name} caught its breath. ({player_pokemon.current_health}/{player_pokemon.max_health})")
        
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
    print("\n----- BATTLE SUMMARY -----")
    print(f"Total battles: {battle_count}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Escapes: {escapes}")
    print(f"Final Pokemon: {player_pokemon.name} (Level {player_pokemon.level})")

if __name__ == "__main__":
    main()