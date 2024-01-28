from enum import Enum

from .Brain import Brain


class Abilities(Enum):
    idle = "idle"
    move = "move"
    #reproduce = "reproduce"


class Phenome:
    """
    It will be possible to create one phenome from other phenome(s) with mutations
    Hereditary attributes are locked into a structure to be passed on to the next generation
    But they are copied and can evolve during the life of the agent
    """

    def __init__(self):
        self.reaction_time: float = 10**-5
        self.speed: float = 100
        self.energy: float = 100
        self.scope: int = 1
        self.brain = Brain(possible_actions=Abilities)

    def mutate(self):  # TODO
        return self