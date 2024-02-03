import threading
import numpy as np
from time import perf_counter_ns

from .Position import Position


# TODO get space...
class Universe:
    """
    This class control & lock space & time
    """

    def __init__(self, height: int, width: int):
        self.height: int = height
        self.width: int = width
        self.genesis = perf_counter_ns()
        self.freeze: bool = False  # TODO verify optimality
        self.init_space()

    def init_space(self):
        # Space
        self.space: np.array = np.full(
            shape=(self.height, self.width), fill_value=None, dtype=object
        )

        # Locks
        self.space_locks: np.array = np.empty(
            shape=(self.height, self.width), dtype=object
        )
        for y in range(self.height):
            for x in range(self.width):
                self.space_locks[y, x] = threading.Lock()

    def wrap_position(self, pos: Position):
        # Used on every pos input
        pos.y = pos.y % self.height
        pos.x = pos.x % self.width
        return pos

    def is_valid(
        self, pos: Position
    ):  # TODO rename or refactor (stop returning bool or pos)
        pos = self.wrap_position(pos)
        return pos if self.space[pos.tuple] is None else False

    def get_area(self, pos: Position, scope: int) -> np.array:
        # Returns an area of the space given a position and a scope.
        # Behaves like a torus
        assert isinstance(pos, Position)
        assert (
            scope > 0 and self.height >= 2 * scope + 1 and self.width >= 2 * scope + 1
        )
        area = np.full(
            shape=(2 * scope + 1, 2 * scope + 1), fill_value=None, dtype=object
        )

        # Central area
        min_y = max(pos.y - scope, 0)
        max_y = min(pos.y + scope, self.height - 1)
        min_x = max(pos.x - scope, 0)
        max_x = min(pos.x + scope, self.width - 1)
        area = self.space

        # Y overflow
        top_overflow = 0
        if pos.y - scope < 0:  # Adding bot area to top center
            top_overflow = scope - pos.y
            bot = area[self.height - top_overflow : self.height, :]
            area = np.concatenate(
                (bot, area),
                axis=0,
            )
        elif pos.y + scope >= self.height:  # Adding top area to bot center
            bot_overflow = pos.y + scope + 1 - self.height
            top = area[0:bot_overflow, :]
            area = np.concatenate(
                (area, top),
                axis=0,
            )

        # X overflow
        left_overflow = 0
        if pos.x - scope < 0:  # Adding right area to left center
            left_overflow = scope - pos.x
            right = area[:, self.width - left_overflow : self.width]
            area = np.concatenate(
                (right, area),
                axis=1,
            )
        elif pos.x + scope >= self.width:  # Adding left area to right center
            right_overflow = pos.x + scope + 1 - self.width
            left = area[:, 0:right_overflow]
            area = np.concatenate(
                (area, left),
                axis=1,
            )

        return area[
            pos.y - scope + top_overflow : pos.y + scope + 1 + top_overflow,
            pos.x - scope + left_overflow : pos.x + scope + 1 + left_overflow,
        ]

    def get_time(self) -> int:
        return perf_counter_ns() - self.genesis

    def get_displayable(self):
        displayable_array: np.array = np.vectorize(
            lambda agent: (1 + agent.id) % 255 if agent is not None else 0,
        )(self.space)
        return displayable_array

    def copy(self):
        new_universe = Universe(self.height, self.width)
        new_universe.genesis = self.genesis
        new_universe.freeze = self.freeze

    def __getitem__(self, pos: Position):
        if isinstance(pos, Position):
            item = self.space[pos.tuple]
        else:
            print(pos, type(pos))
            item = self.space[pos]
        return item

    def __contains__(self, value: object):
        return np.any(self.space == value)

    def __setitem__(self, pos: Position, value: object):
        if isinstance(pos, Position):
            self.space[pos.tuple] = value
        else:
            self.space[pos] = value

    def __eq__(self, other):
        return self.space == other

    def __repr__(self):
        return f"Space at {self.get_time()} ns\n{self.space}"


if __name__ == "__main__":
    a = Space(5, 10)
    print(a)
    a[Position(2, 4)] = 1
    print(a)
    print(a.is_valid(Position(1, 9)))
