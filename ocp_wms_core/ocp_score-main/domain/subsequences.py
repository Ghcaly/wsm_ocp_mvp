class SubsequenceGenerator:
    def __init__(self, limit=30000):
        self.limit = limit

    def subsequences(self, source):
        source = list(source)

        def make_subsequences(src, recursion):
            if src:
                for comb in make_subsequences(src[1:], recursion):
                    recursion += 1

                    if recursion > self.limit:
                        break

                    yield comb
                    yield [src[0], *comb]
            else:
                yield []

        return make_subsequences(source, 0)
