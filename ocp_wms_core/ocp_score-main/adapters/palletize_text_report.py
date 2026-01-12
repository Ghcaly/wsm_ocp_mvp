from pathlib import Path
from typing import Any


class PalletizeTextReport:
    """Generate a human-readable text report similar to the C# output used for
    manual inspection. This writer is intentionally simple and best-effort:
    it reads common context attributes and writes a formatted text file.
    """

    @staticmethod
    def save_text(context: Any, output_dir: Path) -> str:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        kind = getattr(context, 'context_kind', 'map') or 'map'
        file_name = f"{getattr(context, 'MapNumber', 'unknown')}-ocp-{kind}.txt"
        out_path = output_dir / file_name

        lines = []
        lines.append(f"Mapa: {getattr(context, 'MapNumber', '')} Veículo: {getattr(context, 'vehicle', '')}")

        try:
            total_products = getattr(context, 'total_products', None)
            if total_products is None:
                # Sum quantities of each product across mounted spaces (preferred)
                total_products = 0
                mspaces_for_sum = list(getattr(context, 'mounted_spaces', []) or [])
                for ms in mspaces_for_sum:
                    try:
                        products = ms.GetProducts() if hasattr(ms, 'GetProducts') else list(getattr(ms, 'Products', []) or [])
                        for p in products:
                            qty = getattr(p, 'Amount', getattr(p, 'amount', getattr(p, 'Quantity', getattr(p, 'quantity', 0)))) or 0
                            try:
                                total_products += int(qty)
                            except Exception:
                                try:
                                    total_products += int(float(qty))
                                except Exception:
                                    pass
                    except Exception:
                        continue

                # fallback: iterate context.pallets if mounted_spaces had no data
                if total_products == 0:
                    for pal in getattr(context, 'pallets', []) or []:
                        try:
                            products = getattr(pal, 'Products', []) or getattr(pal, 'products', []) or []
                            for p in products:
                                qty = getattr(p, 'Amount', getattr(p, 'amount', getattr(p, 'Quantity', getattr(p, 'quantity', 0)))) or 0
                                try:
                                    total_products += int(qty)
                                except Exception:
                                    try:
                                        total_products += int(float(qty))
                                    except Exception:
                                        pass
                        except Exception:
                            continue
        except Exception:
            total_products = 0

        lines.append(f"Produtos: {total_products}")
        # compute side weights using Context helper if available (preferred)
        motorista = 0.0
        ajudante = 0.0
        total_weight = 0.0
        summary = None
        try:
            summary = context.GetSideWeightSummary()
        except Exception:
            try:
                summary = context.get_side_weight_summary()
            except Exception:
                summary = None

        if isinstance(summary, dict):
            motorista = float(summary.get('motorista', {}).get('weight', 0.0) or 0.0)
            ajudante = float(summary.get('ajudante', {}).get('weight', 0.0) or 0.0)
            total_weight = float(summary.get('total', (motorista + ajudante)) or (motorista + ajudante))
        else:
            # fallback: compute from mounted_spaces
            mspaces_for_sum = list(getattr(context, 'mounted_spaces', []) or [])
            for ms in mspaces_for_sum:
                try:
                    sp = getattr(ms, 'Space', getattr(ms, 'space', None))
                    side = str(getattr(sp, 'Side', getattr(sp, 'side', '')) or '').upper()
                    weight = float(getattr(ms, 'Weight', getattr(ms, 'weight', 0.0)) or 0.0)
                except Exception:
                    continue
                if side.startswith('M'):
                    motorista += weight
                else:
                    ajudante += weight
            total_weight = (motorista + ajudante) or 0.0

        def fmt(n):
            try:
                return (f"{n:.2f}").replace('.', ',')
            except Exception:
                return '0,00'

        def pct(part, whole):
            try:
                v = (part / whole) * 100 if whole else 0.0
                return (f"{v:.2f}").replace('.', ',')
            except Exception:
                return '0,00'

        lines.append(f"Lado Motorista: {fmt(motorista)} ({pct(motorista, total_weight)}%)")
        lines.append(f"Lado Ajudante: {fmt(ajudante)} ({pct(ajudante, total_weight)}%)")
        lines.append("Cálculo Rota")
        lines.append("--------------------------------------------------------------------------------------------------------------------------------------------------")
        lines.append("Pallet        L      Código UN  Entrega Nome                                            Qtd Embalagem Grp/Sub       Peso Atributo        Ocupação   ")
        lines.append("-----------   - ----------- -- -------- ------------------------------------------ -------- --------- ------- ---------- ------------- ----------- ")
        lines.append("")

        mspaces = list(getattr(context, 'mounted_spaces', []) or [])

        def _pallet_sort_key(p):
            # Accept either a pallet dict or a MountedSpace-like object
            num = None
            code = ''
            if isinstance(p, dict):
                num = p.get('number')
                code = p.get('code') or ''
            else:
                # try to extract number from Space
                try:
                    sp = getattr(p, 'Space', getattr(p, 'space', None))
                    num = getattr(sp, 'Number', getattr(sp, 'number', None))
                except Exception:
                    num = None
                # try to extract first product code
                try:
                    products = p.GetProducts() if hasattr(p, 'GetProducts') else list(getattr(p, 'Products', []) or [])
                    first = products[0] if products else None
                    code = getattr(first, 'Code', getattr(first, 'code', '')) if first is not None else ''
                except Exception:
                    code = ''

            try:
                n = int(num) if num is not None else float('inf')
            except Exception:
                try:
                    n = int(str(num))
                except Exception:
                    n = float('inf')

            return (n, str(code))

        # If context has `pallets` (dicts), prefer ordering those; else order mounted_spaces
        pallets = getattr(context, 'pallets', None)
        if pallets:
            try:
                ordered = sorted(list(pallets or []), key=_pallet_sort_key)
                # try to convert ordered pallet dicts back to MountedSpace-like iteration by mapping
                # If pallet dicts contain 'mounted_space' reference, use it; otherwise we will iterate pallets directly below
                use_pallet_dicts = True
            except Exception:
                ordered = sorted(mspaces, key=_pallet_sort_key)
                use_pallet_dicts = False
        else:
            try:
                ordered = sorted(mspaces, key=_pallet_sort_key)
            except Exception:
                ordered = mspaces
            use_pallet_dicts = False


        for ms in mspaces:
            try:
                sp = getattr(ms, 'Space', getattr(ms, 'space', None))
                nr = getattr(sp, 'Number', getattr(sp, 'number', ''))
                lado = getattr(sp, 'Side', getattr(sp, 'side', ''))
                occ = getattr(ms, 'Occupation', getattr(ms, 'occupation', 0))
                total_weight = getattr(ms, 'Weight', getattr(ms, 'weight', 0.0)) or 0.0

                products = []
                # try common product getters
                if hasattr(ms, 'GetProducts'):
                    products = list(ms.GetProducts() or [])
                else:
                    products = list(getattr(ms, 'Products', []) or [])

                # aggregate by code
                agg = {}
                total_qty = 0
                for p in products:
                    code = p.Item.Code 
                    name = p.Item.Product.Name 
                    qty = getattr(p, 'Amount', getattr(p, 'amount', getattr(p, 'Quantity', getattr(p, 'quantity', 0)))) or 0
                    
                    # Determinar atributo baseado nas propriedades do produto
                    atributo = "Descartável"
                    try:
                        if hasattr(p.Item, 'IsReturnable') and callable(p.Item.IsReturnable) and p.Item.IsReturnable():
                            atributo = "Retornavel"
                        elif hasattr(p.Item, 'IsChopp') and callable(p.Item.IsChopp) and p.Item.IsChopp():
                            atributo = "Chopp"
                        elif hasattr(p.Item, 'IsIsotonicWater') and callable(p.Item.IsIsotonicWater) and p.Item.IsIsotonicWater():
                            atributo = "Isotonico"
                        elif hasattr(p.Item, 'IsTopOfPallet') and callable(p.Item.IsTopOfPallet) and p.Item.IsTopOfPallet():
                            atributo = "TopoPallet"
                        elif hasattr(p.Item.Product, 'IsMarketplace') and p.Item.Product.IsMarketplace:
                            atributo = "BinPack"
                    except Exception:
                        pass
                    
                    # Pegar embalagem e grupo/subgrupo do PackingGroup
                    embalagem = ""
                    grp_sub = ""
                    try:
                        if hasattr(p.Item.Product, 'PackingGroup') and p.Item.Product.PackingGroup:
                            packing = p.Item.Product.PackingGroup
                            embalagem = str(getattr(packing, 'PackingCode', ''))
                            grupo = str(getattr(packing, 'GroupCode', ''))
                            subgrupo = str(getattr(packing, 'SubGroupCode', ''))
                            if grupo and subgrupo:
                                grp_sub = f"{grupo}/{subgrupo}"
                    except Exception:
                        pass
                    
                    # Peso total do produto
                    weight = 0.0
                    try:
                        if hasattr(p.Item.Product, 'GrossWeight'):
                            weight = float(p.Item.Product.GrossWeight or 0) * int(qty)
                    except Exception:
                        pass
                    
                    ocupacao = getattr(p, 'Occupation', getattr(p, 'occupation', 0))

                    key = str(code)
                    if key not in agg:
                        agg[key] = {'code': key, 'name': str(name), 'qty': int(qty), 'embalagem': embalagem, 'grp_sub': grp_sub, 'weight': weight, 'atributo': atributo, 'ocupacao': ocupacao}
                    else:
                        agg[key]['qty'] += int(qty)
                        agg[key]['weight'] = (agg[key].get('weight', 0) or 0) + (weight or 0)

                    total_qty += int(qty)

                size = getattr(sp, 'Size', getattr(sp, 'size', ''))
                try:
                    occ_str = f"{float(occ):.2f}".replace('.', ',')
                except Exception:
                    occ_str = '0,00'
                try:
                    peso_total_str = f"{float(total_weight):.2f}".replace('.', ',')
                except Exception:
                    peso_total_str = '0,00'
                header = f"P_{('A' if str(lado).upper().startswith('L') else 'M')}_{str(nr).zfill(2)}_1/{size} - {occ_str} - {total_qty}  Peso: {peso_total_str}"
                lines.append(header)
                lines.append("            |============================ Produtos da área de separação: Geral ===================================================================|")

                prod_lines = []
                for v in sorted(agg.values(), key=lambda x: -x['qty']):
                    code = str(v['code']) if v['code'] is not None else ''
                    name = (v['name'][:42]).ljust(42)
                    qty = str(v['qty']).rjust(8)
                    emb = str(v['embalagem']).ljust(9)
                    grp = str(v['grp_sub']).ljust(7)
                    # peso total do produto na área (2 decimais, vírgula)
                    try:
                        peso_val = float(v.get('weight', 0) or 0)
                        peso = f"{peso_val:.2f}".replace('.', ',').rjust(10)
                    except Exception:
                        peso = f"{0:.2f}".replace('.', ',').rjust(10)
                    atr = str(v.get('atributo', '')).ljust(13)
                    # ocupação com 2 casas decimais e vírgula
                    try:
                        ocu_val = float(v.get('ocupacao', 0) or 0)
                        ocu = f"{ocu_val:.2f}".replace('.', ',').rjust(11)
                    except Exception:
                        ocu = f"{0:.2f}".replace('.', ',').rjust(11)
                    lines.append(f"            | 0       {code:13} {name} {qty} {emb} {grp} {peso} {atr} {ocu} | ")

                lines.append("            |                                                                                                                                     |")
                lines.append("            |=====================================================================================================================================|")
                lines.append("")
            except Exception:
                # best-effort: skip problematic mounted space
                continue

        # Produtos fora do caminhão (não paletizados)
        not_palletized = []
        palletized_codes = {}
        
        # Coletar todos os produtos paletizados
        for ms in mspaces_for_sum:
            try:
                products = ms.GetProducts() if hasattr(ms, 'GetProducts') else list(getattr(ms, 'Products', []) or [])
                for p in products:
                    code = str(getattr(p, 'Code', getattr(p, 'code', '')))
                    qty = getattr(p, 'Amount', getattr(p, 'amount', getattr(p, 'Quantity', getattr(p, 'quantity', 0)))) or 0
                    palletized_codes[code] = palletized_codes.get(code, 0) + int(qty)
            except Exception:
                continue
        
        # Coletar todos os itens do contexto
        all_items = []
        try:
            orders = getattr(context, 'Orders', getattr(context, 'orders', []))
            for order in (orders or []):
                items = getattr(order, 'Items', getattr(order, 'items', []))
                for item in (items or []):
                    all_items.append(item)
        except Exception:
            pass
        
        # Identificar produtos não paletizados
        total_np_weight = 0.0
        for item in all_items:
            try:
                code = str(getattr(item, 'Code', getattr(item, 'code', '')))
                qty_total = int(getattr(item, 'Quantity', getattr(item, 'quantity', 0)) or 0)
                qty_palletized = palletized_codes.get(code, 0)
                qty_not_palletized = qty_total - qty_palletized
                
                if qty_not_palletized > 0:
                    name = str(getattr(item, 'Name', getattr(item, 'name', getattr(item, 'Description', ''))) or '')
                    weight = float(getattr(item, 'Weight', getattr(item, 'weight', 0)) or 0)
                    total_item_weight = weight * qty_not_palletized
                    
                    # Determinar embalagem e grupo
                    packing = getattr(item, 'PackingGroup', getattr(item, 'packing_group', None))
                    embalagem = ''
                    grp_sub = ''
                    if packing:
                        try:
                            emb_code = getattr(packing, 'Code', getattr(packing, 'code', ''))
                            grp = getattr(packing, 'GroupCode', getattr(packing, 'group_code', getattr(packing, 'Group', '')))
                            sub = getattr(packing, 'SubGroupCode', getattr(packing, 'subgroup_code', getattr(packing, 'SubGroup', '')))
                            embalagem = str(emb_code)
                            grp_sub = f"{grp}/{sub}" if grp and sub else ''
                        except Exception:
                            pass
                    
                    # Determinar atributo
                    atributo = ''
                    try:
                        if getattr(item, 'IsReturnable', False) or getattr(item, 'is_returnable', False):
                            atributo = 'Retornavel'
                        elif getattr(item, 'IsIsotonicWater', False) or getattr(item, 'is_isotonic_water', False):
                            atributo = 'Isotonico'
                        elif getattr(item, 'Marketplace', False) or getattr(item, 'marketplace', False):
                            atributo = 'BinPack'
                        elif getattr(item, 'IsTopOfPallet', False) or getattr(item, 'is_top_of_pallet', False):
                            atributo = 'TopoPallet'
                        else:
                            atributo = 'Descartável'
                    except Exception:
                        atributo = 'Descartável'
                    
                    not_palletized.append({
                        'code': code,
                        'name': name,
                        'qty': qty_not_palletized,
                        'embalagem': embalagem,
                        'grp_sub': grp_sub,
                        'weight': total_item_weight,
                        'atributo': atributo
                    })
                    total_np_weight += total_item_weight
            except Exception:
                continue
        
        if not_palletized:
            lines.append(f"Produtos fora do caminhão - Peso: {total_np_weight:.2f}:")
            lines.append("-" * 125)
            for np in not_palletized:
                code = str(np['code']).ljust(14)
                name = np['name'][:60].ljust(60)
                qty = str(np['qty']).rjust(4)
                emb = str(np['embalagem']).ljust(11)
                grp = str(np['grp_sub']).ljust(11)
                peso_str = f"{np['weight']:.2f}".rjust(10)
                atr = np['atributo'].ljust(16)
                lines.append(f"            |          {code} {name} {qty} {emb} {grp} {peso_str} {atr}|")
            lines.append("-" * 125)

        with out_path.open('w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines))

        return str(out_path)
