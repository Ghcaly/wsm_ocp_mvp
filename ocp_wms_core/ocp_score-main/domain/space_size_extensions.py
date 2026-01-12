from .space_size import SpaceSize


class SpaceSizeChain:
    def __init__(self, current: SpaceSize, next_size: SpaceSize | None = None):
        self._current = current
        self._next = next_size

    @property
    def Current(self):
        return self._current

    @property
    def Next(self):
        return self._next


def space_size_chains():
    yield SpaceSizeChain(SpaceSize.Size42, SpaceSize.Size35)
    yield SpaceSizeChain(SpaceSize.Size35, SpaceSize.Size28)
    yield SpaceSizeChain(SpaceSize.Size28, SpaceSize.Size21)
    yield SpaceSizeChain(SpaceSize.Size21, SpaceSize.Size14)
    yield SpaceSizeChain(SpaceSize.Size14)
