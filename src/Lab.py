import threading
import numpy as np
from random import shuffle, randint
from time import sleep
from matplotlib import pyplot as plt
from math import ceil
from enum import Enum
from time import perf_counter_ns

from .Universe import Universe
from .Agent import Agent
from .Position import Position


class Distributions(Enum):
    random = "random"


class Lab:
    def experiment(
        self, height: int, width: int, initial_population_count: int, max_duration: int
    ) -> dict:
        assert initial_population_count <= height * width

        # Universe
        universe = Universe(height=height, width=width)

        # Invoke population
        self._invoke_population(universe, height, width, initial_population_count)
        print(np.sum(universe.space != None))
        assert np.sum(universe.space != None) == initial_population_count

        # Start population
        non_agents_threads = threading.active_count()
        self._start_initial_population(universe)

        # Run
        start = perf_counter_ns()
        while max_duration > 0 and threading.active_count() > non_agents_threads:
            sleep(0.1)
            max_duration -= 0.1

        for th in threading.enumerate():
            if isinstance(th, Agent):
                print(th)
        print(f"Experiment max_duration: {perf_counter_ns() - start}")

        # Stop
        universe.freeze.set()
        self._stop_population(universe)

        return {"universe": universe}

    def _invoke_population(
        self,
        universe: Universe,
        height: int,
        width: int,
        initial_population_count: int,
        distribution: Distributions = Distributions.random,
    ) -> None:
        positions = []
        match distribution:
            case Distributions.random:
                while len(positions) < initial_population_count:
                    new_pos = Position(
                        randint(0, height - 1),
                        randint(0, width - 1),
                    )
                    if new_pos not in positions:
                        positions.append(new_pos)
            case _:
                raise ValueError(
                    f"Possible distributions: {[d.name for d in Distributions]}"
                )
        print(positions)
        start_barrier = threading.Barrier(parties=initial_population_count)
        [
            Agent(
                universe=universe,
                initial_position=pos,
                generation=0,
                parents=None,
                start_barrier=start_barrier,
            )
            for pos in positions
        ]

    def _start_initial_population(self, universe) -> None:
        with universe.population_lock:
            for agent in universe.population.values():
                agent.start()
            print("Agents started")

    def _stop_population(self, universe) -> None:
        with universe.population_lock:  # TODO Add priority to this lock
            for agent in universe.population.values():
                agent.stop.set()

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
        # TODO call it from analyze
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
