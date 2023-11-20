import numpy as np

from Agent import Agent


class Lab:
    def __init__(self, height: int, width: int, agents_number: int):
        self.height = height
        self.width = width
        self.agents_number = agents_number


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    lab = Lab(100, 200, [])
