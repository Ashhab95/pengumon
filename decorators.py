from pengumon import Pengumon

class EvolutionDecorator(Pengumon):
    def __init__(self, decoratedPengumon):
        self.decoratedPengumon = decoratedPengumon

class TypeDecorator(Pengumon):
    def __init__(self, decoratedPengumon):
        self.decoratedPengumon = decoratedPengumon

