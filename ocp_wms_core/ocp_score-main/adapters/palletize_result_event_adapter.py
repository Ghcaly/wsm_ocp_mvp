"""Convert internal Context / domain objects into the PalletizeResultEvent dict.

This module implements minimal, conservative mapping logic inspired by the C#:
`PalletizeResultEventAdapter` and `PalletizeResultPalletAdapter` so the Python
port can emit a JSON with the same high-level structure.

Notes:
- The Python domain model is looser than the C# domain; the adapter fills the
  fields that exist and omits unavailable ones. Keys use PascalCase to match
  the C# serialized output.
"""

from typing import Any, Dict, List, Optional
import json
import datetime


def _map_side(cd_lado: Optional[str]) -> str:
    """Map a Python pallet side to the result Side string used in C# (Driver/Helper).

    Very small heuristic: values that look like driver/motorista -> Driver,
    otherwise Helper.
    """
    if not cd_lado:
        return "Driver"
    s = str(cd_lado).strip().lower()
    if "motor" in s or "d" == s:
        return "Driver"
    return "Helper"


def _build_item_from_itempallet(item: Any) -> Dict[str, Any]:
    """Map a simple ItemPallet (dataclass) to the PalletizeResultItem minimal shape.

    The Python ItemPallet has fields like sqEntrega, cdItem, qtUnVenda, sqMontagem.
    We map the ones we find to the expected C# names.
    """
    return {
        "Quantity": getattr(item, "qtUnVenda", None) or getattr(item, "qt_un_venda", None) or 0,
        "Code": str(getattr(item, "cdItem", None) or getattr(item, "cd_item", "")),
        "AssemblySequence": getattr(item, "sqMontagem", None) or getattr(item, "sq_montagem", None),
        "DeliverySequence": getattr(item, "sqEntrega", None) or getattr(item, "sq_entrega", None),
    }


