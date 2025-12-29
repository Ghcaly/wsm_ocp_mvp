class SpaceSizeChain:
    def __init__(self, current, next_size=None):
        self.Current = current
        self.Next = next_size

def space_size_chains():
    yield SpaceSizeChain(42, 35)
    yield SpaceSizeChain(35, 28)
    yield SpaceSizeChain(28, 21)
    yield SpaceSizeChain(21, 14)
    yield SpaceSizeChain(14, None)
