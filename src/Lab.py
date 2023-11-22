import numpy as np
from random import shuffle, randint

from Agent import Agent


class Lab:
    # INITIALIZATION
    def __init__(self, height: int, width: int, init_population_count: int):
        assert init_population_count <= height * width

        # map
        self.height = height
        self.width = width
        self.population_map = np.full(
            shape=(height, width), fill_value=None, dtype=object
        )

        # population
        self.population = self._init_population(init_population_count)

    def _init_population(
        self, init_population_count: int, distribution: str = "random"
    ) -> list[Agent]:
        positions = []
        match distribution:
            case "random":
                while len(positions) < init_population_count:
                    new_pos = (randint(0, self.height - 1), randint(0, self.width - 1))
                    if new_pos not in positions:
                        positions.append(new_pos)
        return [Agent(self.population_map, pos, 0) for pos in positions]

    # VISUALIZATION
    def get_id_map(self):
        id_map = np.vectorize(
            lambda agent: 255 - agent.id % 200 if agent is not None else 0,
        )(self.population_map)
        return id_map


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    # Settings
    height = 36
    width = 50
    init_pop_count = 100

    # Init lab
    lab = Lab(height=height, width=width, init_population_count=init_pop_count)
    assert np.sum(lab.population_map != None) == init_pop_count

    # Visualization
    id_map = lab.get_id_map()
    plt.imshow(id_map)
    plt.show()
