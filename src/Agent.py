import threading
import numpy as np
from random import randint, choice
from time import sleep, perf_counter_ns

from .Brain import Abilities
from .Phenome import Phenome
from .Universe import Universe
from .Position import Position


class Agent(threading.Thread):
    def __init__(
        self,
        universe: Universe,
        initial_position: Position,
        generation: int,
        parents: list,
        energy: int = None,
        phenome: Phenome = None,
        birth_date: int = None,
        start_on_birth: bool = False,
        start_barrier: threading.Barrier = None,
    ):
        super().__init__()

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
        self.birth_date = birth_date if birth_date else self.universe.get_time()
        self.death_date = None

        # Evolutives
        self.phenome = self.initial_phenome.copy()
        self.energy = energy if energy else self.phenome.energy_capacity
        self.position = initial_position
        self.path = []
        self.actions: list = []
        self.children = []

        # Adding to universe
        self.birth_success = True
        with universe.space_locks[initial_position.tuple]:
            if self.universe.is_valid(initial_position):
                self.universe[initial_position] = self
                if start_on_birth:  # Autostart
                    self.start()
            else:
                self.die()
                self.birth_success = False

        # Debug
        # print(
        #     f"Agent {self.id} initialized by {'Universe' if parents is None else parents}"
        # )

    def run(self):
        if self.start_barrier:
            self.start_barrier.wait()
            # print(f"Agent {self.id} start running")
            self.birth_date = self.universe.get_time()
        self.path.append((self.birth_date, self.position))

        # Lifetime
        while (
            not self.stop.is_set() and not self.universe.freeze.is_set()
        ):  # Reaction time set up to set agents speed dependent of their phenome instead of
            # the CPU core its thread is running on
            sleep(self.phenome.reaction_time)  # TODO rework

            # Minimal energy loss
            self.energy -= 1

            # Decision making taking into account environment and self
            decision = self.phenome.brain(
                self.universe.get_area(self.position, self.phenome.scope)
            )
            decision_time = self.universe.get_time()

            # Decision -> Action
            action_success = False
            match decision:
                case Abilities.idle:
                    self.energy += 4
                    action_success = True
                case Abilities.move_bot:
                    self.energy -= 4
                    if self.move(Position(1, 0)):
                        self.energy -= 4
                        action_success = True
                case Abilities.move_top:
                    self.energy -= 4
                    if self.move(Position(-1, 0)):
                        self.energy -= 4
                        action_success = True
                case Abilities.move_left:
                    self.energy -= 4
                    if self.move(Position(0, 1)):
                        self.energy -= 4
                        action_success = True
                case Abilities.move_right:
                    self.energy -= 4
                    if self.move(Position(0, -1)):
                        self.energy -= 4
                        action_success = True
                case Abilities.reproduce:
                    self.energy -= 1
                    if self.energy >= self.phenome.energy_capacity // 2:
                        self.energy -= self.energy // 2
                        action_success = self.reproduce()
            self.actions.append((decision_time, decision, action_success))

            # Energy boundings
            if self.energy < 1:
                self.die()
            self.energy = min(self.energy, self.phenome.energy_capacity)

        # Stop the agent for monitoring
        self.stop.set()

    def move(self, relative_pos: Position) -> bool:
        # TODO Add acceleration/velocity, manage it with universe time
        # for example
        # TODO Add inertia
        success = False
        new_pos = self.universe.wrap_position(self.position + relative_pos)
        with self.universe.space_locks[new_pos.tuple]:
            if self.universe.is_valid(new_pos):
                success = True

                # Update universe
                self.universe[self.position] = None
                self.universe[new_pos] = self

                # Update self attributes
                self.position = new_pos
                self.path.append(new_pos)

        return success

    def reproduce(self) -> None:  # TODO Multi-agents reproduction
        birth_success = False

        # Check possible positions
        # TODO use universe get_area

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

        return birth_success

    def die(self):
        self.death_date = self.universe.get_time()
        self.stop.set()
        # print(f"Agent {self.id} died")

    def copy(self):
        # TODO
        pass

    @property
    def array_path(self):
        array_path = np.zeros((self.universe.height, self.universe.width))
        for step in self.path:
            array_path[step.tuple] = 255
        return array_path

    def __repr__(self):
        return f"a_{self.id}"

    def __str__(self):
        ID = f"ID: {self.id:-3d}"
        GEN = f"GEN: {self.generation:-3d}"
        BIRTH = f"BIRTH: {int(self.birth_date/1e6):-6d} ms"
        death = -1 if self.death_date is None else self.death_date
        DEATH = f"DEATH: {int(death/1e6):-6d} ms"
        POS = f"POS: {self.position}"
        return f"{ID} | {GEN} | {BIRTH} | {DEATH} | {POS}"
