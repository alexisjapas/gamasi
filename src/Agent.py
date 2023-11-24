import threading
import numpy as np
from random import randint


class Agent(threading.Thread):
    current_count = 0
    total_count = 0

    def __init__(
        self,
        population_map: np.array,
        map_lock: threading.Lock,
        initial_position: (int, int),
        generation: int,
    ):
        # Agent properties
        self.position = initial_position
        self.generation = generation
        self.age = 0
        self.id = Agent.total_count

        # Map
        self.map_lock = map_lock
        self.population_map = population_map
        with map_lock:
            self.population_map[initial_position] = self

        # Increment agents counters
        Agent.current_count += 1
        Agent.total_count += 1

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
