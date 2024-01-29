from enum import Enum

from .Brain import Brain


class Abilities(Enum):
    idle = "idle"
    move = "move"
    reproduce = "reproduce"


class Phenome:
    """
    It will be possible to create one phenome from other phenome(s) with mutations
    Hereditary attributes are locked into a structure to be passed on to the next generation
    But they are copied and can evolve during the life of the agent
    """

    def __init__(
        self,
        reaction_time: float = 10**-5,
        speed: int = 1000,
        energy: int = 1000,
        scope: int = 1,
    ):
        self.reaction_time: float = reaction_time
        self.speed: int = speed
        self.energy: int = energy
        self.scope: int = scope
        self.brain: Brain = Brain(possible_actions=Abilities)

    def mutate(self):  # TODO
        return Phenome(energy=1000)
