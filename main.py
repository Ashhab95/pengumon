from world import World
from player import Player
from battleground import Battleground

class Game:
    def __init__(self):
        self.world = World()
        self.player = Player()
        self.battleground = Battleground()