import threading
import numpy as np
from random import shuffle, randint
from time import sleep

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
        self.map_lock = threading.Lock()

        # population
        self.population = self._invoke_population(init_population_count)

    def _invoke_population(
        self, init_population_count: int, distribution: str = "random"
    ) -> list[Agent]:
        positions = []
        match distribution:
            case "random":
                while len(positions) < init_population_count:
                    new_pos = (randint(0, self.height - 1), randint(0, self.width - 1))
                    if new_pos not in positions:
                        positions.append(new_pos)
        return [
            Agent(
                population_map=self.population_map,
                map_lock=self.map_lock,
                initial_position=pos,
                generation=0,
            )
            for pos in positions
        ]

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
    init_pop_count = 10

    # Init lab
    lab = Lab(height=height, width=width, init_population_count=init_pop_count)
    assert np.sum(lab.population_map != None) == init_pop_count  # TODO add to tests

    for agent in lab.population:
        agent.start()

    print(f"Active threads: {threading.active_count()-1}")
    sleep(1)
    for agent in lab.population:
        agent.kill()
    # Visualization
    id_map = lab.get_id_map()
    plt.imshow(id_map)
    plt.show()
