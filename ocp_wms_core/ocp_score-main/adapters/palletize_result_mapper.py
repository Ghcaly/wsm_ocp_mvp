from typing import Any, Dict, List, Optional
import json
import datetime
import logging


class PalletizeResultMapper:
    """Map a runtime `Context` to the canonical PalletizeResultEvent (camelCase).

    The mapper reads `context.mounted_spaces` (or `context.MountedSpaces`) and
    extracts pallets, items and metadata to produce a dict that matches the
    output.json produced by the original C# adapter.
    """

    @staticmethod
    def _side_to_initial(side_raw: Optional[Any]) -> str:
        """
        Map input Side (may be int like 65/77 or string) to 'H' (Helper) or 'M' (Driver/Motorista).
        65 -> chr(65) == 'A' -> Helper -> 'H'
        77 -> chr(77) == 'M' -> Motorista/Driver -> 'M'
        """
        if side_raw is None:
            return "H"
        # decode bytes to string
        if isinstance(side_raw, (bytes, bytearray)):
            try:
                side_raw = side_raw.decode('utf-8')
            except Exception:
                side_raw = str(side_raw)

        ch = None
        # numeric code from input (int) -> convert to character
        if isinstance(side_raw, int):
            try:
                ch = chr(side_raw).upper()
            except Exception:
                ch = str(side_raw).upper()
        else:
            s = str(side_raw).strip()
            # handle numeric strings like '65' or '77'
            if s.isdigit():
                try:
                    ch = chr(int(s)).upper()
                except Exception:
                    ch = s.upper()
            else:
                ch = s.upper()

        if ch in ("M", "DRIVER", "D", "MOTORISTA", "MOTOR"):
            return "M"
        # treat 'A' (Ajudante) or any other as Helper
        return "H"

    @staticmethod
    def _map_side(side_raw: Optional[Any]) -> str:
        """Return textual side used elsewhere ('Driver' / 'Helper')."""
        init = PalletizeResultMapper._side_to_initial(side_raw)
        return "Driver" if init == "M" else "Helper"

    def _build_pallet_code(self, pallet, ordinal, total_bays, context=None):
        # ...existing code...
        # use _side_to_initial instead of ord()/ASCII
        raw_side = getattr(pallet, "Side", None)
        if raw_side is None and getattr(pallet, "Space", None) is not None:
            raw_side = getattr(pallet.Space, "Side", None)

        side_initial = self._side_to_initial(raw_side)  # returns 'M' or 'H'
        bay_number = int(getattr(pallet, "Number", 0) or 0)
        total = int(total_bays or getattr(context, "TotalBays", 0) or 0)
        return f"P{bay_number:02}_{side_initial}_{ordinal}/{total}"
    
    @staticmethod
    def _to_iso(o: Any):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        return o

    @classmethod
    def build_item(cls, mp: Any) -> Dict[str, Any]:
        # mp may be a MountedProduct-like or a dict 
        desc = getattr(mp, 'Description', None) or getattr(mp, 'description', None) or getattr(getattr(mp, 'Product', None), 'Name', None) or getattr(getattr(mp, 'product', None), 'name', None)
        code = getattr(getattr(mp, 'Product', None), 'Code', None) or getattr(getattr(mp, 'product', None), 'code', None) or getattr(mp, 'cdItem', None) or getattr(mp, 'code', None)
        qty = getattr(mp, 'Amount', None) or getattr(mp, 'amount', None) or getattr(mp, 'qtUnVenda', None) or 0
        try:
            qty = int(qty) if qty is not None else 0
        except Exception:
            qty = 0

        occ = getattr(mp, 'Occupation', None) or getattr(mp, 'occupation', None) or getattr(mp, 'PercentOccupationIntoDefaultPalletSize', None) or None
        asm = getattr(mp, 'AssemblySequence', None) or getattr(mp, 'assembly_sequence', None) or getattr(mp, 'sqMontagem', None)
        delivery = None
        try:
            delivery = getattr(getattr(mp, 'Order', None), 'DeliveryOrder', None) or getattr(getattr(mp, 'order', None), 'delivery_order', None)
        except Exception:
            delivery = None

        map_number = getattr(mp, 'MapNumber', None) or getattr(mp, 'map_number', None) or getattr(getattr(mp, 'Order', None), 'MapNumber', None)
        gross = mp.Product.GrossWeight 
        total_weight = getattr(mp, 'TotalWeight', None) or getattr(mp, 'total_weight', None) or None

        packing = getattr(mp.Product, 'PackingGroup', None) or getattr(mp.Product, 'packing', None) or {}
        packing_obj = {
            'Code': packing.get('PackingCode') if isinstance(packing, dict) else getattr(packing, 'PackingCode', None),
            'Group': packing.get('GroupCode') if isinstance(packing, dict) else getattr(packing, 'GroupCode', None),
            'SubGroup': packing.get('SubGroupCode') if isinstance(packing, dict) else getattr(packing, 'SubGroupCode', None),
        }

        order_obj = getattr(mp, 'Order', None) or getattr(mp, 'order', None)
        if order_obj is not None:
            items_list = getattr(order_obj, 'Items', None) or getattr(order_obj, 'items', None) or []
            # escolher o primeiro item da ordem (se houver)
            first_item = None
            if items_list:
                try:
                    first_item = items_list[0]
                except Exception: 
                    for it in items_list:
                        first_item = it
                        break
            if first_item is not None:
                customer = first_item.Customer
            else:
                customer = None
        

        return {
            'Description': desc,
            'Code': str(code) if code is not None else None,
            'Quantity': qty,
            'AclQtdUom': None,
            'DetachedQuantity': None,
            'RemainingQuantity': None,
            'Occupation': float(occ) if occ is not None else None,
            'AssemblySequence': asm,
            'DeliverySequence': delivery,
            'MapNumber': map_number,
            'GrossWeight': float(gross) if gross is not None else None,
            'TotalWeight': float(gross)*qty if gross is not None else None,
            'LayerCode': mp.Product.LayerCode ,
            'LayerQuantity': None,
            'IsTopOfPallet': mp.IsTopOfPallet(),
            'IsChopp': mp.IsChopp(),
            'IsReturnable': mp.IsReturnable(),
            'IsIsotonicWater': mp.IsIsotonicWater(),
            'Marketplace': mp.IsMarketplace(),
            'Packing': packing_obj,
            'Segregated': None,
            'Realocated': mp.Realocated,
            'AdditionalOccupation': float(mp.AdditionalOccupation) if mp.AdditionalOccupation is not None else None,
            'PrePickingTypeCorrelationId': None, 
            'ItemCorrelationId': getattr(mp, 'ItemCorrelationId', None) or getattr(mp, 'item_correlation_id', None) or getattr(mp, 'WmsId', None),
            'Customer': customer,
        }

    @classmethod
    def build_pallet(cls, ms: Any) -> Dict[str, Any]:
        # ms is mounted space or pallet-like object
        space = getattr(ms, 'Space', None) or getattr(ms, 'space', None)
        number = getattr(space, 'Number', None) or getattr(space, 'number', None) or getattr(ms, 'Number', None) or getattr(ms, 'number', None)
        side_raw = getattr(space, 'Side', None) or getattr(space, 'side', None) or getattr(ms, 'Side', None) or getattr(ms, 'side', None)
        side = cls._map_side(side_raw)
        size = getattr(space, 'Size', None) or getattr(space, 'size', None)
        occupation = getattr(ms, 'Occupation', None) or getattr(ms, 'occupation', None)
        weight = getattr(ms, 'Weight', None) or getattr(ms, 'weight', None)
        is_closed = getattr(ms, 'IsClosed', None) or getattr(ms, 'is_closed', None) or False
        is_palletized = True

        # build code if absent
        code = getattr(ms, 'Code', None) or getattr(ms, 'code', None)
        if not code:
            try:
                n = int(number) if number is not None else 0
            except Exception:
                n = 0
            # derive code initial from raw side value (accept numeric 65/77 or strings)
            try:
                raw_initial = cls._side_to_initial(side_raw)
            except Exception:
                raw_initial = 'H'
            # map internal initial to code initial: Helper -> 'A' (Ajudante), Driver -> 'M' (Motorista)
            code_initial = 'A' if raw_initial == 'H' else 'M'
            size_part = str(size) if size is not None else '0'
            code = f"P{n:02d}_{code_initial}_{n:02d}_1/{size_part}"

        # collect items from containers or Products
        items_src = []
        # Common container attribute names
        containers = getattr(ms, 'Containers', None) or getattr(ms, 'containers', None) or None
        if containers:
            for c in containers:
                prods = None
                # try several container product access patterns
                for cand in ('GetProducts', 'GetProducts', 'Products', 'products', 'GetProducts'):
                    try:
                        if hasattr(c, cand):
                            val = getattr(c, cand)
                            if callable(val):
                                prods = val()
                            else:
                                prods = val
                            break
                    except Exception:
                        prods = None
                if prods:
                    items_src.extend(list(prods))
        else:
            # fallback: mounted space may expose GetProducts / Products itself
            try:
                if hasattr(ms, 'GetProducts'):
                    items_src = list(ms.GetProducts() or [])
                else:
                    items_src = list(getattr(ms, 'Products', []) or [])
            except Exception:
                items_src = []

        items_out = [cls.build_item(mp) for mp in items_src]
        # Sort items by assemblySequence ascending (missing or non-numeric values go last)
        def _asm_key(it: Dict[str, Any]):
            v = it.get('AssemblySequence')
            if v is None:
                return float('inf')
            try:
                return int(v)
            except Exception:
                try:
                    return int(float(str(v)))
                except Exception:
                    return float('inf')
        # ordernacao por assemblySequence
        items_out = sorted(items_out, key=_asm_key)

        # roadShowOrder: collect delivery orders from items
        road_orders = []
        for it in items_out:
            ds = it.get('DeliverySequence')
            if ds is not None:
                ds_s = str(ds)
                if ds_s not in road_orders:
                    road_orders.append(ds_s)
        road_show = "|".join(road_orders) if road_orders else None

        # customer: try mounted_space.Order.Customer or ms.Customer
        # customer = getattr(ms, 'Customer', None) or getattr(getattr(ms, 'Order', None), 'Customer', None)

        # customer: preferir mounted_space.Order.Customer / ms.Customer ; se vazio, inferir do primeiro item
        customer = getattr(ms, 'Customer', None) or getattr(getattr(ms, 'Order', None), 'Customer', None)
        if not customer:
            # items_out já contém 'Customer' por item (build_item)
            for it in items_out:
                c = it.get('Customer') or it.get('customer')
                if c:
                    customer = c
                    break

        # license plates/document numbers extraction
        license_plates = getattr(ms, 'LicensePlates', None) or getattr(ms, 'license_plates', None) or []
        document_numbers = []
        for it in items_out:
            mn = it.get('MapNumber') or it.get('mapNumber')
            if mn is not None:
                if isinstance(mn, (list, tuple)):
                    document_numbers.extend([str(x) for x in mn if x])
                else:
                    document_numbers.append(str(mn))
        document_numbers = list(dict.fromkeys([d for d in document_numbers if d]))

        return {
            'Number': number,
            'Code': code,
            'RoadShowOrder': road_show,
            'Customer': customer,
            'Layer': getattr(ms, 'Layer', getattr(ms, 'layer', False)),
            'Side': side,
            'Size': float(size),
            'Occupation': float(occupation),
            'Weight': float(weight) if weight is not None else None,
            'IsClosed': is_closed,
            'IsPalletized': is_palletized,
            'Items': items_out,
            'LoadTypeOnPallet': getattr(ms, 'LoadTypeOnPallet', getattr(ms, 'load_type_on_pallet', None)) or 'Normal',
            'LicensePlates': license_plates,
            'DocumentNumbers': document_numbers,
        }

    @classmethod
    def build_event(cls, context: Any, palletize_dto: Optional[Any] = None, request: Optional[Any] = None, success: bool = True, message: Optional[str] = None) -> Dict[str, Any]:
        pallets_out: List[Dict[str, Any]] = []

        # accept both context.mounted_spaces (list) and context.MountedSpaces (MountedSpaceList)
        mspaces = None
        if hasattr(context, 'mounted_spaces'):
            mspaces = getattr(context, 'mounted_spaces') or []
        elif hasattr(context, 'MountedSpaces'):
            ms = getattr(context, 'MountedSpaces')
            try:
                mspaces = ms.to_list() if hasattr(ms, 'to_list') else list(ms)
            except Exception:
                try:
                    mspaces = list(ms)
                except Exception:
                    mspaces = []
        else:
            mspaces = []

        for ms in mspaces:
            try:
                pallets_out.append(cls.build_pallet(ms))
            except Exception as e:
                print(f"Erro ao mapear pallet no PalletizeResultMapper: {e}")
                continue
        # ensure empty pallets for spaces not represented by mounted spaces
        try:
            cls.build_pallets_empty(context, pallets_out)
        except Exception:
            pass
        # not-palletized sentinel
        not_palet = []
           
        np_items = context.GetItemsWithAmountRemaining()
        for p in np_items:
            code = p.Code
            qty = p.Amount
            desc = p.Product.Name
            
            # Extract packing info (same logic as build_item)
            packing = getattr(p.Product, 'PackingGroup', None) or getattr(p.Product, 'packing', None) or {}
            packing_obj = {
                'Code': packing.get('PackingCode') if isinstance(packing, dict) else getattr(packing, 'PackingCode', None),
                'Group': packing.get('GroupCode') if isinstance(packing, dict) else getattr(packing, 'GroupCode', None),
                'SubGroup': packing.get('SubGroupCode') if isinstance(packing, dict) else getattr(packing, 'SubGroupCode', None),
            }
            
            # Extract weight and occupation info
            gross = getattr(p.Product, 'GrossWeight', None)
            total_weight = float(gross) * qty if gross is not None else None
            
            # Get occupation (from item's default occupation if available)
            occ = getattr(p, 'Occupation', None) or getattr(p, 'occupation', None) or getattr(p, 'PercentOccupationIntoDefaultPalletSize', None) or None
            
            not_palet.append({
                'Quantity': qty, 
                'Code': str(code) if code is not None else None, 
                'Description': desc if desc is not None else None,
                'GrossWeight': float(gross) if gross is not None else None,
                'TotalWeight': total_weight,
                'Occupation': float(occ) if occ is not None else None,
                'Packing': packing_obj,
                'IsTopOfPallet': p.Product.PalletSetting.IncludeTopOfPallet,
                'IsChopp': p.Product.IsChopp(),
                'IsReturnable': p.Product.IsReturnable(),
                'IsIsotonicWater': p.Product.IsIsotonicWater(),
            })

        pallets_out.append({'Code': 'Z_ITEM_NAO_PALLETIZADO', 'IsClosed': False, 'IsPalletized': False, 'Items': not_palet})

        # ordenar pallets por number asc (1..N) e depois por code asc para saída previsível
        def _pallet_sort_key(p: dict):
            num = p.get('Number')
            try:
                n = int(num) if num is not None else float('inf')
            except Exception:
                try:
                    n = int(str(num))
                except Exception:
                    n = float('inf')
            code = p.get('Code') or ''
            return (n, str(code))

        try:
            pallets_out = sorted(pallets_out, key=_pallet_sort_key)
        except Exception:
            # fallback: keep original ordering on error
            pass

        result = {'success': bool(success), 'message': message, 'status': 'Success' if success else 'GenericError' }
      
        event = {
            'UnbCode': palletize_dto.unb_code ,
            'VehiclePlate': palletize_dto.vehicle_plate  ,
            'DocumentNumber': palletize_dto.document_number  ,
            'DocumentType': palletize_dto.document_type  ,
            'DeliveryDate': palletize_dto.delivery_date  ,
            'Pallets': pallets_out,
            'Request': palletize_dto.request  ,
            'Result': result,
            'UniqueKey': palletize_dto.unique_key ,
            'CatalogName': palletize_dto.catalog_name ,
        }

        # fill missing with placeholder for compatibility
        def _fill_missing(obj: Any):
            if isinstance(obj, dict):
                for k, v in list(obj.items()):
                    if v is None:
                        obj[k] = None
                    else:
                        _fill_missing(v)
            elif isinstance(obj, list):
                for i in range(len(obj)):
                    if obj[i] is None:
                        obj[i] = None
                    else:
                        _fill_missing(obj[i])

        # sanitize the event to avoid circular references and non-serializable objects
        def _sanitize(o: Any, _seen: set = None):
            if _seen is None:
                _seen = set()
            oid = id(o)
            if oid in _seen:
                return str(o)
            # mark compound objects
            if isinstance(o, (dict, list)):
                _seen.add(oid)

            if isinstance(o, dict):
                out = {}
                for k, v in o.items():
                    out[str(k)] = _sanitize(v, _seen)
                return out
            if isinstance(o, list):
                return [_sanitize(v, _seen) for v in o]
            if isinstance(o, (str, int, float, bool)) or o is None:
                return o
            if isinstance(o, (datetime.date, datetime.datetime)):
                return cls._to_iso(o)
            # fallback: try to extract simple attributes commonly used
            try:
                # if object has a 'to_dict' or 'to_json' method, use it
                if hasattr(o, 'to_dict') and callable(getattr(o, 'to_dict')):
                    return _sanitize(o.to_dict(), _seen)
                if hasattr(o, 'to_json') and callable(getattr(o, 'to_json')):
                    return _sanitize(o.to_json(), _seen)
            except Exception:
                pass
            # final fallback: string representation
            try:
                return str(o)
            except Exception:
                return None

        event = _sanitize(event)
        _fill_missing(event)
        return event

    @classmethod
    def build_pallets_empty(cls, context: Any, pallets_out: List[Dict[str, Any]]) -> None:
        """Ensure there is a pallet entry for every Space in the context.

        Appends empty pallet dicts to `pallets_out` for spaces that are
        not represented yet. This mirrors the C# behavior of including
        empty pallets (occupation 0, no items) in the final output.
        """
        def _normalize_key(num, side_raw):
            try:
                n = int(num) if num is not None else None
            except Exception:
                try:
                    n = int(str(num))
                except Exception:
                    n = None
            init = cls._side_to_initial(side_raw)
            return (n, init)

        existing_keys = set()
        for p in pallets_out:
            try:
                existing_keys.add(_normalize_key(p.get('Number') or p.get('number'), p.get('Side') or p.get('side')))
            except Exception:
                continue

        try:
            if hasattr(context, 'GetAllSpaces'):
                spaces = context.GetAllSpaces() or []
            elif hasattr(context, 'get_all_spaces'):
                spaces = context.get_all_spaces() or []
            else:
                spaces = getattr(context, 'spaces', []) or []
        except Exception:
            spaces = getattr(context, 'spaces', []) or []

        for sp in spaces or []:
            try:
                sp_num = getattr(sp, 'Number', None) or getattr(sp, 'number', None)
                sp_side_raw = getattr(sp, 'Side', None) or getattr(sp, 'side', None)
                sp_size = getattr(sp, 'Size', None) or getattr(sp, 'size', None)
                key = _normalize_key(sp_num, sp_side_raw)
                if key in existing_keys:
                    continue

                try:
                    n = int(sp_num) if sp_num is not None else 0
                except Exception:
                    try:
                        n = int(str(sp_num))
                    except Exception:
                        n = 0
                raw_initial = cls._side_to_initial(sp_side_raw)
                code_initial = 'A' if raw_initial == 'H' else 'M'
                size_part = str(sp_size) if sp_size is not None else '0'
                code = f"P{n:02d}_{code_initial}_{n:02d}_1/{size_part}"

                pallet_empty = {
                    'Number': sp_num,
                    'Code': code,
                    'RoadShowOrder': None,
                    'Customer': None,
                    'Layer': False,
                    'Side': cls._map_side(sp_side_raw),
                    'Size': sp_size,
                    'Occupation': 0,
                    'Weight': 0,
                    'IsClosed': False,
                    'IsPalletized': True,
                    'Items': [],
                    'LoadTypeOnPallet': getattr(sp, 'LoadTypeOnPallet', getattr(sp, 'load_type_on_pallet', None)) or 'Normal',
                    'LicensePlates': None,
                    'DocumentNumbers': [],
                }
                pallets_out.append(pallet_empty)
                existing_keys.add(key)
            except Exception:
                continue

        # end build_pallets_empty

    @classmethod
    def save(cls, context: Any, output_path: str, indent: int = 2) -> None:
        # Antes de construir o evento, contabiliza todos os itens que serão incluídos
        try:
            counts = cls._count_items_for_event(context)
            logger = logging.getLogger(__name__)
            logger.info("PalletizeResultMapper: items summary before build_event:")
            logger.info(f"  MountedSpaces: {counts.get('mounted_spaces', 0)}")
            logger.info(f"  Total items (sum quantities): {counts.get('total_quantity', 0)}")
            logger.info(f"  Distinct SKUs: {counts.get('distinct_codes', 0)}")
            top = counts.get('top_codes', [])
            if top:
                logger.info("  Top codes (qty): " + ", ".join([f"{c}:{q}" for c, q in top]))
        except Exception as e:
            # não falhar a serialização por causa do logger
            try:
                print(f"Erro ao contar itens antes do build_event: {e}")
            except Exception:
                pass

        # context.reattach_original_orders_to_mounted_products()
            

        event = cls.build_event(context, palletize_dto=context.palletize_dto, request=context.palletize_dto.request)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(event, f, ensure_ascii=False, indent=indent, default=cls._to_iso)

    @classmethod
    def _count_items_for_event(cls, context: Any) -> Dict[str, Any]:
        """Return a small summary of items that will be placed into the event JSON.

        It uses `build_pallet` for each mounted space so the count matches the
        items that `build_event`/`save` will serialize.
        """
        mounted_count = 0
        code_counts: Dict[str, int] = {}
        total_quantity = 0

        # accept both context.mounted_spaces and context.MountedSpaces
        mspaces = None
        if hasattr(context, 'mounted_spaces'):
            mspaces = getattr(context, 'mounted_spaces') or []
        elif hasattr(context, 'MountedSpaces'):
            ms = getattr(context, 'MountedSpaces')
            try:
                mspaces = ms.to_list() if hasattr(ms, 'to_list') else list(ms)
            except Exception:
                try:
                    mspaces = list(ms)
                except Exception:
                    mspaces = []
        else:
            mspaces = []

        for ms in mspaces:
            try:
                mounted_count += 1
                pal = cls.build_pallet(ms)
                items = pal.get('Items') or pal.get('items', []) or []
                for it in items:
                    code = it.get('Code') or it.get('code') if isinstance(it, dict) else None
                    qty = it.get('Quantity') or it.get('quantity') if isinstance(it, dict) else None
                    try:
                        qn = int(qty) if qty is not None else 0
                    except Exception:
                        try:
                            qn = int(float(qty))
                        except Exception:
                            qn = 0
                    total_quantity += qn
                    if code:
                        code_counts[code] = code_counts.get(code, 0) + qn
            except Exception:
                # ignore per-mounted-space errors, we only want a best-effort summary
                continue

        distinct_codes = len(code_counts)
        # top codes by quantity
        top_codes = sorted(code_counts.items(), key=lambda x: -x[1])[:10]

        return {
            'mounted_spaces': mounted_count,
            'total_quantity': total_quantity,
            'distinct_codes': distinct_codes,
            'top_codes': top_codes,
            'per_code': code_counts,
        }
