import threading
import numpy as np
from random import shuffle, randint
from time import sleep
from matplotlib import pyplot as plt
from math import ceil
from enum import Enum

from .Agent import Agent
from .Space import Space
from .Position import Position


class Distributions(Enum):
    random = "random"


class Lab:
    def __init__(self, height: int, width: int, init_population_count: int):
        assert init_population_count <= height * width

        # Spacetime
        self.space = Space(height=height, width=width, lock=threading.Lock())

        # Population
        self.init_population_count = init_population_count
        self._invoke_population(init_population_count)
        assert np.sum(self.space.array != None) == init_population_count

    def _start_agents(self):
        with Agent.living_lock:
            for agent in Agent.living.values():
                agent.start()

    def _stop_agents(self):
        with Agent.living_lock:
            for agent in Agent.living.values():
                agent.stop.set()

    def _invoke_population(
        self, init_population_count: int, distribution: Distributions = Distributions.random
    ) -> list[Agent]:
        positions = []
        match distribution:
            case Distributions.random:
                while len(positions) < init_population_count:
                    new_pos = Position(
                        randint(0, self.space.height - 1),
                        randint(0, self.space.width - 1),
                    )
                    if new_pos not in positions:
                        positions.append(new_pos)
            case _:
                raise ValueError(f"Possible distributions: {[d.name for d in Distributions]}")
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
        n_viz = min(n_viz, self.init_population_count)
        assert n_viz <= len(Agent.living) + len(Agent.dead)

        # Display paths of some dead and living agents
        fig = plt.figure()
        n_rows = ceil(n_viz**(1/2))
        n_cols = ceil(n_viz / n_rows)
        deads_vizualized_count = min(n_viz//2, len(Agent.dead))
        for i in range(deads_vizualized_count):
            plt.subplot(n_rows, n_cols, i+1)
            plt.imshow(Agent.dead[i].array_path)
            plt.title(f"Dead agent's n°{i} path")
            plt.axis("off")
        for i in range(n_viz - deads_vizualized_count):
            plt.subplot(n_rows, n_cols, i+1)
            plt.imshow(Agent.living[i].array_path)
            plt.title(f"Living agent's n°{i} path")
            plt.axis("off")

        # Display the space's final disposition
        plt.figure()
        plt.imshow(self.space.displayable)
        plt.title("Final space disposition")
        plt.axis("off")
        plt.show()