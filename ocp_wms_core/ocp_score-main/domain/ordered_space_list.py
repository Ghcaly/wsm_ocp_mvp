from typing import Callable, Iterable, Any, List

class OrderedSpaceList:
    def __init__(self, spaces: Iterable[Any], keys: List[tuple]):
        self._spaces = list(spaces)
        self._keys = list(keys)

    def ThenBy(self, key_selector: Callable[[Any], Any]):
        return OrderedSpaceList(self._spaces, self._keys + [(key_selector, False)])

    def ThenByDescending(self, key_selector: Callable[[Any], Any]):
        return OrderedSpaceList(self._spaces, self._keys + [(key_selector, True)])

    def ToList(self):
        result = list(self._spaces)
        for key_selector, desc in reversed(self._keys):
            result.sort(key=key_selector, reverse=desc)
        return list(self._spaces)

    # def FirstOrDefault(self, default=None):
    #     lst = self.ToList()
    #     try:
    #         return lst.FirstOrDefault()
    #     except Exception:
    #         return lst[0] if lst else default

    def _apply_order(self):
        result = self._spaces
        # aplica da ÚLTIMA chave para a PRIMEIRA
        for key_fn, is_desc in reversed(self._keys):
            result = sorted(result, key=key_fn, reverse=is_desc)
        return result

    def FirstOrDefault(self):
        ordered = self._apply_order()
        return ordered[0] if ordered else None
    
    # snake_case aliases
    then_by = ThenBy
    then_by_descending = ThenByDescending
    to_list = ToList
    first_or_default = FirstOrDefault