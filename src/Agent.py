import threading
import numpy as np
from random import randint, choice
from time import sleep, perf_counter_ns
import statistics

from .Brain import Abilities
from .Phenome import Phenome
from .Universe import Universe
from .Position import Position


class Agent(threading.Thread):  # TODO make this ABC
    def __init__(
        self,
        universe: Universe,
        initial_position: Position,
        generation: int,
        parents: list,
        energy: int = None,
        phenome: Phenome = None,
        start_date: int = None,
        start_on_birth: bool = False,
        start_barrier: threading.Barrier = None,
        debug: bool = False,
    ):
        super().__init__()
        self.daemon = True
        self.debug = debug

        # Agent properties
        # Experiment related
        # Add to population dict
        self.universe = universe
        with universe.population_lock:
            self.id = len(universe.population)
            universe.population[self.id] = self
        self.stop = threading.Event()
        self.start_barrier = start_barrier

        # Constants
        self.initial_phenome = phenome if phenome is not None else Phenome()
        self.generation = generation
        self.parents = parents
        # Set once
        self.death_date = None
        self.start_date = start_date

        # Evolutives
        self.phenome = self.initial_phenome.copy()
        self.energy = energy if energy else self.phenome.energy_capacity
        self.position = initial_position
        self.path = []  # remove and post-compute with actions
        self.actions: list = []
        self.children = []

        # Adding to universe
        self.birth_success = True
        with universe.space_locks[initial_position.tuple]:
            self.spawn_date = self.universe.get_time()
            self.actions.append(
                {
                    "id": self.id,
                    "decision": "spawn",
                    "action_time": self.spawn_date,
                    "action_success": True,
                    # "reaction_time": 0,
                    # "decision_time": 0,
                }
            )

            if self.universe.is_valid(initial_position):
                self.universe[initial_position] = self
                self.path.append((self.spawn_date, self.position))
                if start_on_birth:  # Autostart
                    self.start()
            else:
                self.die()
                self.birth_success = False

        # Debug
        if self.debug:
            print(f"Agent {self.id} initialized by {parents}")

    def run(self):
        if self.start_barrier:
            self.start_barrier.wait()
        self.start_date = self.universe.get_time()
        self.actions.append(
            {
                "id": self.id,
                "decision": "start",
                "action_time": self.start_date,
                "action_success": True,
                # "reaction_time": 0,
                # "decision_time": 0,
            }
        )

        if self.debug:
            print(f"Agent {self.id} start running")

        # Lifetime
        while not self.stop.is_set() and not self.universe.freeze.is_set():
            # Minimal energy loss
            self.energy -= 1

            # Reaction time set up to set agents speed dependent of their phenome instead of
            # the CPU core its thread is running on
            sleep(self.phenome.reaction_time)  # TODO rework
            reaction_time = self.universe.get_time()

            # Decision making taking into account environment and self
            decision = self.phenome.brain(
                self.universe.get_area(self.position, self.phenome.scope)
            )
            decision_time = self.universe.get_time()

            # Decision -> Action
            action_success = False
            match decision:
                case Abilities.idle:
                    action_success, action_time = self.idle()
                case Abilities.move_bot:
                    action_success, action_time = self.move(Position(1, 0))
                case Abilities.move_top:
                    action_success, action_time = self.move(Position(-1, 0))
                case Abilities.move_left:
                    action_success, action_time = self.move(Position(0, -1))
                case Abilities.move_right:
                    action_success, action_time = self.move(Position(0, 1))
                case Abilities.eat_bot:
                    action_success, action_time = self.eat(Position(1, 0))
                case Abilities.eat_top:
                    action_success, action_time = self.eat(Position(-1, 0))
                case Abilities.eat_left:
                    action_success, action_time = self.eat(Position(0, -1))
                case Abilities.eat_right:
                    action_success, action_time = self.eat(Position(0, 1))
                case Abilities.reproduce:
                    action_success, action_time = self.reproduce()

            self.actions.append(
                {
                    "id": self.id,
                    # "reaction_time": reaction_time,
                    # "decision_time": decision_time,
                    "decision": decision.value,
                    "action_time": action_time,
                    "action_success": action_success,
                }
            )

            # Energy boundings
            if self.energy < 1:
                self.die()
            self.energy = min(self.energy, self.phenome.energy_capacity)

        # Stop the agent for monitoring
        self.stop.set()

    # SIMULATION
    def idle(self) -> tuple[bool, int]:
        self.energy += 1
        return True, self.universe.get_time()

    def move(self, relative_pos: Position) -> bool:
        # TODO Add acceleration/velocity, manage it with universe time
        # for example
        # TODO Add inertia
        self.energy -= 2
        success = False
        new_pos = self.universe.wrap_position(self.position + relative_pos)
        with self.universe.space_locks[new_pos.tuple]:
            move_time = self.universe.get_time()
            if self.universe.is_valid(new_pos):
                success = True

                # Update universe
                self.universe[self.position] = None
                self.universe[new_pos] = self

                # Update self attributes
                self.position = new_pos
                self.path.append((move_time, new_pos))

        return success, move_time

    def eat(self, relative_pos: Position) -> bool:
        success = False
        eat_pos = self.universe.wrap_position(self.position + relative_pos)
        with self.universe.space_locks[eat_pos.tuple]:
            eat_time = self.universe.get_time()
            if (  # Do not compare color
                isinstance(self.universe[eat_pos], Agent)
                and self.universe[eat_pos].phenome.color != self.phenome.color
            ):
                success = True
                self.energy += self.universe[eat_pos].energy
                self.universe[eat_pos].energy = 0

        return success, eat_time

    def reproduce(self) -> None:  # TODO Multi-agents reproduction
        birth_success = False
        self.energy -= self.energy // 2

        # Check possible positions
        # TODO use universe get_area
        reproduction_time = self.universe.get_time()

        possible_positions = []
        for y in range(-1, 2):
            for x in range(-1, 2):
                pos = self.position + Position(y=y, x=x)
                if self.universe.is_valid(pos):
                    possible_positions.append(pos)

        # Newborn to life if possible
        if possible_positions:
            child_pos = choice(possible_positions)
            if self.universe.is_valid(child_pos):
                child = Agent(
                    universe=self.universe,
                    initial_position=child_pos,
                    generation=self.generation + 1,
                    phenome=self.initial_phenome.copy(),  # TODO Use phenome.mutate()
                    energy=self.energy // 2,
                    start_on_birth=True,
                    parents=[self],
                )
                self.children.append(child)
                birth_success = child.birth_success

        return birth_success, reproduction_time

    def die(self):
        self.stop.set()
        self.death_date = self.universe.get_time()
        self.universe[self.position] = None  # Remove itself from universe
        self.actions.append(
            {
                "id": self.id,
                "decision": "die",
                "action_time": self.death_date,
                "action_success": True,
                # "reaction_time": 0,
                # "decision_time": 0,
            }
        )

        if self.debug:
            print(f"Agent {self.id} died")

    # UTILITIES
    def copy(self):
        # TODO
        pass

    # DATA
    def get_data(self) -> dict:
        # Attributes and lifespan
        data = {
            "id": self.id,
            "generation": self.generation,
            "parents_count": 1 if self.parents is None else len(self.parents),
            "dead": False if self.death_date is None else True,
            "lifespan": self.universe.culmination - self.spawn_date
            if self.death_date is None
            else self.death_date - self.spawn_date,
            "children_count": len(self.children),
            "birth_success": self.birth_success,
            "travelled_distance": max(len(self.path) - 1, 0),
        }

        # Activity track TODO def func
        data["actions_count"] = len(self.actions)

        decision_durations = [
            b - a
            for b, a in zip(
                self.actions["decision_time"], self.actions["reaction_time"]
            )
        ]
        data["min_decision_duration"] = (
            None if len(decision_durations) < 1 else min(decision_durations)
        )
        data["max_decision_duration"] = (
            None if len(decision_durations) < 1 else max(decision_durations)
        )
        data["mean_decision_duration"] = (
            None if len(decision_durations) < 1 else statistics.mean(decision_durations)
        )
        data["median_decision_duration"] = (
            None
            if len(decision_durations) < 1
            else statistics.median(decision_durations)
        )
        data["std_decision_duration"] = (
            None
            if len(decision_durations) < 2
            else statistics.stdev(decision_durations)
        )

        action_durations = [
            b - a
            for b, a in zip(self.actions["action_time"], self.actions["decision_time"])
        ]
        data["min_action_duration"] = (
            None if len(action_durations) < 1 else min(action_durations)
        )
        data["max_action_duration"] = (
            None if len(action_durations) < 1 else max(action_durations)
        )
        data["mean_action_duration"] = (
            None if len(action_durations) < 1 else statistics.mean(action_durations)
        )
        data["median_action_duration"] = (
            None if len(action_durations) < 1 else statistics.median(action_durations)
        )
        data["std_action_duration"] = (
            None if len(action_durations) < 2 else statistics.stdev(action_durations)
        )

        # Meta-data
        round_timers = [a for a in self.actions["action_time"]]
        round_durations = [
            round_timers[i + 1] - round_timers[i] for i in range(len(round_timers) - 1)
        ]
        data["min_round_duration"] = (
            None if len(round_durations) < 1 else min(round_durations)
        )
        data["max_round_duration"] = (
            None if len(round_durations) < 1 else max(round_durations)
        )
        data["mean_round_duration"] = (
            None if len(round_durations) < 1 else statistics.mean(round_durations)
        )
        data["median_round_duration"] = (
            None if len(round_durations) < 1 else statistics.median(round_durations)
        )
        data["std_round_duration"] = (
            None if len(round_durations) < 2 else statistics.stdev(round_durations)
        )

        return data

    # VISUALIZATION
    @property
    def array_path(self):  # TODO rework
        array_path = np.zeros((self.universe.height, self.universe.width))
        for step in self.path:
            array_path[step.tuple] = 255
        return array_path

    # REPRESENTATION
    def __repr__(self):
        return f"a_{self.id}"

    def __str__(self):
        ID = f"ID: {self.id:-3d}"
        GEN = f"GEN: {self.generation:-3d}"
        start = -1 if self.start_date is None else self.start_date
        BIRTH = f"BIRTH: {int(start/1e6):-6d} ms"
        death = -1 if self.death_date is None else self.death_date
        DEATH = f"DEATH: {int(death/1e6):-6d} ms"
        POS = f"POS: {self.position}"
        return f"{ID} | {GEN} | {BIRTH} | {DEATH} | {POS}"

    # SAVE TODO refactor
    def to_dict(self):
        data = {
            "id": self.id,
            "generation": self.generation,
            "parents": [p.id for p in self.parents if isinstance(p, Agent)],
            "start_date": self.start_date,
            "death_date": self.death_date,
            "children": [c.id for c in self.children],
            "birth_success": self.birth_success,
        }
        data.update(self.phenome.to_dict())
        return data
