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
        initial_population_map = self.get_population_map()
        self.population_maps = initial_population_map[np.newaxis, :, :]

    def get_population_map(self):
        current_map = np.zeros((self.height, self.width))
        for agent in self.population:
            current_map[agent.position] = agent.id
        
        return current_map


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    lab = Lab(height=10, width=20, initial_population=200)
    print(np.sum(lab.population_maps[-1] != 0))
    plt.imshow(lab.population_maps[-1])
    plt.show()