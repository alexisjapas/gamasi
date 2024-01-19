import threading
import numpy as np
from random import shuffle, randint
from time import sleep
from matplotlib import pyplot as plt
from math import ceil

from .Agent import Agent
from .Space import Space
from .Position import Position


class Lab:
    def __init__(self, height: int, width: int, init_population_count: int):
        assert init_population_count <= height * width

        # Spacetime
        self.space = Space(height=height, width=width, lock=threading.Lock())

        # Population
        self._invoke_population(init_population_count)

    def _start_agents(self):
        with Agent.living_lock:
            for agent in Agent.living.values():
                agent.start()

    def _stop_agents(self):
        with Agent.living_lock:
            for agent in Agent.living.values():
                agent.stop.set()

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
        [
            Agent(
                space=self.space,
                initial_position=pos,
                generation=0,
            )
            for pos in positions
        ]

    def experiment(self, duration):
        # Start
        self._start_agents()  # TODO all agents shall wait until starting

        # Run
        sleep(duration)

        # Stop
        self._stop_agents()

    def analyze(self, n_viz=4):
        assert n_viz <= len(Agent.living)

        fig = plt.figure()
        n_rows = ceil(n_viz**(1/2))
        n_cols = ceil(n_viz / n_rows)
        print(n_rows)
        for i in range(n_viz):
            plt.subplot(n_rows, n_cols, i+1)
            plt.imshow(Agent.living[i].array_path)
            plt.title(f"Agent's n°{i} path")
            plt.axis("off")
        plt.figure()
        plt.imshow(self.space.displayable)
        plt.title("Final positions")
        plt.axis("off")
        plt.show()