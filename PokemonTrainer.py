from .imports import *
from .bag import Bag
from .pokeball import Pokeball
from .pokemon import Pokemon

class PokemonTrainer(HumanPlayer):
    def __init__(self):
        self.bag = Bag()