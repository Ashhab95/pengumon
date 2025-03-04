from bag import Bag
from move import Move
from pengumon import Pengumon

class Player:
    def __init__(self):
        self.bag = Bag()
        self.move = Move()
        self.pengumon = Pengumon()
        self.pengumon_list = []
        self.active_pengumon = None
        self.potion = 0