import random


class Brain:
    def __init__(self, possible_actions) -> None:
        self.possible_actions = possible_actions

    def __call__(self, inputs: list):
        return random.choice([pa for pa in self.possible_actions])
