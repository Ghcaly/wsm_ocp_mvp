# class SpaceSizeChain:
#     def __init__(self, current, next_size=None):
#         self.Current = current
#         self.Next = next_size

# def space_size_chains():
#     yield SpaceSizeChain(42, 35)
#     yield SpaceSizeChain(35, 28)
#     yield SpaceSizeChain(28, 21)
#     yield SpaceSizeChain(21, 14)
#     yield SpaceSizeChain(14, None)

from ocp_score_ia.domain.space_size import SpaceSize


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
