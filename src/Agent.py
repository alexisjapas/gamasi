from random import randint


class Agent:
    current_count = 0
    total_count = 0

    def __init__(self, generation: int):
        self.generation = generation

        self.id = Agent.total_count
        Agent.current_count += 1
        Agent.total_count += 1
        self.color = (randint(1, 255), randint(1, 255), randint(1, 255))

    def __del__(self):
        Agent.current_count -= 1


if __name__ == "__main__":
    agents = [Agent(0) for i in range(10)]
    a = Agent(0)
    b = Agent(0)
    c = Agent(1)
    print(Agent.current_count)
    del b
    print(Agent.current_count)
    agents.pop()
    print(Agent.current_count)
