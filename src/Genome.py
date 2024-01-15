from .Brain import Brain


class Genome:
    """
    It will be possible to create one genome from other genome(s) with mutations
    Hereditary attributes are locked into a structure to be passed on to the next generation
    But they are copied and can evolve during the life of the agent
    """

    def __init__(self, possible_actions: list=None):
        self.reaction_time: float = 10**-5
        self.speed: float = 10
        self.energy: float = 10
        self.brain = Brain(possible_actions=possible_actions)

    def mutate(self):  # TODO
        return self