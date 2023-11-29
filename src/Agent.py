import threading
import numpy as np
from random import randint
from time import sleep

from Genome import Genome
from Space import Space
from Position import Position


class Agent(threading.Thread):
    current_count = 0
    total_count = 0

    def __init__(
        self,
        space: Space,
        initial_position: Position,
        generation: int,
    ):
        super().__init__()

        # Genome
        self.genome = Genome()

        # Agent properties
        self.position = initial_position
        self.path = [initial_position]
        self.generation = generation
        self.age = 0
        self.id = Agent.total_count
        self.die = threading.Event()

        # Space
        self.space = space
        with space.lock:
            self.space[initial_position] = self

        # Increment agents counters
        Agent.current_count += 1
        Agent.total_count += 1

        # Debug
        print(f"Agent {self.id} initialized")

    def run(self):
        print(f"Agent {self.id} start running")
        while not self.die.is_set():
            sleep(self.genome.reaction_time)
            self.move(
                Position(randint(-1, 1), randint(-1, 1), genesis=self.space.genesis)
            )

    def move(self, relative_pos: Position):
        new_pos = self.position + relative_pos
        with self.space.lock:
            if self.space.is_valid(new_pos):
                # Update space
                self.space[self.position] = None
                self.space[new_pos] = self

                # Update self attributes
                self.position = new_pos
                self.path.append(new_pos)

    def kill(self):
        self.die.set()

    @property
    def array_path(self):
        array_path = np.zeros((self.space.height, self.space.width))
        for step in self.path:
            array_path[step.tuple] = int(
                (step.t - self.path[0].t) / (self.path[-1].t - self.path[0].t) * 255
            )
        return array_path

    def __del__(self):
        Agent.current_count -= 1

    def __repr__(self):
        return f"{self.id}"

    def __str__(self):
        ID = f"ID: {self.id:05d}"
        GEN = f"GEN: {self.generation:05d}"
        AGE = f"AGE: {self.age:05}"
        POS = f"POS: {self.position}"
        return f"{ID} | {GEN} | {AGE} | {POS}\n"
