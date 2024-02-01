import threading
import numpy as np
from random import shuffle, randint
from time import sleep
from matplotlib import pyplot as plt
from math import ceil
from enum import Enum

from .Agent import Agent
from .Universe import Universe
from .Position import Position


class Distributions(Enum):
    random = "random"


class Lab:
    def __init__(self, height: int, width: int, init_population_count: int):
        assert init_population_count <= height * width

        # Universe
        self.universe = Universe(height=height, width=width)

        # Population
        self.init_population_count = init_population_count
        self._invoke_population(init_population_count)
        assert np.sum(self.universe.space != None) == init_population_count

    def _start_agents(self):
        with Agent.lock:  # Lock births
            for agent in Agent.population.values():
                agent.start()
            print("Agents started")

    def _stop_agents(self):
        with Agent.lock:
            for agent in Agent.population.values():
                agent.stop.set()

    def _invoke_population(
        self,
        init_population_count: int,
        distribution: Distributions = Distributions.random,
    ) -> list[Agent]:
        positions = []
        match distribution:
            case Distributions.random:
                while len(positions) < init_population_count:
                    new_pos = Position(
                        randint(0, self.universe.height - 1),
                        randint(0, self.universe.width - 1),
                    )
                    if new_pos not in positions:
                        positions.append(new_pos)
            case _:
                raise ValueError(
                    f"Possible distributions: {[d.name for d in Distributions]}"
                )
        [
            Agent(
                universe=self.universe,
                initial_position=pos,
                generation=0,
                parents=None,
            )
            for pos in positions
        ]

    def experiment(self, duration):
        # Start
        self._start_agents()  # TODO all agents shall wait until starting

        # Run
        while duration > 0:  # TODO Stop when all died?
            sleep(0.1)
            duration -= 0.1

        # Stop
        self.universe.freeze = True
        self._stop_agents()

        # return TODO the results of the experiment in order to run multiple experiments

    def analyze(self, n_viz=4):  # TODO Copy agents until analyse
        # TODO  Add an argument of data (agents...) to analyze or analyze last one
        n_viz = min(n_viz, Agent.count)

        # Some stats
        print(f"Total agents: {Agent.count}")
        paths_lengths = [len(agent.path) for agent in Agent.population.values()]
        paths_lengths.sort()
        path_len_mean = int(sum(paths_lengths) / len(paths_lengths))
        print(f"Agents mean path len = {path_len_mean} px")
        path_len_median = paths_lengths[len(paths_lengths) // 2]
        print(f"Agents median path len = {path_len_median} px")

        # Display paths of some agents
        agents = list([a for a in Agent.population.values()])
        fig = plt.figure()
        n_rows = ceil(n_viz ** (1 / 2))
        n_cols = ceil(n_viz / n_rows)
        for i in range(n_viz):
            plt.subplot(n_rows, n_cols, i + 1)
            plt.imshow(agents[i].array_path)
            plt.title(f"Agent's n°{agents[i].id} path")
            plt.axis("off")

    def generate_actions_timeline(self, time_step):
        # TODO maybe use copy()
        # TODO look for a method to determine optimal time_step
        actives: list = [a for a in Agent.population.values() if a.path]
        inactives: list = [a for a in Agent.population.values() if not a.path]
        time = min([a.path[0].t for a in actives])
        self.universe.init_space()  # Reset universe space

        while actives:
            # Removing deads
            actives: list = [
                a for a in actives if a.death_date is None or time < a.death_date
            ]
            inactives: list = [
                a for a in inactives if a.death_date is None or time < a.death_date
            ]
            # Update time and position of active agents
            
            for agent in [a for a in actives if a.path[0].t <= time]:
                i = 0
                while agent.path and agent.path[0].t <= time:
                    i += 1
                    agent.position = agent.path.pop(0)
                if i > 1:  # TODO
                    print("JUMP")
                if not agent.path:
                    actives.remove(agent)
                    inactives.append(agent)

            # Display agents
            frame = np.ones(
                (self.universe.space.shape[0], self.universe.space.shape[1], 3),
                dtype=np.uint8,
            )
            for agent in actives + inactives:
                if agent.position.t <= time:
                    frame[agent.position.y, agent.position.x] = agent.phenome.color
            

            time += time_step

            # Yield
            yield frame
