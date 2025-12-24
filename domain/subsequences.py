# class SubsequenceGenerator:
#     def __init__(self, limit=30000):
#         self.limit = limit  # limite de recursão opcional
#         self.recursion_count = 0

#     def subsequences(self, source):
#         """
#         Gera todas as subsequências de 'source' até o limite definido.
#         """
#         source = list(source)

#         def make_subsequences(src):
#             if src:
#                 for comb in make_subsequences(src[1:]):
#                     self.recursion_count += 1
#                     if self.recursion_count > self.limit:
#                         break
#                     yield comb
#                     yield [src[0], *comb]
#             else:
#                 yield []

#         return make_subsequences(source)
# class SubsequenceGenerator:
#     def __init__(self, limit=30000):
#         self.limit = limit

#     def subsequences(self, source):
#         source = list(source)
#         counter = {'value': 0}

#         def make_subsequences(src):
#             if src:
#                 for comb in make_subsequences(src[1:]):
#                     counter['value'] += 1

#                     if counter['value'] > self.limit:
#                         break  # 🔑 break, NÃO return

#                     yield comb
#                     yield [src[0], *comb]
#             else:
#                 yield []

#         return make_subsequences(source)

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


