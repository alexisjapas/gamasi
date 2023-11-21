import numpy as np
from random import shuffle

from Agent import Agent


class Lab:
    def __init__(self, height: int, width: int, initial_population: int):
        # map
        self.height = height
        self.width = width

        # population
        y_pos = [y * height // initial_population for y in range(0, initial_population)]
        shuffle(y_pos)
        x_pos = [x * width // initial_population for x in range(0, initial_population)]
        shuffle(x_pos)
        self.population = [
            Agent((y_pos.pop(), x_pos.pop()), 0) for _ in range(initial_population)
        ]

        # timeline metrics
        initial_population_map = np.zeros((height, width))
        self.population_map = initial_population_map[np.newaxis, :, :]


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    lab = Lab(height=10, width=20, initial_population=10)
    print(lab.population)
    print(lab.population_map)