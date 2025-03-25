from typing import Dict
from .PokemonTrainer import PokemonTrainer

_trainer_map: Dict[str, PokemonTrainer] = {}

def get_trainer(human_player) -> PokemonTrainer:
    email = human_player.get_email()  
    return _trainer_map.get(email, None)

def register_trainer(human_player, starter: str):
    email = human_player.get_email()
    trainer = PokemonTrainer(human_player, starter)
    _trainer_map[email] = trainer