import numpy as np
from time import perf_counter_ns


class Position:
    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x

    @property
    def tuple(self):
        return (self.y, self.x)

    def is_in(self, map: np.array):
        return 0 <= self.y < np.array.shape[0] and 0 <= self.x < np.array.shape[1]

    def __add__(self, other):
        assert isinstance(other, Position)
        return Position(y=self.y + other.y, x=self.x + other.x)

    def __eq__(self, other):
        is_equal = False
        if isinstance(other, Position):
            is_equal = self.y == other.y and self.x == other.x
        return is_equal

    def __repr__(self):
        return f"P(y={self.y}, x={self.x})"


if __name__ == "__main__":
    a = Position(2, 4)
    b = Position(3, 5)
    c = a + b
    print(c)
    e = a + b + c
    print(e.tuple)
    e.x = 0
    print(e.tuple)
