import threading
import numpy as np
from random import randint, choice
from time import sleep, perf_counter_ns

from .Phenome import Phenome, Abilities
from .Universe import Universe
from .Position import Position


class Agent(threading.Thread):
    living_lock = threading.Lock()
    living = {}
    dead_lock = threading.Lock()
    dead = {}

    def __init__(
        self,
        universe: Universe,
        initial_position: Position,
        generation: int,
        parents: list,
        phenome: Phenome = None,
        birth_date: int = None,
        start_on_birth: bool = False,
    ):
        super().__init__()

        # Agent properties TODO attributes structuring
        if phenome is None:
            phenome = Phenome()
        self.initial_phenome = phenome
        self.phenome = phenome
        self.position = initial_position
        self.path = [initial_position]  # TODO change it into an actions stacktrace
        self.generation = generation
        self.birth_date = birth_date
        self.death_date = None
        self.parents = parents
        self.start_on_birth = start_on_birth
        with Agent.living_lock:
            with Agent.dead_lock:
                self.id = len(Agent.living) + len(Agent.dead)
            Agent.living[self.id] = self
        self.childrens = []
        self.stop = threading.Event()
        self.color = (randint(22,222), randint(22,222),randint(22,222))  # TODO Keep it?

        # Universe
        self.universe = universe
        with universe.lock:
            if self.universe.is_valid(initial_position):
                self.universe[initial_position] = self
                if self.start_on_birth:
                    self.start()
            else:
                self.die()

        # Debug
        print(
            f"Agent {self.id} initialized by {'Universe' if parents is None else parents}"
        )

    def run(self):
        print(f"Agent {self.id} start running")
        # Birth
        if self.position.t is None:
            # As universe genesis can be started here, the first value
            # of the time dimension of the first activated agent
            # is equivalent to the time of the call of the function
            # TODO is this conceptually optimal?
            self.position.start_time(genesis=self.universe.genesis)
        if self.birth_date is None:  # Get the value of the first position it has
            self.birth_date = self.path[0].t

        # Lifetime
        while not self.stop.is_set():  # TODO rework energy loss
            # Minimal energy loss
            self.phenome.energy -= 1

            # Decision making taking into account environment and self
            decision = self.phenome.brain(self._perceive_environment())

            # Try to apply its decision
            match decision:
                case Abilities.idle:
                    pass
                case Abilities.move:
                    self.phenome.energy -= 2
                    if self.move(
                        Position(
                            randint(-1, 1),
                            randint(-1, 1),
                            genesis=self.universe.genesis,
                        )
                    ):
                        self.phenome.energy -= 2
                case Abilities.reproduce:
                    self.phenome.energy -= 10
                    if (
                        self.phenome.energy >= 20
                        and self.universe.get_time() - self.birth_date >= 1e9
                        and len(Agent.living) < 20
                        and self.reproduce()
                    ):
                        print(len(Agent.living))
                        self.phenome.energy -= 20

            # Reaction time set up to set agents speed dependent of their phenome instead of
            # the CPU core its thread is running on
            sleep(self.phenome.reaction_time)  # TODO rework

            # Die if energy < 1
            if self.phenome.energy < 1:
                self.die()

    def _perceive_environment(self):
        environment = None
        with self.universe.lock:
            environment = self.universe.get_area(self.position, self.phenome.scope)

        return environment

    def move(self, relative_pos: Position) -> bool:  # Add acceleration/velocity
        sleep(1 / (2 * self.phenome.speed))
        success = False
        with self.universe.lock:
            new_pos = self.universe.is_valid(self.position + relative_pos)
            if new_pos:
                success = True

                # Update universe
                self.universe[self.position] = None
                self.universe[new_pos] = self

                # Update self attributes
                self.position = new_pos
                self.path.append(new_pos)
                sleep(1 / (2 * self.phenome.speed))
        return success

    def reproduce(self) -> None:  # TODO Multi-agents reproduction
        # Check possible positions
        possible_positions = []
        for y in range(-1, 2):
            for x in range(-1, 2):
                pos = self.position + Position(y, x, self.universe.genesis)
                if self.universe.is_valid(pos):
                    possible_positions.append(pos)

        # Newborn to life if possible
        if possible_positions:  # TODO Verify here if isvalid with lock
            Agent(
                universe=self.universe,
                initial_position=choice(possible_positions),
                generation=self.generation + 1,
                phenome=self.phenome.mutate(),
                start_on_birth=True,
                parents=[self],
            )

    def die(self):
        with Agent.living_lock:
            dead = Agent.living.pop(self.id)
        with Agent.dead_lock:
            Agent.dead[self.id] = dead
        self.death_date = self.universe.get_time()
        self.stop.set()
        print(f"Agent {self.id} died")

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
        death = 0 if self.death_date is None else self.death_date
        DEATH = f"DEATH: {int(death/1e6):-6d} ms"
        POS = f"POS: {self.position}"
        return f"{ID} | {GEN} | {BIRTH} | {DEATH} | {POS}"