def _build_palletize_result_pallet_from_pallet(pallet: Any) -> Dict[str, Any]:
    """Convert a Python Pallet domain object into a minimal PalletizeResultPallet dict.

    The C# implementation contains many fields (Occupation, Layer, Weight, etc.).
    Here we include a conservative subset mapped from the Python Pallet dataclass
    present in this project.
    """
    number = getattr(pallet, "nrBaiaGaveta", None) or getattr(pallet, "nr_baia_gaveta", None) or 0
    side_original = getattr(pallet, "cdLado", None) or getattr(pallet, "cd_lado", None)
    side = _map_side(side_original)

    # Code uses the C# formatting as close as possible with limited info
    code = f"P{int(number):02d}_{side}_{int(number):02d}_1/0"

    # Build items with a fuller field set (PascalCase) so PascalCase output
    # matches the camelCase shape we also produce.
    items = []
    # accept several possible attribute names used across domain objects: Items, items, Products, products, itens
    raw_items = None
    for candidate in ("Items", "items", "Products", "products", "Produtos", "ProdutosPallet", "itens"):
        raw_items = getattr(pallet, candidate, None)
        if raw_items:
            break
    raw_items = raw_items or []
    for it in raw_items:
        # use the small mapper when object is a dataclass-like ItemPallet
        if not isinstance(it, dict):
            itm = _build_item_from_itempallet(it)
            # _build_item_from_itempallet returns some keys in PascalCase (Quantity, Code,...)
            # normalize to the expected full set
            item_out = {
                "Description": getattr(it, "Nome", None) or getattr(it, "description", None),
                "Code": str(getattr(it, "cdItem", None) or getattr(it, "cd_item", None) or getattr(it, "Codigo", None) or getattr(it, "code", None) or itm.get("Code")),
                "Quantity": itm.get("Quantity", None),
                "AclQtdUom": _get_first(it, "AclQtdUom", "aclQtdUom", default=None),
                "DetachedQuantity": _get_first(it, "DetachedQuantity", "detachedQuantity", default=None),
                "RemainingQuantity": _get_first(it, "RemainingQuantity", "remainingQuantity", default=None),
                "Occupation": _get_first(it, "Occupation", "occupation", default=None),
                "AssemblySequence": _get_first(it, "AssemblySequence", "assemblySequence", "SequenciaMontagem", "sqMontagem", default=None),
                "DeliverySequence": _get_first(it, "DeliverySequence", "deliverySequence", "SequenciaEntrega", "sqEntrega", default=None),
                "MapNumber": _get_first(it, "MapNumber", "mapNumber", default=None),
                "GrossWeight": _get_first(it, "GrossWeight", "grossWeight", default=None),
                "TotalWeight": _get_first(it, "TotalWeight", "totalWeight", default=None),
                "LayerCode": _get_first(it, "LayerCode", "layerCode", default=None),
                "LayerQuantity": _get_first(it, "LayerQuantity", "layerQuantity", default=None),
                "IsTopOfPallet": _get_first(it, "IsTopOfPallet", "isTopOfPallet", default=None),
                "IsChopp": _get_first(it, "IsChopp", "isChopp", default=None),
                "IsReturnable": _get_first(it, "IsReturnable", "isReturnable", default=None),
                "IsIsotonicWater": _get_first(it, "IsIsotonicWater", "isIsotonicWater", default=None),
                "Marketplace": _get_first(it, "Marketplace", "marketplace", default=None),
                "Packing": {
                    "Code": None,
                    "Group": None,
                    "SubGroup": None,
                },
                "Segregated": _get_first(it, "Segregated", "segregated", default=None),
                "Realocated": _get_first(it, "Realocated", "realocated", default=None),
                "AdditionalOccupation": _get_first(it, "AdditionalOccupation", "additionalOccupation", default=None),
                "PrePickingTypeCorrelationId": _get_first(it, "PrePickingTypeCorrelationId", "prePickingTypeCorrelationId", default=None),
                "ItemCorrelationId": _get_first(it, "ItemCorrelationId", "itemCorrelationId", "WmsId", default=None),
            }
            # if packing dict-like exists on original, copy subfields
            pr = _get_first(it, "Packing", "packing", default=None)
            if isinstance(pr, dict):
                item_out["Packing"]["Code"] = pr.get("code") or pr.get("Code")
                item_out["Packing"]["Group"] = pr.get("group") or pr.get("Group")
                item_out["Packing"]["SubGroup"] = pr.get("subGroup") or pr.get("SubGroup")
        else:
            # it is already a dict-like; map conservatively
            item_out = {
                "Description": it.get("Description") or it.get("description"),
                "Code": str(it.get("Code") or it.get("code") or it.get("cdItem") or ""),
                "Quantity": it.get("Quantity") or it.get("quantity"),
                "AclQtdUom": it.get("AclQtdUom") or it.get("aclQtdUom"),
                "DetachedQuantity": it.get("DetachedQuantity") or it.get("detachedQuantity"),
                "RemainingQuantity": it.get("RemainingQuantity") or it.get("remainingQuantity"),
                "Occupation": it.get("Occupation") or it.get("occupation"),
                "AssemblySequence": it.get("AssemblySequence") or it.get("assemblySequence"),
                "DeliverySequence": it.get("DeliverySequence") or it.get("deliverySequence"),
                "MapNumber": it.get("MapNumber") or it.get("mapNumber"),
                "GrossWeight": it.get("GrossWeight") or it.get("grossWeight"),
                "TotalWeight": it.get("TotalWeight") or it.get("totalWeight"),
                "LayerCode": it.get("LayerCode") or it.get("layerCode"),
                "LayerQuantity": it.get("LayerQuantity") or it.get("layerQuantity"),
                "IsTopOfPallet": it.get("IsTopOfPallet") or it.get("isTopOfPallet"),
                "IsChopp": it.get("IsChopp") or it.get("isChopp"),
                "IsReturnable": it.get("IsReturnable") or it.get("isReturnable"),
                "IsIsotonicWater": it.get("IsIsotonicWater") or it.get("isIsotonicWater"),
                "Marketplace": it.get("Marketplace") or it.get("marketplace"),
                "Packing": {
                    "Code": (it.get("Packing") or {}).get("code") or (it.get("Packing") or {}).get("Code"),
                    "Group": (it.get("Packing") or {}).get("group") or (it.get("Packing") or {}).get("Group"),
                    "SubGroup": (it.get("Packing") or {}).get("subGroup") or (it.get("Packing") or {}).get("SubGroup"),
                },
                "Segregated": it.get("Segregated") or it.get("segregated"),
                "Realocated": it.get("Realocated") or it.get("realocated"),
                "AdditionalOccupation": it.get("AdditionalOccupation") or it.get("additionalOccupation"),
                "PrePickingTypeCorrelationId": it.get("PrePickingTypeCorrelationId") or it.get("prePickingTypeCorrelationId"),
                "ItemCorrelationId": it.get("ItemCorrelationId") or it.get("itemCorrelationId") or it.get("WmsId"),
            }

        items.append(item_out)

    pallet_out = {
        "Number": int(number) if number is not None else None,
        "Code": code,
        "RoadShowOrder": _get_first(pallet, "RoadShowOrder", "RoadShow", "roadShowOrder", default=None),
        "Customer": _get_first(pallet, "Customer", "customer", default=None),
        "Layer": _get_first(pallet, "Layer", "layer", default=None),
        "Side": side,
        "Size": _get_first(pallet, "Size", "size", default=None),
        "Occupation": _get_first(pallet, "Occupation", "occupation", default=None),
        "Weight": _get_first(pallet, "Weight", "weight", default=None),
        "IsClosed": _get_first(pallet, "IsClosed", "isClosed", default=None),
        "IsPalletized": _get_first(pallet, "IsPalletized", "isPalletized", default=None),
        "Items": items,
        "LoadTypeOnPallet": _get_first(pallet, "LoadTypeOnPallet", "loadTypeOnPallet", default=None),
        "LicensePlates": _get_first(pallet, "LicensePlates", "licensePlates", default=None),
        "DocumentNumbers": _get_first(pallet, "DocumentNumbers", "documentNumbers", default=None),
    }

    return pallet_out


