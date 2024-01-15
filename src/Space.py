import threading
import numpy as np
from time import perf_counter_ns

from .Position import Position


class Space:
    """
    This class control and lock space (and time)
    """

    def __init__(self, height: int, width: int, lock: threading.Lock = None):
        self.height: int = height
        self.width: int = width
        self._genesis = None  # Lazily loaded
        self.lock = lock
        self.array: np.array = np.full(
            shape=(height, width), fill_value=None, dtype=object
        )

    def is_valid(self, pos: Position):
        return (
            0 <= pos.y < self.height
            and 0 <= pos.x < self.width
            and self.array[pos.tuple] is None
        )

    @property
    def genesis(self):
        if self._genesis is None:
            self._genesis = perf_counter_ns()
        return self._genesis

    @property
    def displayable(self):
        displayable_array: np.array = np.vectorize(
            lambda agent: agent.id % 255 if agent is not None else 0,
        )(self.array)
        return displayable_array

    def __getitem__(self, pos: Position):
        return self.array[pos.tuple]

    def __setitem__(self, pos: Position, value: object):
        self.array[pos.tuple] = value

    def __repr__(self):
        return f"{self.array}"


if __name__ == "__main__":
    a = Space(5, 10)
    print(a)
    a[Position(2, 4)] = 1
    print(a)
    print(a.is_valid(Position(1, 9)))
