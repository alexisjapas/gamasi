import threading
import numpy as np
from random import shuffle, randint
from time import sleep

from Agent import Agent
from Space import Space
from Position import Position


class Lab:
    def __init__(self, height: int, width: int, init_population_count: int):
        assert init_population_count <= height * width

        # Spacetime
        self.space = Space(height=height, width=width, lock=threading.Lock())

        # Population
        self.population = self._invoke_population(init_population_count)

    def experiment(self, duration):
        # Start
        for agent in lab.population:
            agent.start()
        sleep(duration)

        # Stop
        for agent in lab.population:
            agent.kill()

    def analyze(self, n_viz):
        assert n_viz <= len(self.population)
        n_viz = 3
        for i in range(n_viz):
            plt.figure(f"Agent's n°{i} path")
            plt.imshow(lab.population[i].array_path)
        plt.figure("Final positions")
        plt.imshow(lab.space.displayable)
        plt.show()

    def _invoke_population(
        self, init_population_count: int, distribution: str = "random"
    ) -> list[Agent]:
        positions = []
        match distribution:
            case "random":
                while len(positions) < init_population_count:
                    new_pos_values = (
                        randint(0, self.space.height - 1),
                        randint(0, self.space.width - 1),
                    )
                    if new_pos_values not in positions:
                        positions.append(
                            Position(
                                new_pos_values[0], new_pos_values[1], self.space.genesis
                            )
                        )
        return [
            Agent(
                space=self.space,
                initial_position=pos,
                generation=0,
            )
            for pos in positions
        ]


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    # Settings
    height = 72
    width = 100
    init_pop_count = 10

    # Init lab
    lab = Lab(height=height, width=width, init_population_count=init_pop_count)
    assert np.sum(lab.space.array != None) == init_pop_count  # TODO move to tests
    lab.experiment(duration=1e-1)
    lab.analyze(n_viz=3)
