import threading
import numpy as np
from random import randint
from time import sleep

from .Genome import Genome
from .Space import Space
from .Position import Position


class Agent(threading.Thread):
    living_lock = threading.Lock()
    living = {}
    dead_lock = threading.Lock()
    dead = {}

    def __init__(
        self,
        space: Space,
        initial_position: Position,
        generation: int,
        genome: Genome = None,
    ):
        super().__init__()

        # Genome TODO change names
        if genome is None:
            genome = Genome()
        self.genome = genome  # hereditary
        self.phenotype = genome

        # Agent properties
        self.position = initial_position
        self.path = [initial_position]
        self.generation = generation
        self.age = 0
        with Agent.living_lock:
            with Agent.dead_lock:
                self.id = len(Agent.living) + len(Agent.dead)
        self.childrens = []
        self.stop = threading.Event()

        # Space
        self.space = space
        with space.lock:
            self.space[initial_position] = self

        # Add to living list
        with Agent.living_lock:
            Agent.living[self.id] = self

        # Debug
        print(f"Agent {self.id} initialized")

    def run(self):
        print(f"Agent {self.id} start running")
        while not self.stop.is_set():
            sleep(self.phenotype.reaction_time)
            self.move(
                Position(randint(-1, 1), randint(-1, 1), genesis=self.space.genesis)
            )

    def move(self, relative_pos: Position) -> bool:
        sleep(1 / (2 * self.phenotype.speed))
        success = False
        new_pos = self.position + relative_pos
        with self.space.lock:
            if self.space.is_valid(new_pos):
                success = True

                # Update space
                self.space[self.position] = None
                self.space[new_pos] = self

                # Update self attributes
                self.position = new_pos
                self.path.append(new_pos)
                sleep(1 / (2 * self.phenotype.speed))
        return success

    def reproduce(self) -> None:  # TODO Multi-agents reproduction
        success = False

        # Check possible positions
        possible_positions = []
        for y in range(-1, 2):
            for x in range(-1, 2):
                pos = self.position + Position(y, x, self.space.genesis)
                if self.space.is_valid(pos):
                    possible_positions.append(pos)

        # Newborn to life if possible
        if possible_positions:
            success = True

            with Agent.living_lock:
                Agent.living.append(
                    Agent(
                        space=self.space,
                        initial_position=None,
                        generation=self.generation + 1,
                        genome=self.genome.mutate(),
                    )
                )

        return success

    def kill(self):
        with Agent.living_lock:
            dead = Agent.living.pop(self.id)
        with Agent.dead_lock:
            Agent.dead[self.id] = dead
        self.stop.set()

    @property
    def array_path(self):
        array_path = np.zeros((self.space.height, self.space.width))
        for step in self.path:
            array_path[step.tuple] = int(
                (step.t - self.path[0].t) / (self.path[-1].t - self.path[0].t) * 255
            )
        return array_path

    def __repr__(self):
        return f"{self.id}"

    def __str__(self):
        ID = f"ID: {self.id:05d}"
        GEN = f"GEN: {self.generation:05d}"
        AGE = f"AGE: {self.age:05}"
        POS = f"POS: {self.position}"
        return f"{ID} | {GEN} | {AGE} | {POS}\n"