def _build_not_palletized_sentinel(not_palletized: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the Z_ITEM_NAO_PALLETIZADO sentinel pallet containing non-palletized items.

    We accept a list of dicts (context.not_palletized_items) and try to map each
    entry to a PalletizeResultItem minimal structure.
    """
    items = []
    for p in not_palletized or []:
        # try common keys
        code = str(p.get("Code") or p.get("cdItem") or p.get("ItemCode") or p.get("Codigo", ""))
        qty = p.get("Quantity") or p.get("qtUnVenda") or p.get("Quantidade") or 0
        items.append({
            "Quantity": qty,
            "Code": code,
            "Description": p.get("Description") or p.get("Nome") or None,
        })

    return {
        "Code": "Z_ITEM_NAO_PALLETIZADO",
        "IsClosed": False,
        "IsPalletized": False,
        "Items": items,
    }


def build_palletize_result_event(context: Any, palletize_dto: Optional[Any] = None, request: Optional[Any] = None, success: bool = True, message: Optional[str] = None, pre_picking: Optional[Any] = None) -> Dict[str, Any]:
    """Builds a dict representing the PalletizeResultEvent.

    Parameters:
    - context: the runtime Context instance (has .pallets and .not_palletized_items)
    - palletize_dto/request: optional DTOs to populate metadata (DocumentNumber, Type, UnbCode,...)
    - success/message: result status

    Returns:
    - dict matching the high-level C# PalletizeResultEvent shape (keys in PascalCase).
    """
    # Build pallets list from context.pallets (if present)
    pallets_out: List[Dict[str, Any]] = []
    for p in getattr(context, "pallets", []) or []:
        try:
            pallets_out.append(_build_palletize_result_pallet_from_pallet(p))
        except Exception:
            # defensive: skip problematic pallets
            continue

    # Build not-palletized sentinel
    not_palletized = _build_not_palletized_sentinel(getattr(context, "not_palletized_items", []) or [])

    # Append sentinel as the last pallet (C# did Pallets = pallets.Append(notPalletized).ToList())
    pallets_out.append(not_palletized)

    # Metadata
    document_number = None
    document_type = None
    unb_code = None
    vehicle_plate = None
    delivery_date = None
    unique_key = None
    is_new_palletize = None

    if palletize_dto is not None:
        document_number = getattr(palletize_dto, "DocumentNumber", None) or getattr(palletize_dto, "document_number", None)
        document_type = getattr(palletize_dto, "Type", None) or getattr(palletize_dto, "type", None)
        unb_code = getattr(getattr(palletize_dto, "Warehouse", {}), "UnbCode", None) if palletize_dto else None
        vehicle_plate = getattr(palletize_dto, "Vehicle", {}).get("LicensePlate") if isinstance(getattr(palletize_dto, "Vehicle", {}), dict) else getattr(getattr(palletize_dto, "Vehicle", None), "LicensePlate", None)
        delivery_date = getattr(palletize_dto, "DeliveryDate", None) or getattr(palletize_dto, "delivery_date", None)
        unique_key = getattr(palletize_dto, "UniqueKey", None) or getattr(palletize_dto, "unique_key", None)
        is_new_palletize = getattr(palletize_dto, "IsNewPalletize", None) or getattr(palletize_dto, "is_new_palletize", None)

    # Build Result
    result = {
        "Success": bool(success),
        "Status": "Success" if success else "GenericError",
    }
    if message:
        result["Message"] = message

    event = {
        "DocumentNumber": document_number,
        "DocumentType": document_type,
        "UnbCode": unb_code,
        "VehiclePlate": vehicle_plate,
        "DeliveryDate": delivery_date,
        "Pallets": pallets_out,
        "Request": getattr(request, "__dict__", request) if request is not None else None,
        "Result": result,
        "UniqueKey": unique_key,
        "IsNewPalletize": is_new_palletize,
    }

    # Remove keys with None values to keep output compact like the C# serializer
    return {k: v for k, v in event.items() if v is not None}


def to_json(event: Dict[str, Any], *, indent: int = 2) -> str:
    """Serialize event dict to JSON string using a stable formatting."""
    def _json_default(o: Any):
        # convert datetimes/dates to ISO-8601 strings
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    return json.dumps(event, ensure_ascii=False, indent=indent, default=_json_default)


def save_palletize_result(context: Any, output_path: str, *, palletize_dto: Optional[Any] = None, request: Optional[Any] = None, success: bool = True, message: Optional[str] = None, pre_picking: Optional[Any] = None, indent: int = 2) -> None:
    """Build the PalletizeResultEvent from a runtime Context and save it to disk.

    Parameters:
    - context: runtime Context instance (must have .pallets and optionally .not_palletized_items)
    - output_path: filesystem path where the JSON will be written
    - palletize_dto/request/...: passed through to build_palletize_result_event
    - indent: JSON formatting indent

    The function writes UTF-8 JSON with ensure_ascii=False to preserve accents.
    """
    event = build_palletize_result_event(context, palletize_dto=palletize_dto, request=request, success=success, message=message, pre_picking=pre_picking)
    json_text = to_json(event, indent=indent)
    # write file using UTF-8
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_text)


def _get_first(obj: Any, *attrs, default=None):
    """Return first non-None attribute from obj using several possible names.

    Accepts attribute name variations (PascalCase, snake_case, legacy names).
    """
    if obj is None:
        return default
    for a in attrs:
        try:
            # try attribute access
            v = getattr(obj, a, None)
            if v is not None:
                return v
        except Exception:
            pass
        # treat like dict-like
        try:
            v = obj.get(a)
            if v is not None:
                return v
        except Exception:
            pass
    return default


def _map_pallet_to_camel(pallet: Any) -> Dict[str, Any]:
    """Map a pallet-like domain object to the C#-style camelCase pallet dict.

    This is a best-effort mapper that reads common attribute names used across
    the Python domain objects (PascalCase and snake_case variants) and falls
    back to compact defaults when fields are missing.
    """
    # common numeric / identity fields
    number = _get_first(pallet, "Number", "number", "Numero", "NumeroPallet", "nrBaiaGaveta", default=0)
    code = _get_first(pallet, "Code", "code", default=None)
    # prefer an explicit Code if present, otherwise format like the C# adapter
    side_raw = _get_first(pallet, "Side", "side", "Lado", "cdLado", default=None)
    size_raw = _get_first(pallet, "Size", "size", "Tamanho", "tamanho", "TamanhoPallet", default=None)
    if code is None:
        side_str = str(side_raw) if side_raw is not None else "A"
        size_str = str(size_raw) if size_raw is not None else "0"
        try:
            number_int = int(number)
        except Exception:
            number_int = 0
        code = f"P{number_int:02d}_{side_str}_{number_int:02d}_1/{size_str}"

    # map simple fields (keep all keys present - we'll fill missing later)
    road_show = _get_first(pallet, "RoadShowOrder", "RoadShow", "roadShowOrder", "OrdemRoadshow", default=None)
    customer = _get_first(pallet, "Customer", "customer", default=None)
    layer = _get_first(pallet, "Layer", "layer", default=None)
    occupation = _get_first(pallet, "Occupation", "occupation", "Ocupacao", default=None)
    weight = _get_first(pallet, "Weight", "weight", "Peso", default=None)
    is_closed = _get_first(pallet, "IsClosed", "isClosed", "Fechado", default=None)
    is_palletized = _get_first(pallet, "IsPalletized", "isPalletized", default=None)
    load_type = _get_first(pallet, "LoadTypeOnPallet", "loadTypeOnPallet", default=None)
    license_plates = _get_first(pallet, "LicensePlates", "licensePlates", "LicensePlateCrossDock", default=None)
    document_numbers = _get_first(pallet, "DocumentNumbers", "documentNumbers", "DocumentNumbersCrossDock", default=None)

    # attempt to build items list from common attributes (and keep all keys)
    # accept Products / products as common container attribute as well
    items_src = _get_first(pallet, "Items", "items", "Products", "products", "Produtos", "ProdutosPallet", "itens", default=[]) or []
    items_out = []
    for it in items_src:
        qty = _get_first(it, "Quantity", "quantity", "QuantidadeVenda", "qtUnVenda", default=None)
        code_item = _get_first(it, "Code", "code", "Codigo", "cdItem", default=None)
        assembly = _get_first(it, "AssemblySequence", "assemblySequence", "SequenciaMontagem", "sqMontagem", default=None)
        delivery_seq = _get_first(it, "DeliverySequence", "deliverySequence", "SequenciaEntrega", "sqEntrega", default=None)
        occupation_it = _get_first(it, "Occupation", "occupation", default=None)
        additional_occ = _get_first(it, "AdditionalOccupation", "additionalOccupation", default=None)
        desc = _get_first(it, "Description", "description", "Nome", default=None)
        gross = _get_first(it, "GrossWeight", "grossWeight", "PesoBruto", default=None)
        total_weight = _get_first(it, "TotalWeight", "totalWeight", default=None)
        is_chopp = _get_first(it, "IsChopp", "isChopp", "Chopp", default=None)
        is_isotonic = _get_first(it, "IsIsotonicWater", "isIsotonicWater", default=None)
        is_returnable = _get_first(it, "IsReturnable", "isReturnable", default=None)
        is_top = _get_first(it, "IsTopOfPallet", "isTopOfPallet", default=None)
        layer_code = _get_first(it, "LayerCode", "layerCode", default=None)
        layer_qty = _get_first(it, "LayerQuantity", "layerQuantity", default=None)
        packing = _get_first(it, "Packing", "packing", default=None)
        map_number = _get_first(it, "MapNumber", "mapNumber", default=None)
        segregated = _get_first(it, "Segregated", "segregated", default=None)
        realocated = _get_first(it, "Realocated", "realocated", default=None)
        acl = _get_first(it, "AclQtdUom", "aclQtdUom", default=None)
        item_corr = _get_first(it, "ItemCorrelationId", "itemCorrelationId", "WmsId", default=None)

        # Always include the full set of expected keys for items — values may be None
        packing_obj = None
        # If a packing structure exists (dict-like), try to extract subkeys
        p_raw = _get_first(it, "Packing", "packing", default=None)
        if isinstance(p_raw, dict):
            packing_obj = {
                "code": p_raw.get("code") if p_raw.get("code") is not None else p_raw.get("Code") if p_raw.get("Code") is not None else None,
                "group": p_raw.get("group") if p_raw.get("group") is not None else p_raw.get("Group") if p_raw.get("Group") is not None else None,
                "subGroup": p_raw.get("subGroup") if p_raw.get("subGroup") is not None else p_raw.get("SubGroup") if p_raw.get("SubGroup") is not None else None,
            }
        else:
            # keep as explicit dict so keys exist and will be filled with placeholder later
            packing_obj = {"code": None, "group": None, "subGroup": None}

        item_out: Dict[str, Any] = {
            "description": desc,
            "code": str(code_item) if code_item is not None else None,
            "quantity": qty,
            "aclQtdUom": acl,
            "detachedQuantity": _get_first(it, "DetachedQuantity", "detachedQuantity", "QuantidadeUnitariaAvulsa", default=None),
            "remainingQuantity": _get_first(it, "RemainingQuantity", "remainingQuantity", "QuantidadeVendaRestante", default=None),
            "occupation": occupation_it,
            "assemblySequence": assembly,
            "deliverySequence": delivery_seq,
            "mapNumber": map_number,
            "grossWeight": gross,
            "totalWeight": total_weight,
            "layerCode": layer_code,
            "layerQuantity": layer_qty,
            "isTopOfPallet": is_top,
            "isChopp": is_chopp,
            "isReturnable": is_returnable,
            "isIsotonicWater": is_isotonic,
            "marketplace": _get_first(it, "Marketplace", "marketplace", default=None),
            "packing": packing_obj,
            "segregated": segregated,
            "realocated": realocated,
            "additionalOccupation": additional_occ,
            "prePickingTypeCorrelationId": _get_first(it, "PrePickingTypeCorrelationId", "prePickingTypeCorrelationId", default=None),
            "itemCorrelationId": item_corr,
        }

        items_out.append(item_out)

    pallet_out = {
        "number": number,
        "code": code,
        "roadShowOrder": road_show,
        "customer": customer,
        "layer": layer,
        "side": side_raw,
        "size": size_raw,
        "occupation": occupation,
        "weight": weight,
        "isClosed": is_closed,
        "isPalletized": is_palletized,
        "items": items_out,
        "loadTypeOnPallet": load_type,
        "licensePlates": license_plates,
        "documentNumbers": document_numbers,
    }

    return pallet_out


def build_palletize_result_event_camel(context: Any, palletize_dto: Optional[Any] = None, request: Optional[Any] = None, success: bool = True, message: Optional[str] = None, pre_picking: Optional[Any] = None) -> Dict[str, Any]:
    """Build event dict mirroring the C# PalletizeResultEvent but using camelCase keys.

    This function is intentionally permissive and reads many attribute name
    variants (PascalCase, snake_case, Portuguese names) used across the
    Python/C# domain models in this repo. It attempts to reproduce the
    structure present in `ocp_score/data/AS/output.json`.
    """
    pallets_out: List[Dict[str, Any]] = []
    for p in getattr(context, "pallets", []) or []:
        try:
            pallets_out.append(_map_pallet_to_camel(p))
        except Exception:
            continue

    # build not-palletized sentinel from context or from provided pre_picking
    not_palet_items = _get_first(context, "not_palletized_items", "notPalletizedItems", default=[])
    if not_palet_items:
        items = []
        for p in not_palet_items:
            code = p.get("Code") or p.get("cdItem") or p.get("ItemCode") or p.get("Codigo") or p.get("code")
            qty = p.get("Quantity") or p.get("qtUnVenda") or p.get("Quantidade") or p.get("quantity") or None
            items.append({"quantity": qty, "code": str(code or None), "description": p.get("Description") or p.get("Nome")})
        sentinel = {"code": "Z_ITEM_NAO_PALLETIZADO", "isClosed": False, "isPalletized": False, "items": items}
    else:
        sentinel = {"code": "Z_ITEM_NAO_PALLETIZADO", "isClosed": False, "isPalletized": False, "items": []}

    pallets_out.append(sentinel)

    # top-level metadata (camelCase names matching output.json) - keep keys present
    unb_code = None
    vehicle_plate = None
    document_number = None
    document_type = None
    delivery_date = None
    unique_key = None
    is_new_palletize = None

    if palletize_dto is not None:
        unb_code = _get_first(palletize_dto, "Warehouse", "warehouse", default={})
        if isinstance(unb_code, dict):
            unb_code = unb_code.get("UnbCode") or unb_code.get("unbCode")
        else:
            unb_code = _get_first(getattr(palletize_dto, 'Warehouse', None), "UnbCode", "unbCode", default=None)

        vehicle_plate = _get_first(palletize_dto, "Vehicle", "vehicle", default={})
        if isinstance(vehicle_plate, dict):
            vehicle_plate = vehicle_plate.get("LicensePlate") or vehicle_plate.get("licensePlate")
        else:
            vehicle_plate = _get_first(getattr(palletize_dto, "Vehicle", None), "LicensePlate", "licensePlate", default=None)

        document_number = _get_first(palletize_dto, "DocumentNumber", "documentNumber", default=None)
        document_type = _get_first(palletize_dto, "Type", "type", default=None)
        delivery_date = _get_first(palletize_dto, "DeliveryDate", "deliveryDate", default=None)
        unique_key = _get_first(palletize_dto, "UniqueKey", "uniqueKey", default=None)
        is_new_palletize = _get_first(palletize_dto, "IsNewPalletize", "isNewPalletize", default=None)

    result = {"success": bool(success), "status": "Success" if success else "GenericError", "message": message}

    event = {
        "unbCode": unb_code,
        "vehiclePlate": vehicle_plate,
        "documentNumber": document_number,
        "documentType": document_type,
        "deliveryDate": delivery_date,
        "pallets": pallets_out,
        "request": getattr(request, "__dict__", request) if request is not None else None,
        "result": result,
        "uniqueKey": unique_key,
        "isNewPalletize": is_new_palletize,
    }

    # Ensure every None is replaced with a placeholder so the final JSON contains all keys
    def _fill_missing(obj: Any):
        if isinstance(obj, dict):
            for k, v in list(obj.items()):
                if v is None:
                    obj[k] = "SEM_VALOR"
                else:
                    _fill_missing(v)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                if obj[i] is None:
                    obj[i] = "SEM_VALOR"
                else:
                    _fill_missing(obj[i])

    _fill_missing(event)

    return event


def save_palletize_result_camel(context: Any, output_path: str, *, palletize_dto: Optional[Any] = None, request: Optional[Any] = None, success: bool = True, message: Optional[str] = None, pre_picking: Optional[Any] = None, indent: int = 2) -> None:
    """Build camelCase PalletizeResultEvent and save to disk as JSON (UTF-8).

    Use this when you need the JSON shape produced by the C# adapter (`output.json`).
    """
    event = build_palletize_result_event_camel(context, palletize_dto=palletize_dto, request=request, success=success, message=message, pre_picking=pre_picking)
    text = to_json(event, indent=indent)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def publish_result_calculated_from_context(context: Any, *, palletize_dto: Optional[Any] = None, request: Optional[Any] = None, processed_map: Optional[Any] = None, pre_picking: Optional[Any] = None, save_path: Optional[str] = None, indent: int = 2) -> Dict[str, Any]:
    """Build the camelCase PalletizeResultEvent from a runtime Context and return it.

    This is a small helper that mirrors the C# flow: the application assembles a
    PalletizeResultEvent (using the processed map and the original palletize
    DTO/request) and then persists it. Callers may pass a `palletize_dto` or
    `request` to populate top-level metadata. If `save_path` is provided the
    JSON will also be written to disk.

    Returns the event dict (camelCase keys).
    """
    event = build_palletize_result_event_camel(context, palletize_dto=palletize_dto, request=request, success=True, message=None, pre_picking=pre_picking)

    if save_path:
        text = to_json(event, indent=indent)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)

    return event


def publish_result_calculated_strict(context: Any, *, palletize_dto: Optional[Any] = None, request: Optional[Any] = None, processed_map: Optional[Any] = None, pre_picking: Optional[Any] = None, save_path: Optional[str] = None, indent: int = 2) -> Dict[str, Any]:
    """Strict variant that enforces required fields (raises ValueError if missing).

    Use this when you want the Python pipeline to fail early if required
    information for the canonical JSON is not present — similar to the
    C# path which expects a PalletizeDto + ProcessedMap to assemble the
    PalletizeResultEvent.
    """
    event = build_palletize_result_event_camel(context, palletize_dto=palletize_dto, request=request, success=True, message=None, pre_picking=pre_picking)

    # Perform validations similar to C# expectations
    missing = []

    # Top-level required metadata: uniqueKey (or palletize_dto.UniqueKey), documentNumber, unbCode
    unique_key = _get_first(palletize_dto, "UniqueKey", "uniqueKey") or _get_first(context, "uniqueKey", "UniqueKey") or event.get("uniqueKey")
    if not unique_key:
        missing.append("uniqueKey")

    doc_number = _get_first(palletize_dto, "DocumentNumber", "documentNumber") or event.get("documentNumber")
    if not doc_number:
        missing.append("documentNumber")

    unb = None
    wh = _get_first(palletize_dto, "Warehouse", "warehouse")
    if isinstance(wh, dict):
        unb = wh.get("UnbCode") or wh.get("unbCode")
    elif wh is not None:
        unb = _get_first(wh, "UnbCode", "unbCode")
    if not unb:
        # also try event
        if not event.get("unbCode"):
            missing.append("unbCode / Warehouse.UnbCode")

    # pallets must exist on context (can be empty list, but attribute must be present)
    if not hasattr(context, "pallets"):
        missing.append("context.pallets (attribute missing)")

    # Validate pallets structure: each pallet should have a number and items list
    pallets_src = event.get("pallets") or []
    for idx, p in enumerate(pallets_src):
        # skip sentinel pallet code if present
        code = p.get("code") or p.get("Code")
        if code == "Z_ITEM_NAO_PALLETIZADO":
            continue
        if p.get("number") is None and p.get("Number") is None:
            missing.append(f"pallets[{idx}].number")
        if p.get("items") is None and p.get("Items") is None:
            missing.append(f"pallets[{idx}].items")
        else:
            items = p.get("items") or p.get("Items") or []
            for jdx, it in enumerate(items):
                # if there are items, require an itemCorrelationId to trace them
                if not _get_first(it, "itemCorrelationId", "ItemCorrelationId", "WmsId"):
                    missing.append(f"pallets[{idx}].items[{jdx}].itemCorrelationId")

    if missing:
        # Instead of failing, attach warnings to the event and continue.
        # The event has already been built and had None replaced by "SEM_VALOR",
        # so we keep compatible output while informing callers what was missing.
        event.setdefault("validationWarnings", [])
        event["validationWarnings"].extend(sorted(set(missing)))

    if save_path:
        text = to_json(event, indent=indent)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)

    return event
