import random
from enum import Enum


class Abilities(Enum):
    idle = "idle"
    move = "move"
    reproduce = "reproduce"


class Brain:
    def __init__(self, weights=[0.5, 0.3, 0.2]) -> None:
        self.weights = weights

    def __call__(self, inputs: list):
        action = random.choices([pa for pa in Abilities], self.weights)
        return action[0]

    def copy(self, mutation: float = 0):
        # TODO mutation
        return Brain(weights=self.weights)
