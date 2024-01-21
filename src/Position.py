import numpy as np
from time import perf_counter_ns


class Position:
    def __init__(self, y: int, x: int, genesis: int=None):
        self.y = y
        self.x = x
        self.genesis = genesis
        self.t = None if genesis is None else perf_counter_ns() - genesis

    @property
    def tuple(self):
        return (self.y, self.x)

    def start_time(self, genesis):
        self.genesis = genesis
        self.t = perf_counter_ns() - genesis

    def is_in(self, map: np.array):
        return 0 <= self.y < np.array.shape[0] and 0 <= self.x < np.array.shape[1]

    def __add__(self, other):
        assert isinstance(other, Position)
        assert self.genesis == other.genesis
        return Position(y=self.y + other.y, x=self.x + other.x, genesis=self.genesis)

    def __eq__(self, other):
        is_equal = False
        if isinstance(other, Position):
            is_equal = self.y == other.y and self.x == other.x and self.t == other.t
        return is_equal

    def __repr__(self):
        return f"P(y={self.y}, x={self.x}, t={self.t})"


if __name__ == "__main__":
    a = Position(2, 4, 6)
    b = Position(3, 5)
    c = a + b
    print(c)
    e = a + b + c
    print(e.tuple)
    e.x = 0
    print(e.tuple)
