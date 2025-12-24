import json
from pathlib import Path
from collections import defaultdict, OrderedDict
import argparse


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def summarize_by_pallet(data: dict):
    """Return OrderedDict sorted by pallet code -> dict of product_code -> info (description, total_qty, gross_weight)

    This aggregates items by product code within each pallet.
    """
    pallets = data.get("Pallets") or data.get("pallets", []) or []
    result = {}
    for p in pallets:
        code = p.get("Code") or p.get("code") or "UNKN"
        items = p.get("Items") or p.get("items", []) or []
        prod_map = result.setdefault(code, {})
        for it in items:
            prod_code = str(it.get("Code") or it.get("code") or "")
            desc = (it.get("Description") or it.get("description") or "").strip()
            qty = int(it.get("Quantity") or it.get("quantity") or 0)
            gross = None
            try:
                gw = it.get("GrossWeight") or it.get("grossWeight")
                gross = float(gw) if gw is not None else None
            except Exception:
                gross = None
            if prod_code in prod_map:
                prod_map[prod_code]["quantity"] += qty
                if gross is not None:
                    prod_map[prod_code]["total_weight"] = prod_map[prod_code].get("total_weight", 0.0) + gross * qty
            else:
                prod_map[prod_code] = {"description": desc, "quantity": qty, "total_weight": (gross * qty) if gross is not None else None}
    # sort pallets by code
    ordered = OrderedDict(sorted(result.items(), key=lambda kv: kv[0]))
    return ordered


