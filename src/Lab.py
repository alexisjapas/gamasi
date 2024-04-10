import threading
import numpy as np
import pandas as pd
from random import randint
from time import sleep
from matplotlib import pyplot as plt
import seaborn as sns
from math import ceil
from enum import Enum
from tqdm import tqdm

from .Universe import Universe
from .Agent import Agent
from .Position import Position


class Distributions(Enum):
    random = "random"


class Lab:
    # SIMULATION
    def experiment(
        self,
        height: int,
        width: int,
        initial_population_count: int,
        max_total_duration: int,
        max_simulation_duration: int,
        verbose: bool = True,
    ) -> dict:
        assert initial_population_count <= height * width

        # Init outputs
        parameters = {
            "height": height,
            "width": width,
            "initial_population_count": initial_population_count,
            "max_total_duration": max_total_duration,
            "max_simulation_duration": max_simulation_duration,
        }
        timings = {}

        # Universe
        if verbose:
            print("Generating universe...", end="\t")
        universe = Universe(height=height, width=width)
        timings["init_universe"] = universe.get_time()
        if verbose:
            print(f": Done in {(timings['init_universe'] / 1e9):.3f} s")

        # Invoke population
        self._invoke_initial_population(
            universe, height, width, initial_population_count, verbose
        )
        assert (
            np.sum(universe.space != None) == initial_population_count
        )  # Positions are uniques
        timings["invoke_initial_population"] = universe.get_time()

        # Start population
        non_agents_threads = threading.active_count()
        self._start_initial_population(universe, verbose)
        timings["start_initial_population"] = universe.get_time()

        # Run
        early_stop = False
        start_running = universe.get_time()
        total_duration_remaining = max_total_duration - max(0, int(start_running / 1e9))
        simulation_duration = min(total_duration_remaining, max_simulation_duration)
        for i in tqdm(
            range(simulation_duration, 0, -1),
            desc="Running simulation\t",
            disable=not verbose,
            colour="yellow",
        ):
            if threading.active_count() <= non_agents_threads:
                if verbose:
                    print(f"Simulation early stop\t: All entities died.")
                early_stop = True
                break
            t = (universe.get_time() - start_running) / 1e9  # Avoiding time drift
            sleep(max(1 + simulation_duration - i - t, 0))
        timings["run"] = universe.get_time()

        # Stop
        universe.freeze.set()
        first_iteration = True
        active_agents = threading.active_count() - non_agents_threads
        while active_agents > 0:
            if first_iteration:
                print(f"Interrupting population\t: {active_agents}...")
                first_iteration = False
            else:
                print(f"\t\t\t| {active_agents}...")
            sleep(1e-1)
            active_agents = threading.active_count() - non_agents_threads
        universe.culmination = universe.get_time()
        timings["stop"] = universe.culmination

        if verbose:
            print(
                f"Simulation succeed...\t: Returning data... Done in {(timings['stop'] / 1e9):.3f} s"
            )

        return {"parameters": parameters, "timings": timings, "universe": universe}

    def _generate_position(self, positions: list[Position], height: int, width: int):
        new_pos = Position(y=randint(0, height - 1), x=randint(0, width - 1))
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
        # For the moment it is unused, but to enable universe to unfreeze, it'll be needed
        with universe.population_lock:  # TODO Add priority to this lock
            for agent in tqdm(
                universe.population.values(),
                desc="Stopping population\t",
                disable=not verbose,
                colour="red",
            ):
                agent.stop.set()

    # ANALYSIS
    def gather_data(self, simulation: dict, verbose: bool = True) -> dict:
        # TODO copy the universe to not alter it
        # Individuals statistics
        agents_statistics = []
        for a_id, agent in tqdm(
            simulation["universe"].population.items(),
            desc="Computing agents statistics\t",
            disable=not verbose,
            colour="red",
        ):
            agents_statistics.append(agent.get_data())

        agents_statistics_df = pd.DataFrame(agents_statistics)
        agents_statistics_df.set_index("id", inplace=True)

        # Population statistics
        computed_data = [
            "lifespan",
            "children_count",
            "birth_success",
            "travelled_distance",
            "actions_count",
            "mean_decision_duration",
            "mean_action_duration",
            "mean_round_duration",
        ]
        population_statistics = []
        for cp in computed_data:
            population_statistics.append(
                {
                    "data": cp,
                    "min": agents_statistics_df[cp].min(),
                    "max": agents_statistics_df[cp].max(),
                    "mean": agents_statistics_df[cp].mean(),
                    "median": agents_statistics_df[cp].median(),
                    "std": agents_statistics_df[cp].std(),
                }
            )
        population_statistics_df = pd.DataFrame(population_statistics)
        population_statistics_df.set_index("data", inplace=True)

        # Population count timeline TODO its wrong
        birth_timeline = [a.birth_date for a in simulation["universe"].population.values()]
        birth_timeline.sort()
        death_timeline = [a.death_date for a in simulation["universe"].population.values() if a.death_date]
        death_timeline.sort()

        population_count = 0
        population_timeline = []
        while birth_timeline or death_timeline:
            # Trick to get min between the first element of two lists of different size
            birth = float("inf") if not birth_timeline else birth_timeline[0]
            death = float("inf") if not death_timeline else death_timeline[0]
            if birth < death:
                t = birth_timeline.pop(0)
                population_count += 1
            else:
                t = death_timeline.pop(0)
                population_count -= 1
            population_timeline.append({"t": t, "population_count": population_count})
        population_timeline_df = pd.DataFrame(population_timeline)
        population_timeline_df.set_index("t", inplace=True)

        # Positions timeline
        positions_timeline = self.get_spatial_frames(simulation)

        # Actions timelines TODO
        actions_timeline = []
        for a_id, agent in tqdm(
            simulation["universe"].population.items(),
            desc="Gathering timelines\t\t",
            disable=not verbose,
            colour="red",
        ):
            pass

        return {
            "agents_statistics": agents_statistics_df,
            "population_statistics": population_statistics_df,
            "population_timeline": population_timeline_df,
            "positions": positions_timeline,
            "actions": actions_timeline,
        }

    def get_spatial_frames(self, simulation):
        # TODO look for a method to determine optimal linear time step
        # Probably something like finding the GCD of all time steps

        frames_shape = simulation["universe"].space.shape
        frames = []
        timestamps = []
        next_moves = [a.path[0][0] for a in simulation["universe"].population.values() if a.path]
        next_timestamp = None if not next_moves else min(next_moves)
        disabled_agents = [a for a in simulation["universe"].population.values()]
        enabled_agents = []

        while next_timestamp < float("inf"):
            # Timestamp
            timestamps.append(next_timestamp)
            next_moves = [a.path[1][0] for a in simulation["universe"].population.values() if len(a.path) >= 2]
            next_timestamp = float("inf") if not next_moves else min(next_moves)

            # Enabling agents
            for a in disabled_agents:
                if a.path and a.path[0][0] < next_timestamp:
                    disabled_agents.remove(a)
                    enabled_agents.append(a)

            # Updating enabled positions
            for a in enabled_agents:
                if not a.path:
                    enabled_agents.remove(a)
                elif a.path[0][0] < next_timestamp:
                    a.position = a.path[0][1]
                    a.path.pop(0)

            # Create frame with enabled agents
            frame = np.ones((*frames_shape, 3), dtype=np.uint8)
            for a in enabled_agents:
                frame[a.position.y, a.position.x] = a.phenome.color
            
            frames.append(frame)
        return timestamps, frames

    # VISUALIZATION
    def plot_generation_stats(self, data):
        # Set up subplots
        fig, axes = plt.subplots(2, 3, figsize=(14, 10))

        # Plotting the count of agents for each generation
        ax = axes[0, 0]
        sns.countplot(x="generation", data=data["agents_statistics"], ax=ax)
        ax.set_title("Count of Agents for Each Generation")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Count of Agents")

        # Proportion of dead agents for each generation
        ax = axes[0, 1]
        proportion_dead = data["agents_statistics"].groupby("generation")["dead"].mean()
        sns.barplot(x=proportion_dead.index, y=proportion_dead.values, ax=ax)
        ax.set_title("Proportion of Dead Agents for Each Generation")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Proportion of Dead Agents")

        # Lifespan
        ax = axes[0, 2]
        sns.violinplot(
            x="generation", y="lifespan", data=data["agents_statistics"], ax=ax
        )
        ax.set_title("Lifespan vs Generation")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Lifespan")

        # Children count
        ax = axes[1, 0]
        sns.violinplot(
            x="generation", y="children_count", data=data["agents_statistics"], ax=ax
        )
        ax.set_title("Children count vs Generation")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Children count")

        # Actions count
        ax = axes[1, 1]
        sns.violinplot(
            x="generation", y="actions_count", data=data["agents_statistics"], ax=ax
        )
        ax.set_title("Actions count vs Generation")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Actions count")

        # Median round duration
        ax = axes[1, 2]
        sns.violinplot(
            x="generation",
            y="median_round_duration",
            data=data["agents_statistics"],
            ax=ax,
        )
        ax.set_title("Median round duration vs Generation")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Median round duration")

        # Adjust layout
        plt.tight_layout()

        # Show plot
        plt.show()
