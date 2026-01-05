from dataclasses import dataclass
from typing import Optional, Any
import unicodedata
import re

from .box_type import BoxType


def _normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", text)


_ALIASES = {
    "garrafeira": BoxType.BottleBox,
    "bottlebox": BoxType.BottleBox,
    "bottle": BoxType.BottleBox,
    "caixavazada": BoxType.LeakedBox,
    "caixavazada": BoxType.LeakedBox,
    "leakedbox": BoxType.LeakedBox,
    "leaked": BoxType.LeakedBox,
}


def parse_box_type(value: Optional[Any]) -> Optional[BoxType]:
    """
    Converte uma entrada (string, int, enum) para `BoxType`.
    Retorna None se não for possível mapear.
    """
    if value is None:
        return None

    if isinstance(value, BoxType):
        return value

    # número (int ou str com dígitos)
    try:
        if isinstance(value, int) or (isinstance(value, str) and value.strip().isdigit()):
            return BoxType(int(value))
    except Exception:
        pass

    if isinstance(value, str):
        n = _normalize(value)
        if not n:
            return None
        if n in _ALIASES:
            return _ALIASES[n]
        for member in BoxType:
            if _normalize(member.name) == n:
                return member
    return None


@dataclass
class ItemMarketplace:
    box_type: Optional[BoxType] = None
    units_per_box: Optional[int] = None
    item: Optional[Any] = None  # referência opcional a ItemPalletization

    @classmethod
    def from_command(cls, cmd: Optional[Any]) -> Optional["ItemMarketplace"]:
        if cmd is None:
            return None
        raw_box = getattr(cmd, "BoxType", None) or getattr(cmd, "box_type", None) or getattr(cmd, "boxType", None)
        raw_units = getattr(cmd, "UnitsPerBox", None) or getattr(cmd, "units_per_box", None) or getattr(cmd, "unitsPerBox", None)
        return cls.from_row_values(raw_box, raw_units)

    @classmethod
    def copy_from(cls, other: Optional["ItemMarketplace"]) -> Optional["ItemMarketplace"]:
        if other is None:
            return None
        return cls(box_type=other.box_type, units_per_box=other.units_per_box)

    def update_from(self, cmd: Optional[Any]) -> None:
        if cmd is None:
            return
        new = self.from_command(cmd)
        if new is None:
            return
        if new.box_type is not None:
            self.box_type = new.box_type
        if new.units_per_box is not None:
            self.units_per_box = new.units_per_box

    @classmethod
    def from_row_values(cls, raw_box_value: Optional[Any], raw_units_value: Optional[Any]) -> "ItemMarketplace":
        """
        Cria um ItemMarketplace recebendo apenas os valores crus extraídos do row:
          - raw_box_value: valor de row.get("Tipo Caixa", None)
          - raw_units_value: valor de row.get("Quantidade de unidades por caixa", None)
        Faz parsing robusto e retorna a instância pronta.
        """
        # parse box type
        box = parse_box_type(raw_box_value)

        # parse units per box - aceitar int, str com vírgula/ponto, float-like
        units = None
        if raw_units_value is not None:
            try:
                if isinstance(raw_units_value, int):
                    units = int(raw_units_value)
                else:
                    s = str(raw_units_value).strip()
                    if s == "":
                        units = None
                    else:
                        # normaliza vírgula decimal e remove espaços
                        s = s.replace(",", ".")
                        # tenta converter float e depois para int quando for inteiro
                        if "." in s:
                            f = float(s)
                            units = int(f) if f.is_integer() else int(f)
                        else:
                            units = int(s)
            except Exception:
                units = None

        return cls(box_type=box, units_per_box=units)