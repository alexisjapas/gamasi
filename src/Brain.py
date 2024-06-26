from random import random, choices
from enum import Enum


class Abilities(
    Enum
):  # TODO Create an abstract Action class to implement birth and death
    idle = "idle"
    move_bot = "move_bot"
    move_top = "move_top"
    move_left = "move_left"
    move_right = "move_right"
    reproduce = "reproduce"
    eat_bot = "eat_bot"
    eat_top = "eat_top"
    eat_left = "eat_left"
    eat_right = "eat_right"


class Brain:
    def __init__(self, weights=None) -> None:
        weights = weights if weights else [random() for _ in range(len(Abilities))]
        self.weights = [w / sum(weights) for w in weights]

    def __call__(self, inputs: list):
        action = choices([pa for pa in Abilities], self.weights)
        return action[0]

    def copy(self):
        return Brain(weights=self.weights)

    def mutate(self):  # TODO mutation rate and strength?
        # TODO use copy?
        pass