def write_txt(summary: OrderedDict, out_path: Path):
    # NOTE: `summary` contains only aggregated pallet -> products. To build a full report similar to
    # the project's `output.txt` we need some top-level fields. We expect the JSON to live adjacent
    # to this TXT and contain those fields; the caller should pass the full JSON when invoking this
    # helper. Here we only write the product tables that were aggregated by `summarize_by_pallet`.
    lines = []
    for pallet_code, products in summary.items():
        lines.append(f"{pallet_code}")
        lines.append("{:<13}  {:<60}  {:>10}".format("Code", "Description", "Quantity"))
        lines.append("-" * 88)
        for prod_code, info in sorted(products.items(), key=lambda kv: kv[0]):
            desc = info.get("description", "")
            qty = info.get("quantity", 0)
            weight = info.get("total_weight")
            weight_s = f"{weight:.2f}" if weight is not None else ""
            lines.append("{:<13}  {:<60}  {:>10}  {:>10}".format(prod_code, desc[:60], str(qty), weight_s))
        lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_full_report(data: dict, out_path: Path):
    """Write a detailed report similar to project's `output.txt` using the full JSON data."""
    lines = []
    doc = data.get('DocumentNumber') or data.get('documentNumber') or data.get('document_number') or ''
    vehicle = data.get('VehiclePlate') or data.get('vehiclePlate') or data.get('vehicle_plate') or ''
    lines.append(f"Mapa: {doc} Veículo: {vehicle}")

    # total products = sum of quantities across all pallets and non-palletized
    total_products = 0
    pallets = data.get('Pallets') or data.get('pallets', []) or []
    for p in pallets:
        for it in p.get('Items') or p.get('items', []) or []:
            try:
                total_products += int(it.get('Quantity') or it.get('quantity') or 0)
            except Exception:
                pass
    # include not palletized items if any (no quantity available there, treat as 1 each)
    notp = next((p for p in pallets if (p.get('Code') or p.get('code')) == 'Z_ITEM_NAO_PALLETIZADO'), None)
    if notp:
        for it in notp.get('Items') or notp.get('items', []) or []:
            q = it.get('Quantity') or it.get('quantity') or 1
            try:
                total_products += int(q)
            except Exception:
                total_products += 1

    lines.append(f"Produtos: {total_products}")

    # side weights
    side_weights = {'Driver': 0.0, 'Helper': 0.0}
    total_weight = 0.0
    for p in pallets:
        w = p.get('Weight') or p.get('weight')
        try:
            wv = float(w) if w is not None else 0.0
        except Exception:
            wv = 0.0
        side = p.get('Side') or p.get('side')
        if side in side_weights:
            side_weights[side] += wv
        total_weight += wv

    def fmt_w(x):
        return f"{x:.2f}" if x is not None else "0.00"

    # Labels in Portuguese
    motorista = fmt_w(side_weights.get('Driver', 0.0))
    ajudante = fmt_w(side_weights.get('Helper', 0.0))
    perc_m = f"{(side_weights.get('Driver',0.0)/total_weight*100):.2f}%" if total_weight > 0 else "0.00%"
    perc_a = f"{(side_weights.get('Helper',0.0)/total_weight*100):.2f}%" if total_weight > 0 else "0.00%"

    lines.append(f"Lado Motorista: {motorista} ({perc_m})")
    lines.append(f"Lado Ajudante: {ajudante} ({perc_a})")
    lines.append("Cálculo Rota")
    lines.append("-" * 140)

    # Column header (approximate)
    lines.append("Pallet        L      Código UN  Entrega Nome                                            Qtd Embalagem Grp/Sub       Peso Atributo        Ocupação   ")
    lines.append("-----------   - ----------- -- -------- ------------------------------------------ -------- --------- ------- ---------- ------------- ----------- ")
    lines.append("")

    # Build per-pallet blocks
    # for p in sorted((p for p in pallets if p.get('code') != 'Z_ITEM_NAO_PALLETIZADO'), key=lambda x: x.get('code') or ''):
    for p in [p for p in pallets if (p.get('Code') or p.get('code')) != 'Z_ITEM_NAO_PALLETIZADO']:
        code = p.get('Code') or p.get('code') or ''
        occ = p.get('Occupation') or p.get('occupation')
        try:
            occ_f = float(occ)
            occ_s = f"{occ_f:.2f}"
        except Exception:
            occ_s = str(occ or '')
        road = p.get('RoadShowOrder') or p.get('roadShowOrder') or ''
        weight = p.get('Weight') or p.get('weight')
        try:
            weight_f = float(weight) if weight is not None else 0.0
        except Exception:
            weight_f = 0.0
        # pick a representative code from first item if available
        first_code = ''
        items = p.get('Items') or p.get('items', []) or []
        if items:
            first_code = str(items[0].get('Code') or items[0].get('code') or '')

        customer = p.get('Customer') or p.get('customer') or ''

        header = f"{code} - {occ_s} - {road} - {customer}  Peso: {weight_f:.2f}"
        lines.append(header)
        lines.append("            |============================ Produtos da área de separação: Geral ===================================================================|")

        # aggregate products by code within this pallet
        agg = {}
        for it in items:
            c = str(it.get('Code') or it.get('code') or '')
            name = (it.get('Description') or it.get('description') or '').strip()
            q = int(it.get('Quantity') or it.get('quantity') or 0)
            gw = it.get('GrossWeight') or it.get('grossWeight')
            try:
                gwf = float(gw) if gw is not None else None
            except Exception:
                gwf = None
            emb = ''
            grp_sub = ''
            try:
                packing = it.get('Packing') or it.get('packing') or {}
                # prefer explicit packing codes if present
                emb = str(packing.get('Code') or packing.get('code') or packing.get('PalletQuantity') or packing.get('palletQuantity') or '')
                grp = packing.get('Group') or packing.get('group') or packing.get('grp') or packing.get('packing_group')
                sub = packing.get('SubGroup') or packing.get('subGroup') or packing.get('sub_group')
                if grp or sub:
                    grp_sub = f"{grp or ''}/{sub or ''}".strip('/')
            except Exception:
                emb = ''
                grp_sub = ''

            atributo = ''
            # Check both camelCase (old) and PascalCase (new) for compatibility
            is_marketplace = it.get('Marketplace') or it.get('marketplace')
            is_top = it.get('IsTopOfPallet') or it.get('isTopOfPallet')
            is_returnable = it.get('IsReturnable') or it.get('isReturnable')
            is_isotonic = it.get('IsIsotonicWater') or it.get('isIsotonicWater')
            is_chopp = it.get('IsChopp') or it.get('isChopp')
            
            # Prioridade: BinPack > TopoPallet > outros atributos
            if is_marketplace:
                atributo = 'BinPack'
            elif is_top:
                atributo = 'TopoPallet'
            elif is_returnable:
                atributo = 'Retornavel'
            elif is_isotonic:
                atributo = 'Isotonico'
            elif is_chopp:
                atributo = 'Chopp'
            else:
                # fallback: Descartável if not returnable
                atributo = 'Descartável' if not is_returnable else ''

            ocu_unit = it.get('Occupation') or it.get('occupation')
            try:
                ocu_unit_f = float(ocu_unit) if ocu_unit is not None else None
            except Exception:
                ocu_unit_f = None

            emb_grp = f"{emb} {grp_sub}".strip()
            if c not in agg:
                agg[c] = {'code': c, 'name': name, 'qty': q, 'emb_grp': emb_grp, 'peso': (gwf * q) if gwf is not None else None, 'atributo': atributo, 'ocupacao': (ocu_unit_f) if ocu_unit_f is not None else None}
            else:
                agg[c]['qty'] += q
                if gwf is not None:
                    agg[c]['peso'] = (agg[c].get('peso') or 0.0) + gwf * q
                if ocu_unit_f is not None:
                    agg[c]['ocupacao'] = (agg[c].get('ocupacao') or 0.0) + ocu_unit_f 

        # write product lines ordered by qty desc
        # for v in sorted(agg.values(), key=lambda x: x.get('assemblySequence', '')):
        for v in agg.values():
            code = v['code'][:13].ljust(13)
            name = v['name'][:42].ljust(42)
            qty = str(v['qty']).rjust(8)
            emb_grp = str(v.get('emb_grp') or '')[:16].ljust(16)
            peso = f"{(v['peso'] or 0):.2f}".rjust(10) if v.get('peso') is not None else ''.rjust(10)
            atr = v.get('atributo','').ljust(13)
            ocu_val = v.get('ocupacao')
            if isinstance(ocu_val, (int, float)):
                ocu = f"{ocu_val:.2f}".rjust(11)
            else:
                ocu = str(ocu_val or '').rjust(11)
            lines.append(f"            | 0       {code} {name}     {qty} {emb_grp} {peso} {atr} {ocu} | ")

        lines.append("            |                                                                                                                                     |")
        lines.append("            |=====================================================================================================================================|")
        lines.append("")

    # non-palletized items block
    if notp and (notp.get('Items') or notp.get('items')):
        # compute total weight for these
        total_np_weight = 0.0
        np_items = notp.get('Items') or notp.get('items', []) or []
        for it in np_items:
            tw = it.get('TotalWeight') or it.get('totalWeight')
            if tw is None:
                gw = it.get('GrossWeight') or it.get('grossWeight') or 0
                qty = it.get('Quantity') or it.get('quantity') or 0
                try:
                    tw = float(gw) * int(qty)
                except Exception:
                    tw = 0
            try:
                total_np_weight += float(tw)
            except Exception:
                pass
        lines.append(f"Produtos fora do caminhão - Peso: {total_np_weight:.2f}:")
        lines.append("-" * 140)
        
        # Build aggregated view for not-palletized items (similar to palletized items)
        agg = {}
        for it in np_items:
            c = str(it.get('Code') or it.get('code') or '')
            name = (it.get('Description') or it.get('description') or '').strip()
            q = int(it.get('Quantity') or it.get('quantity') or 0)
            gw = it.get('GrossWeight') or it.get('grossWeight')
            try:
                gwf = float(gw) if gw is not None else None
            except Exception:
                gwf = None
            
            # Extract packing info
            emb = ''
            grp_sub = ''
            try:
                packing = it.get('Packing') or it.get('packing') or {}
                emb = str(packing.get('Code') or packing.get('code') or '')
                grp = packing.get('Group') or packing.get('group')
                sub = packing.get('SubGroup') or packing.get('subGroup')
                if grp or sub:
                    grp_sub = f"{grp or ''}/{sub or ''}".strip('/')
            except Exception:
                emb = ''
                grp_sub = ''
            
            # Extract atributo
            atributo = ''
            is_marketplace = it.get('Marketplace') or it.get('marketplace')
            is_top = it.get('IsTopOfPallet') or it.get('isTopOfPallet')
            is_returnable = it.get('IsReturnable') or it.get('isReturnable')
            is_isotonic = it.get('IsIsotonicWater') or it.get('isIsotonicWater')
            is_chopp = it.get('IsChopp') or it.get('isChopp')
            
            # Prioridade: BinPack > TopoPallet > outros atributos
            if is_marketplace:
                atributo = 'BinPack'
            elif is_top:
                atributo = 'TopoPallet'
            elif is_returnable:
                atributo = 'Retornavel'
            elif is_isotonic:
                atributo = 'Isotonico'
            elif is_chopp:
                atributo = 'Chopp'
            else:
                atributo = 'Descartável' if not is_returnable else ''
            
            # Get occupation
            ocu_unit = it.get('Occupation') or it.get('occupation')
            try:
                ocu_unit_f = float(ocu_unit) if ocu_unit is not None else None
            except Exception:
                ocu_unit_f = None
            
            emb_grp = f"{emb} {grp_sub}".strip()
            
            if c not in agg:
                agg[c] = {
                    'code': c, 
                    'name': name, 
                    'qty': q, 
                    'emb_grp': emb_grp, 
                    'peso': (gwf * q) if gwf is not None else None, 
                    'atributo': atributo, 
                    'ocupacao': (ocu_unit_f) if ocu_unit_f is not None else None
                }
            else:
                agg[c]['qty'] += q
                if gwf is not None:
                    agg[c]['peso'] = (agg[c].get('peso') or 0.0) + gwf * q
                if ocu_unit_f is not None:
                    agg[c]['ocupacao'] = (agg[c].get('ocupacao') or 0.0) + ocu_unit_f
        
        # Write aggregated not-palletized items with full formatting
        for v in agg.values():
            code = v['code'][:13].ljust(13)
            name = v['name'][:60].ljust(60)
            qty = str(v['qty']).rjust(8)
            emb_grp = str(v.get('emb_grp') or '')[:16].ljust(16)
            peso = f"{(v['peso'] or 0):.2f}".rjust(10) if v.get('peso') is not None else ''.rjust(10)
            atr = v.get('atributo','').ljust(13)
            ocu_val = v.get('ocupacao')
            if isinstance(ocu_val, (int, float)):
                ocu = f"{ocu_val:.2f}".rjust(11)
            else:
                ocu = str(ocu_val or '').rjust(11)
            lines.append(f"            |          {code} {name} {qty} {emb_grp} {peso} {atr} {ocu} | ")
        lines.append("-" * 140)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate pallet product summary from palletize_result_map JSON")
    parser.add_argument("input", help="Path to palletize_result_map JSON file")
    parser.add_argument("--output", help="Output TXT path (optional)")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    data = load_json(in_path)
    summary = summarize_by_pallet(data)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = in_path.parent / "pallet_summary.txt"

    write_txt(summary, out_path)
    print(f"Wrote pallet summary to: {out_path}")


if __name__ == "__main__":
    main()
