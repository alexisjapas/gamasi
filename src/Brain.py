import random


class Brain:
    def __init__(self, possible_actions) -> None:
        self.possible_actions = possible_actions

    def __call__(self, inputs: list):
        action = random.choices(
            [pa for pa in self.possible_actions], weights=[0.09, 0.90, 0.01]
        )
        return action[0]
