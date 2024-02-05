from random import randint

from .Brain import Brain


class Phenome:
    def __init__(
        self,
        reaction_time: float = 1e-5,
        speed: int = 1e5,
        energy_capacity: int = 1e2,
        scope: int = 3,
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

    def copy(self):
        return Phenome(
            reaction_time=self.reaction_time,
            speed=self.speed,
            energy_capacity=self.energy_capacity,
            scope=self.scope,
            color=self.color,
            brain=self.brain.copy(),
        )

    def mutate(self):
        # TODO
        pass
