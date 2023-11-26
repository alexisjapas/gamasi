class Genome:
    """
    For the moment, this is just a dataclass-like used to store hereditary attributes
    It will be possible to create one genome from other genome(s) with mutations
    Hereditary attributes are locked into a structure to be passed on to the next generation
    But they are copied and can evolve during the life of the agent
    """
    def __init__(self):
        self.reaction_time: float = 10**-5