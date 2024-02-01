from .Brain import Brain
from random import randint


class Phenome:
    """
    It will be possible to create one phenome from other phenome(s) with mutations
    Hereditary attributes are locked into a structure to be passed on to the next generation
    But they are copied and can evolve during the life of the agent
    """

    def __init__(
        self,
        reaction_time: float = 1e-5,
        speed: int = 1e5,
        energy_capacity: int = 1e4,
        scope: int = 1,
        color: tuple = None,
        brain: Brain = None,
    ):
        self.reaction_time: float = reaction_time
        self.speed: int = speed
        self.energy_capacity: int = energy_capacity
        self.scope: int = scope
        self.color: tuple = (
            color if color else (randint(5, 252), randint(5, 252), randint(5, 252))
        )
        self.brain: Brain = brain if brain else Brain()

    def copy(self, mutation: float = 0):
        # TODO mutation
        return Phenome(
            reaction_time=self.reaction_time,
            speed=self.speed,
            energy_capacity=self.energy_capacity,
            scope=self.scope,
            color=self.color,  # TODO how to mutate it?
            brain=self.brain.copy(mutation=mutation),
        )
