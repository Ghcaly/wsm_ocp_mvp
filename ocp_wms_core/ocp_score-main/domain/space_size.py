from enum import IntEnum

class SpaceSize(IntEnum):
    """Tamanhos de pallet/caixa usados no projeto (compatível com referências C#)."""
    Size42 = 42
    Size48 = 48
    Size36 = 36

    @classmethod
    def default(cls):
        return cls.Size42