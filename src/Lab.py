import threading
import numpy as np
from random import shuffle, randint
from time import sleep
from matplotlib import pyplot as plt
from math import ceil
from enum import Enum
from time import perf_counter_ns
from tqdm import tqdm

from .Universe import Universe
from .Agent import Agent
from .Position import Position


class Distributions(Enum):
    random = "random"


class Lab:
    def experiment(
        self,
        height: int,
        width: int,
        initial_population_count: int,
        max_duration: int,
        verbose: bool = True,
    ) -> dict:
        assert initial_population_count <= height * width

        # Init outputs
        parameters = {
            "height": height,
            "width": width,
            "initial_population_count": initial_population_count,
            "max_duration": max_duration,
        }
        timings = {}

        # Universe
        if verbose:
            print("Generating universe...", end="\t")
        universe = Universe(height=height, width=width)
        timings["init_universe"] = perf_counter_ns() - universe.genesis
        if verbose:
            print(f": Done in {(timings['init_universe'] / 1e9):.3f} s")

        # Invoke population
        self._invoke_initial_population(
            universe, height, width, initial_population_count, verbose
        )
        assert np.sum(universe.space != None) == initial_population_count
        timings["invoke_initial_population"] = perf_counter_ns() - universe.genesis

        # Start population
        non_agents_threads = threading.active_count()
        self._start_initial_population(universe, verbose)
        timings["start_initial_population"] = perf_counter_ns() - universe.genesis

        # Run
        early_stop = False
        start_running = perf_counter_ns()
        max_duration -= max(0, int((start_running - universe.genesis) / 1e9))
        for i in tqdm(
            range(max_duration, 0, -1),
            desc="Running simulation\t",
            disable=not verbose,
            colour="yellow",
        ):
            if threading.active_count() <= non_agents_threads:
                if verbose:
                    print(f"Simulation early stop\t: All entities died.")
                early_stop = True
                break
            t = (perf_counter_ns() - start_running) / 1e9  # Avoiding time drift
            sleep(max(1 + max_duration - i - t, 0))
        timings["run"] = perf_counter_ns() - universe.genesis

        # Stop
        universe.freeze.set()
        if not early_stop:
            self._stop_population(universe, verbose)
        timings["stop"] = perf_counter_ns() - universe.genesis

        if verbose:
            print("Simulation succeed...\t: Returning data...")

        return {"parameters": parameters, "timings": timings, "universe": universe}

    def _generate_position(self, positions: list[Position], height: int, width: int):
        new_pos = Position(
            y=randint(0, height - 1), x=randint(0, width - 1)
        )
        if new_pos not in positions:
            return new_pos
        else:
            return self._generate_position(positions, height, width)

    def _invoke_initial_population(
        self,
        universe: Universe,
        height: int,
        width: int,
        initial_population_count: int,
        verbose: bool,
        distribution: Distributions = Distributions.random,
    ) -> None:
        positions = []
        match distribution:
            case Distributions.random:
                for _ in tqdm(
                    range(initial_population_count),
                    desc="Generating positions\t",
                    disable=not verbose,
                    colour="magenta",
                ):
                    positions.append(self._generate_position(positions, height, width))
            case _:
                raise ValueError(
                    f"Possible distributions: {[d.name for d in Distributions]}"
                )
        start_barrier = threading.Barrier(parties=initial_population_count)
        for pos in tqdm(
            positions, "Invoking population\t", disable=not verbose, colour="blue"
        ):
            Agent(
                universe=universe,
                initial_position=pos,
                generation=0,
                parents=None,
                start_barrier=start_barrier,
            )

    def _start_initial_population(self, universe, verbose: bool) -> None:
        with universe.population_lock:
            for agent in tqdm(
                universe.population.values(),
                desc="Starting population\t",
                disable=not verbose,
                colour="green",
            ):
                agent.start()

    def _stop_population(self, universe, verbose: bool) -> None:
        with universe.population_lock:  # TODO Add priority to this lock
            for agent in tqdm(
                universe.population.values(),
                desc="Stopping population\t",
                disable=not verbose,
                colour="red",
            ):
                agent.stop.set()

    def analyze(self, simulation: dict):
        print(simulation)
        for agent in simulation.universe.population:
            pass

    ##############################################################################

    def vizuaanalyze(self, n_viz=4):  # TODO Copy agents until analyse
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
