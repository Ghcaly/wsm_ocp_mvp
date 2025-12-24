from enum import IntEnum

class SpaceSize(IntEnum):
    """Tamanhos de pallet/caixa usados no projeto (compatível com referências C#)."""
    Size42 = 42
    Size35 = 35
    Size28 = 28
    Size21 = 21
    Size14 = 14

    @classmethod
    def default(cls):
        return cls.Size42