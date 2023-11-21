from random import randint


class Agent:
    current_count = 0
    total_count = 0

    def __init__(self, initial_position: (int, int), generation: int):
        self.position = initial_position
        self.generation = generation

        self.age = 0

        # id
        self.id = Agent.total_count
        Agent.current_count += 1
        Agent.total_count += 1

    def __repr__(self):
        ID = f"ID: {self.id:05d}"
        GEN = f"GEN: {self.generation:05d}"
        AGE = f"AGE: {self.age:05}"
        POS = f"POS: {self.position}"
        return f"{ID} | {GEN} | {AGE} | {POS}\n"

    def __del__(self):
        Agent.current_count -= 1


if __name__ == "__main__":
    agents = [Agent(0) for i in range(10)]
    a = Agent((0, 0), 0)
    b = Agent((0, 1), 0)
    c = Agent(1)
    print(Agent.current_count)
    del b
    print(Agent.current_count)
    agents.pop()
    print(Agent.current_count)
