"""check.py

Compara `output.json` (referência) com `palletize_result_map_107527.json` (map)
Gera um relatório Markdown em `reports/check_report_<ts>.md` com uma tabela resumida.
"""
from __future__ import annotations

import argparse
import json
import html as _html
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def count_input_items(input_data: dict) -> Tuple[int, int]:
    """Return (total_items, distinct_item_codes) present in the input JSON (Orders->Items).

    Quantities in input items may be a dict (e.g. {'Sales':n,'Unit':m}) or a number.
    We sum all numeric fields when Quantity is a dict.
    """
    total = 0
    distinct = set()
    if not input_data:
        return 0, 0

    for order in input_data.get("Orders", []) or []:
        for it in order.get("Items", []) or []:
            code = normalize_code(it.get("Code") or it.get("code"))
            if code:
                distinct.add(code)
            q = 0
            qobj = it.get("Quantity") or it.get("quantity")
            if isinstance(qobj, dict):
                for v in qobj.values():
                    try:
                        q += float(v or 0)
                    except Exception:
                        pass
            else:
                try:
                    q = float(qobj or 0)
                except Exception:
                    q = 0

            total += q

    return int(total), len(distinct)


def normalize_code(code) -> str:
    if code is None:
        return ""
    return str(code).strip()


def aggregate_items_list(items: List[dict]) -> Tuple[set, Dict[str, float], float, int]:
    """Return distinct item codes set, quantity map (code->sum qty), total qty and distinct count."""
    codes = set()
    qty_map: Dict[str, float] = {}
    for it in items or []:
        code = normalize_code(it.get("code") or it.get("Code"))
        codes.add(code)
        try:
            q = float(it.get("quantity") or it.get("Quantity") or 0)
        except Exception:
            q = 0.0
        qty_map[code] = qty_map.get(code, 0.0) + q

    total_qty = sum(qty_map.values())
    distinct_count = len(codes)
    return codes, qty_map, total_qty, distinct_count


def count_item_attributes(items: List[dict]) -> Dict[str, int]:
    """Count specific boolean/flag attributes over a list of items.

    Returns counts for: isTopOfPallet, isChopp, isReturnable, isIsotonicWater,
    marketplace (non-null), segregated, realocated/reallocated.
    """
    attrs = {
        "isTopOfPallet": 0,
        "isChopp": 0,
        "isReturnable": 0,
        "isIsotonicWater": 0,
        "marketplace": 0,
        "segregated": 0,
        "realocated": 0,
    }

    def get_val(it: dict, key: str):
        # try exact key, then PascalCase variant
        if key in it:
            return it.get(key)
        k2 = key[0].upper() + key[1:]
        return it.get(k2)

    for it in items or []:
        try:
            if bool(get_val(it, "isTopOfPallet")):
                attrs["isTopOfPallet"] += 1
        except Exception:
            pass
        try:
            if bool(get_val(it, "isChopp")):
                attrs["isChopp"] += 1
        except Exception:
            pass
        try:
            if bool(get_val(it, "isReturnable")):
                attrs["isReturnable"] += 1
        except Exception:
            pass
        try:
            if bool(get_val(it, "isIsotonicWater")):
                attrs["isIsotonicWater"] += 1
        except Exception:
            pass
        # marketplace: count when non-null / non-empty
        try:
            mp = get_val(it, "marketplace")
            if mp is not None and str(mp).strip() != "":
                attrs["marketplace"] += 1
        except Exception:
            pass
        try:
            if bool(get_val(it, "segregated")):
                attrs["segregated"] += 1
        except Exception:
            pass
        # handle both spellings
        try:
            if bool(get_val(it, "realocated")) or bool(get_val(it, "reallocated")):
                attrs["realocated"] += 1
        except Exception:
            pass

    return attrs


def pallet_summary_min(p: dict) -> dict:
    if not p:
        return {}
    items = p.get("items") or p.get("Items") or []
    codes, qty_map, total_qty, distinct = aggregate_items_list(items)
    return {
        "code": normalize_code(p.get("code") or p.get("Code")),
        "occupation": float(p.get("occupation") or p.get("Occupation") or 0.0),
        "weight": float(p.get("weight") or p.get("Weight") or 0.0),
        "isClosed": bool(p.get("isClosed") or p.get("IsClosed") or False),
        "items_codes": codes,
        "items_qty": qty_map,
        "items_total": total_qty,
        "distinct_count": distinct,
    }


def similarity(a: dict, b: dict) -> float:
    """Similarity measured as proportion of map items that are present in the same pallet in output.

    Implementation: sum over item codes of min(q_map, q_out) / total_map_qty.
    Returns percentage [0.0, 100.0]."""
    if not a or not b:
        return 0.0

    a_qty: Dict[str, float] = a.get("items_qty", {}) or {}
    b_qty: Dict[str, float] = b.get("items_qty", {}) or {}

    # matched quantity = sum of min quantities for each code present in the map
    matched = 0.0
    for code, q in a_qty.items():
        matched += min(q, b_qty.get(code, 0.0))

    total_map = float(a.get("items_total", sum(a_qty.values()) if a_qty else 0.0) or 0.0)
    if total_map <= 0.0:
        # if there is nothing to compare, consider fully similar when both empty
        total_out = float(b.get("items_total", sum(b_qty.values()) if b_qty else 0.0) or 0.0)
        return 100.0 if total_out == 0.0 else 0.0

    percent = (matched / total_map) * 100.0
    return round(percent, 2)


def build_table(map_pallets: List[dict], out_pallets: List[dict]) -> Tuple[List[dict], dict]:
    def aggregate_pallets_by_code(pallets: List[dict]) -> List[dict]:
        """Combine pallets that share the same `code` into a single pallet entry.

        - items lists are concatenated
        - weight and occupation are summed (converted to float)
        - isClosed is OR'ed
        """
        agg = {}
        for p in pallets or []:
            code = normalize_code(p.get("code") or p.get("Code"))
            if not code:
                continue
            items = p.get("items") or p.get("Items") or []
            try:
                weight = float(p.get("weight") or p.get("Weight") or 0.0)
            except Exception:
                weight = 0.0
            try:
                occupation = float(p.get("occupation") or p.get("Occupation") or 0.0)
            except Exception:
                occupation = 0.0
            isClosed = bool(p.get("isClosed") or p.get("IsClosed") or False)

            if code not in agg:
                # copy relevant fields
                agg[code] = {
                    "code": code,
                    "items": list(items),
                    "weight": weight,
                    "occupation": occupation,
                    "isClosed": isClosed,
                }
            else:
                agg[code]["items"].extend(items)
                agg[code]["weight"] += weight
                agg[code]["occupation"] += occupation
                agg[code]["isClosed"] = agg[code]["isClosed"] or isClosed

        return list(agg.values())

    map_pallets = aggregate_pallets_by_code(map_pallets)
    out_pallets = aggregate_pallets_by_code(out_pallets)

    amap = {normalize_code(p.get("code") or p.get("Code")): p for p in map_pallets}
    bmap = {normalize_code(p.get("code") or p.get("Code")): p for p in out_pallets}
    codes = sorted(set(amap.keys()) | set(bmap.keys()))

    # Overall totals: total items, distinct item codes, palletized vs non-palletized
    def is_non_pallet_code(code: str) -> bool:
        if not code:
            return False
        c = code.upper()
        return ("NAO" in c and "PALLET" in c) or ("NOT" in c and "PALLET" in c) or c.startswith("Z_") and "NAO" in c

    total_items_map = 0.0
    total_items_out = 0.0
    distinct_map_set = set()
    distinct_out_set = set()
    nonp_map = 0.0
    nonp_out = 0.0

    for code, p in amap.items():
        s = pallet_summary_min(p)
        qty = float(s.get("items_total", 0.0) or 0.0)
        total_items_map += qty
        distinct_map_set |= set(s.get("items_codes", []))
        if is_non_pallet_code(code):
            nonp_map += qty

    for code, p in bmap.items():
        s = pallet_summary_min(p)
        qty = float(s.get("items_total", 0.0) or 0.0)
        total_items_out += qty
        distinct_out_set |= set(s.get("items_codes", []))
        if is_non_pallet_code(code):
            nonp_out += qty

    palletized_map = int(total_items_map - nonp_map)
    palletized_out = int(total_items_out - nonp_out)
    total_items_map = int(total_items_map)
    total_items_out = int(total_items_out)
    distinct_map_total = len(distinct_map_set)
    distinct_out_total = len(distinct_out_set)

    rows = []
    sims = []
    for code in codes:
        a = pallet_summary_min(amap.get(code)) if code in amap else {}
        b = pallet_summary_min(bmap.get(code)) if code in bmap else {}

        # attribute counts per pallet (map vs output)
        a_items_raw = amap.get(code, {}).get("items") if code in amap else []
        b_items_raw = bmap.get(code, {}).get("items") if code in bmap else []
        a_attrs = count_item_attributes(a_items_raw)
        b_attrs = count_item_attributes(b_items_raw)

        a_count = float(a.get("items_total", 0))
        b_count = float(b.get("items_total", 0))
        a_codes = set(a.get("items_codes", []))
        b_codes = set(b.get("items_codes", []))
        inter = len(a_codes & b_codes)
        union = len(a_codes | b_codes)
        diff_count = (union - inter) if union else 0

        # quantity-based matching
        a_qty = a.get("items_qty", {}) or {}
        b_qty = b.get("items_qty", {}) or {}
        matched_qty = sum(min(a_qty.get(code, 0.0), b_qty.get(code, 0.0)) for code in a_qty.keys())
        total_map = float(a_count or 0.0)
        total_out = float(b_count or 0.0)
        matched_pct_map = round((matched_qty / total_map) * 100.0, 2) if total_map > 0 else (100.0 if total_out == 0 else 0.0)
        matched_pct_out = round((matched_qty / total_out) * 100.0, 2) if total_out > 0 else (100.0 if total_map == 0 else 0.0)
        missing_qty = max(0.0, total_map - matched_qty)
        missing_pct_map = round((missing_qty / total_map) * 100.0, 2) if total_map > 0 else 0.0
        # items present in output but not matched to map (extras)
        extra_qty = max(0.0, total_out - matched_qty)
        extra_pct_out = round((extra_qty / total_out) * 100.0, 2) if total_out > 0 else 0.0

        # distinct matching
        matched_distinct = inter
        distinct_map = len(a_codes)
        distinct_out = len(b_codes)
        matched_distinct_pct_out = round((matched_distinct / distinct_out) * 100.0, 2) if distinct_out > 0 else (100.0 if distinct_map == 0 else 0.0)
        missing_distinct = max(0, distinct_map - matched_distinct)

        sim = similarity(a, b)
        if a and b:
            sims.append(sim)

        rows.append(
            {
                "code": code,
                "in_map": bool(a),
                "in_output": bool(b),
                "items_in_map": int(a_count),
                "items_in_output": int(b_count),
                "items_equal": inter,
                "distinct_in_map": distinct_map,
                "distinct_in_output": distinct_out,
                "distinct_equal": matched_distinct,
                "items_different": diff_count,
                "matched_qty": matched_qty,
                "extra_qty": extra_qty,
                "matched_pct_map": matched_pct_map,
                "matched_pct_out": matched_pct_out,
                "missing_qty": missing_qty,
                "missing_pct_map": missing_pct_map,
                "matched_distinct": matched_distinct,
                "matched_distinct_pct_out": matched_distinct_pct_out,
                "missing_distinct": missing_distinct,
                "extra_distinct": max(0, distinct_out - matched_distinct),
                "weight_map": a.get("weight") if a else None,
                "weight_output": b.get("weight") if b else None,
                "occupation_map": a.get("occupation") if a else None,
                "occupation_output": b.get("occupation") if b else None,
                "isClosed_map": a.get("isClosed") if a else None,
                "isClosed_output": b.get("isClosed") if b else None,
                "similarity_percent": sim,
                # attribute counts
                "isTopOfPallet_map": int(a_attrs.get("isTopOfPallet", 0)),
                "isTopOfPallet_out": int(b_attrs.get("isTopOfPallet", 0)),
                "isChopp_map": int(a_attrs.get("isChopp", 0)),
                "isChopp_out": int(b_attrs.get("isChopp", 0)),
                "isReturnable_map": int(a_attrs.get("isReturnable", 0)),
                "isReturnable_out": int(b_attrs.get("isReturnable", 0)),
                "isIsotonicWater_map": int(a_attrs.get("isIsotonicWater", 0)),
                "isIsotonicWater_out": int(b_attrs.get("isIsotonicWater", 0)),
                "marketplace_map": int(a_attrs.get("marketplace", 0)),
                "marketplace_out": int(b_attrs.get("marketplace", 0)),
                "segregated_map": int(a_attrs.get("segregated", 0)),
                "segregated_out": int(b_attrs.get("segregated", 0)),
                "realocated_map": int(a_attrs.get("realocated", 0)),
                "realocated_out": int(b_attrs.get("realocated", 0)),
            }
        )

    # compute how many individual items (quantity) were matched to the correct pallet
    matched_items = sum(float(r.get('matched_qty', 0.0)) for r in rows)
    # average similarity KPI = proportion of items from the map that stayed in the correct pallet
    avg_sim_pct = round((matched_items / total_items_map) * 100.0, 2) if total_items_map > 0 else 0.0

    overall = {
        "total_codes_map": len(amap),
        "total_codes_output": len(bmap),
        "matched": sum(1 for r in rows if r["in_map"] and r["in_output"]),
        "matched_items": int(matched_items),
        "average_similarity": avg_sim_pct,
        "total_items_map": total_items_map,
        "total_items_output": total_items_out,
        "distinct_items_map": distinct_map_total,
        "distinct_items_output": distinct_out_total,
        "palletized_items_map": palletized_map,
        "palletized_items_output": palletized_out,
        "nonpalletized_items_map": int(nonp_map),
        "nonpalletized_items_output": int(nonp_out),
    }

    return rows, overall


def save_markdown(rows: List[dict], overall: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    md = out_dir / f"check_report_{ts}.md"
    with open(md, "w", encoding="utf-8") as fh:
        fh.write("# Relatório de Checagem de Paletes\n\n")
        fh.write(f"**Gerado em:** {datetime.utcnow().isoformat()}Z\n\n")
        fh.write("## Resumo\n\n")
        # two-column summary table: left = pallets, right = items
        fh.write("| **Paletes / Similaridade** | **Itens (map / out)** |\n")
        fh.write("|---|---|\n")
        left = (
            f"Paletes no mapa: **{overall['total_codes_map']}**<br>"
            f"Paletes na saída: **{overall['total_codes_output']}**<br>"
            f"Paletes coincidentes: **{overall['matched']}**<br>"
            f"Similaridade média: **{overall['average_similarity']}%**"
        )
        right = (
            f"Itens totais: **{overall.get('total_items_map',0)} / {overall.get('total_items_output',0)}**<br>"
            f"Itens distintos: **{overall.get('distinct_items_map',0)} / {overall.get('distinct_items_output',0)}**<br>"
            f"Palletizados: **{overall.get('palletized_items_map',0)} / {overall.get('palletized_items_output',0)}**<br>"
            f"Não palletizados: **{overall.get('nonpalletized_items_map',0)} / {overall.get('nonpalletized_items_output',0)}**<br>"
            f"Input (total/distinct): **{overall.get('total_items_input',0)} / {overall.get('distinct_items_input',0)}**"
        )
        fh.write(f"| {left} | {right} |\n\n")

        # Tabela de presença separada
        fh.write("## Tabela de Presença\n\n")
        fh.write("| code | in_map | in_output |\n")
        fh.write("|---|:---:|:---:|\n")
        for r in rows:
            in_map = '✅' if r['in_map'] else ''
            in_out = '✅' if r['in_output'] else ''
            fh.write(f"| {r['code']} | {in_map} | {in_out} |\n")

        fh.write("\n## Tabela de Comparação\n\n")
        fh.write("| code | qtd result / qtd output | matched | extra (no result) | missing (no map) | peso (res/out) | occ (res/out) | sim % (map) | sim % (out) |\n")
        fh.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for r in rows:
            qty_col = f"{r['items_in_map']} / {r['items_in_output']}"
            matched = f"{r.get('matched_qty', 0):.2f}"
            extra = f"{r.get('extra_qty', 0):.2f}"
            missing = f"{r.get('missing_qty', 0):.2f}"
            weight_map_val = r.get('weight_map')
            weight_output_val = r.get('weight_output')
            wmap = f"{weight_map_val:.2f}" if weight_map_val is not None else ""
            wout = f"{weight_output_val:.2f}" if weight_output_val is not None else ""
            wcol = f"{wmap} / {wout}"

            occ_map_val = r.get('occupation_map')
            occ_out_val = r.get('occupation_output')
            omap = f"{occ_map_val:.2f}" if occ_map_val is not None else ""
            oout = f"{occ_out_val:.2f}" if occ_out_val is not None else ""
            ocol = f"{omap} / {oout}"
            sim_map = f"{r.get('matched_pct_map', 0):.2f}%"
            sim_out = f"{r.get('matched_pct_out', 0):.2f}%"
            fh.write(f"| {r['code']} | {qty_col} | {matched} | {extra} | {missing} | {wcol} | {ocol} | {sim_map} | {sim_out} |\n")

        # Segunda tabela: itens distintos (por código)
        fh.write("\n\n## Tabela por Itens Distintos\n\n")
        fh.write("| code | distinct map / distinct out | matched_distinct | extra_distinct | missing_distinct | peso (res/out) | occ (res/out) | sim % (map) | sim % (out) |\n")
        fh.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for r in rows:
            distinct_col = f"{r.get('distinct_in_map',0)} / {r.get('distinct_in_output',0)}"
            matched_d = f"{r.get('matched_distinct',0)}"
            extra_d = f"{r.get('extra_distinct',0)}"
            missing_d = f"{r.get('missing_distinct',0)}"
            weight_map_val = r.get('weight_map')
            weight_output_val = r.get('weight_output')
            wmap = f"{weight_map_val:.2f}" if weight_map_val is not None else ""
            wout = f"{weight_output_val:.2f}" if weight_output_val is not None else ""
            wcol = f"{wmap} / {wout}"

            occ_map_val = r.get('occupation_map')
            occ_out_val = r.get('occupation_output')
            omap = f"{occ_map_val:.2f}" if occ_map_val is not None else ""
            oout = f"{occ_out_val:.2f}" if occ_out_val is not None else ""
            ocol = f"{omap} / {oout}"
            sim_map = f"{r.get('matched_pct_map', 0):.2f}%"
            sim_out = f"{r.get('matched_pct_out', 0):.2f}%"
            fh.write(f"| {r['code']} | {distinct_col} | {matched_d} | {extra_d} | {missing_d} | {wcol} | {ocol} | {sim_map} | {sim_out} |\n")

        # Terceira tabela: contagem por tipos de itens/flags (colunas separadas)
        fh.write("\n\n## Tabela por Tipos de Itens (flags)\n\n")
        fh.write("| code | top | chopp | returnable | isotonic | marketplace | segregated | realocated |\n")
        fh.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for r in rows:
            top = f"{r.get('isTopOfPallet_map',0)} / {r.get('isTopOfPallet_out',0)}"
            chopp = f"{r.get('isChopp_map',0)} / {r.get('isChopp_out',0)}"
            ret = f"{r.get('isReturnable_map',0)} / {r.get('isReturnable_out',0)}"
            iso = f"{r.get('isIsotonicWater_map',0)} / {r.get('isIsotonicWater_out',0)}"
            mp = f"{r.get('marketplace_map',0)} / {r.get('marketplace_out',0)}"
            seg = f"{r.get('segregated_map',0)} / {r.get('segregated_out',0)}"
            rea = f"{r.get('realocated_map',0)} / {r.get('realocated_out',0)}"
            fh.write(f"| {r['code']} | {top} | {chopp} | {ret} | {iso} | {mp} | {seg} | {rea} |\n")

    return md


def save_html(rows: List[dict], overall: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    html_path = out_dir / f"check_report_{ts}.html"

    def esc(x):
        return _html.escape(str(x)) if x is not None else ""

    css = """
    body{font-family: Arial, sans-serif; margin:20px; color:#222}
    .cards{display:flex;gap:12px;margin-bottom:18px}
    .col{flex:1;display:flex;flex-direction:column;gap:8px}
    .card{background:#f7f9fb;padding:12px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
    .card h3{margin:0;font-size:14px}
    table{width:100%;border-collapse:collapse}
    th,td{padding:8px;border-bottom:1px solid #e6eef6;text-align:left}
    th{background:#f0f6fb}
    tr:nth-child(even){background:#fbfdff}
    .bar{height:10px;background:#e6eef6;border-radius:6px;overflow:hidden}
    .bar > i{display:block;height:100%;background:linear-gradient(90deg,#4caf50,#2b8cff)}
    .small{font-size:12px;color:#666}
    """

    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write("<html><head><meta charset='utf-8'><title>Relatório de Checagem</title>")
        fh.write(f"<style>{css}</style></head><body>")
        fh.write(f"<h1>Relatório de Checagem de Paletes</h1>")
        fh.write(f"<p class=small>Gerado em: {datetime.utcnow().isoformat()}Z</p>")

        fh.write('<div class="cards">')
        # left column: pallets + similarity
        fh.write('<div class="col">')
        fh.write(f"<div class=card><h3>Paletes no mapa</h3><div>{overall['total_codes_map']}</div></div>")
        fh.write(f"<div class=card><h3>Paletes na saída</h3><div>{overall['total_codes_output']}</div></div>")
        fh.write(f"<div class=card><h3>Coincidências</h3><div>{overall['matched']}</div></div>")
        fh.write(f"<div class=card><h3>Similaridade média</h3><div>{overall['average_similarity']}%</div></div>")
        fh.write('</div>')
        # right column: items
        fh.write('<div class="col">')
        fh.write(f"<div class=card><h3>Itens totais (map/out)</h3><div>{overall.get('total_items_map',0)} / {overall.get('total_items_output',0)}</div></div>")
        fh.write(f"<div class=card><h3>Itens distintos (map/out)</h3><div>{overall.get('distinct_items_map',0)} / {overall.get('distinct_items_output',0)}</div></div>")
        fh.write(f"<div class=card><h3>Palletizados (map/out)</h3><div>{overall.get('palletized_items_map',0)} / {overall.get('palletized_items_output',0)}</div></div>")
        fh.write(f"<div class=card><h3>Não palletizados (map/out)</h3><div>{overall.get('nonpalletized_items_map',0)} / {overall.get('nonpalletized_items_output',0)}</div></div>")
        fh.write(f"<div class=card><h3>Input (total/distinct)</h3><div>{overall.get('total_items_input',0)} / {overall.get('distinct_items_input',0)}</div></div>")
        fh.write('</div>')
        fh.write('</div>')

        # Tabela de presença separada (HTML)
        fh.write('<h2>Tabela de Presença</h2>')
        fh.write('<table>')
        fh.write('<thead><tr><th>code</th><th>in_map</th><th>in_output</th></tr></thead><tbody>')
        for r in rows:
            im = '✅' if r['in_map'] else ''
            io = '✅' if r['in_output'] else ''
            fh.write(f"<tr><td>{esc(r['code'])}</td><td>{esc(im)}</td><td>{esc(io)}</td></tr>")
        fh.write('</tbody></table>')

        fh.write('<h2>Tabela de Comparação</h2>')
        fh.write('<table>')
        fh.write('<thead><tr>')
        fh.write('<th>code</th><th>qtd result / qtd output</th>'
             '<th>matched</th><th>extra (no result)</th><th>missing (no map)</th>'
             '<th>peso (res / out)</th><th>occ (res / out)</th><th>sim % (map)</th><th>sim % (out)</th>')
        fh.write('</tr></thead><tbody>')

        for r in rows:
            sim = float(r.get("similarity_percent") or 0.0)
            bar = f'<div class="bar"><i style="width:{max(0,min(100,sim))}%"></i></div>'
            qty_col = f"{r['items_in_map']} / {r['items_in_output']}"
            matched_qty = f"{r.get('matched_qty', 0):.2f}"
            extra_qty = f"{r.get('extra_qty', 0):.2f}"
            missing_qty = f"{r.get('missing_qty', 0):.2f}"
            weight_map_val = r.get('weight_map')
            weight_output_val = r.get('weight_output')
            wmap = f"{weight_map_val:.2f}" if weight_map_val is not None else ""
            wout = f"{weight_output_val:.2f}" if weight_output_val is not None else ""
            wcol = f"{wmap} / {wout}"

            occ_map_val = r.get('occupation_map')
            occ_out_val = r.get('occupation_output')
            omap = f"{occ_map_val:.2f}" if occ_map_val is not None else ""
            oout = f"{occ_out_val:.2f}" if occ_out_val is not None else ""
            ocol = f"{omap} / {oout}"
            sim_map = f"{r.get('matched_pct_map', 0):.2f}%"
            sim_out = f"{r.get('matched_pct_out', 0):.2f}%"

            fh.write('<tr>')
            fh.write(f"<td>{esc(r['code'])}</td>")
            fh.write(f"<td>{esc(qty_col)}</td>")
            fh.write(f"<td>{esc(matched_qty)}</td>")
            fh.write(f"<td>{esc(extra_qty)}</td>")
            fh.write(f"<td>{esc(missing_qty)}</td>")
            fh.write(f"<td>{esc(wcol)}</td>")
            fh.write(f"<td>{esc(ocol)}</td>")
            fh.write(f"<td>{esc(sim_map)}</td>")
            fh.write(f"<td>{esc(sim_out)}</td>")
            fh.write('</tr>')

        fh.write('</tbody></table>')

        # Segunda tabela: itens distintos
        fh.write('<h2>Tabela por Itens Distintos</h2>')
        fh.write('<table>')
        fh.write('<thead><tr>')
        fh.write('<th>code</th><th>distinct map / distinct out</th>'
             '<th>matched_distinct</th><th>extra_distinct</th><th>missing_distinct</th>'
             '<th>peso (res / out)</th><th>occ (res / out)</th><th>sim % (map)</th><th>sim % (out)</th>')
        fh.write('</tr></thead><tbody>')

        for r in rows:
            dmap = r.get('distinct_in_map', 0)
            dout = r.get('distinct_in_output', 0)
            dequal = r.get('distinct_equal', 0)
            extra_d = r.get('extra_distinct', 0)
            missing_d = r.get('missing_distinct', 0)
            sim = float(r.get("similarity_percent") or 0.0)
            bar = f'<div class="bar"><i style="width:{max(0,min(100,sim))}%"></i></div>'
            distinct_col = f"{dmap} / {dout}"
            weight_map_val = r.get('weight_map')
            weight_output_val = r.get('weight_output')
            wmap = f"{weight_map_val:.2f}" if weight_map_val is not None else ""
            wout = f"{weight_output_val:.2f}" if weight_output_val is not None else ""
            wcol = f"{wmap} / {wout}"

            occ_map_val = r.get('occupation_map')
            occ_out_val = r.get('occupation_output')
            omap = f"{occ_map_val:.2f}" if occ_map_val is not None else ""
            oout = f"{occ_out_val:.2f}" if occ_out_val is not None else ""
            ocol = f"{omap} / {oout}"
            sim_map = f"{r.get('matched_pct_map', 0):.2f}%"
            sim_out = f"{r.get('matched_pct_out', 0):.2f}%"

            fh.write('<tr>')
            fh.write(f"<td>{esc(r['code'])}</td>")
            fh.write(f"<td>{esc(distinct_col)}</td>")
            fh.write(f"<td>{esc(dequal)}</td>")
            fh.write(f"<td>{esc(extra_d)}</td>")
            fh.write(f"<td>{esc(missing_d)}</td>")
            fh.write(f"<td>{esc(wcol)}</td>")
            fh.write(f"<td>{esc(ocol)}</td>")
            fh.write(f"<td>{esc(sim_map)}</td>")
            fh.write(f"<td>{esc(sim_out)}</td>")
            fh.write('</tr>')

        fh.write('</tbody></table>')

        # Terceira tabela: contagem por tipos de itens/flags
        fh.write('<h2>Tabela por Tipos de Itens (flags)</h2>')
        fh.write('<table>')
        fh.write('<thead><tr>')
        fh.write('<th>code</th><th>top</th><th>chopp</th><th>returnable</th><th>isotonic</th><th>marketplace</th><th>segregated</th><th>realocated</th>')
        fh.write('</tr></thead><tbody>')

        for r in rows:
            top = f"{r.get('isTopOfPallet_map',0)} / {r.get('isTopOfPallet_out',0)}"
            chopp = f"{r.get('isChopp_map',0)} / {r.get('isChopp_out',0)}"
            ret = f"{r.get('isReturnable_map',0)} / {r.get('isReturnable_out',0)}"
            iso = f"{r.get('isIsotonicWater_map',0)} / {r.get('isIsotonicWater_out',0)}"
            mp = f"{r.get('marketplace_map',0)} / {r.get('marketplace_out',0)}"
            seg = f"{r.get('segregated_map',0)} / {r.get('segregated_out',0)}"
            rea = f"{r.get('realocated_map',0)} / {r.get('realocated_out',0)}"

            fh.write('<tr>')
            fh.write(f"<td>{esc(r['code'])}</td>")
            fh.write(f"<td>{esc(top)}</td>")
            fh.write(f"<td>{esc(chopp)}</td>")
            fh.write(f"<td>{esc(ret)}</td>")
            fh.write(f"<td>{esc(iso)}</td>")
            fh.write(f"<td>{esc(mp)}</td>")
            fh.write(f"<td>{esc(seg)}</td>")
            fh.write(f"<td>{esc(rea)}</td>")
            fh.write('</tr>')

        fh.write('</tbody></table>')
        fh.write('</body></html>')

    return html_path


def run_reports(map_json=None, output_json=None, input_json=None) -> None:
    parser = argparse.ArgumentParser(description="Check similarity between map and output pallet JSONs and generate markdown report")
    # parser.add_argument("map_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\AS\output\palletize_result_map_107527.json")
    # parser.add_argument("output_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\AS\output.json")
    # parser.add_argument("input_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\AS\inputcompleto.json")

    if map_json and output_json and input_json:
        parser.add_argument("map_json", nargs="?", default=map_json)
        parser.add_argument("output_json", nargs="?", default=output_json)
        parser.add_argument("input_json", nargs="?", default=input_json)
    else:
        parser.add_argument("map_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\route\612481\output\palletize_result_map_612481.json")
        parser.add_argument("output_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\route\612481\output.json")
        parser.add_argument("input_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\route\612481\input.json")
    # parser.add_argument("input_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\AS\input.json")


    # parser.add_argument("input_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\AS\input.json")
    parser.add_argument("--out-dir", default="reports")
    args = parser.parse_args()

    map_path = Path(args.map_json)
    out_path = Path(args.output_json)

    if not map_path.exists():
        print(f"Map file not found: {map_path}")
        return
    if not out_path.exists():
        print(f"Output file not found: {out_path}")
        return

    map_data = load_json(map_path)
    out_data = load_json(out_path)
    input_path = Path(args.input_json)
    input_data = None
    if input_path.exists():
        input_data = load_json(input_path)
    else:
        # attempt to read if user passed JSON string
        try:
            input_data = load_json(Path(args.input_json))
        except Exception:
            input_data = None

    map_pallets = map_data.get("pallets") or map_data.get("Pallets") or []
    out_pallets = out_data.get("pallets") or out_data.get("Pallets") or []

    def _is_excluded(p: dict) -> bool:
        code = normalize_code(p.get("code") or p.get("Code"))
        return (code or "").upper() == "Z_ITEM_NAO_PALLETIZADO"

    map_pallets = [p for p in (map_pallets or []) if not _is_excluded(p)]
    out_pallets = [p for p in (out_pallets or []) if not _is_excluded(p)]


    rows, overall = build_table(map_pallets, out_pallets)
    # augment overall with input counts
    total_in, distinct_in = count_input_items(input_data)
    overall["total_items_input"] = total_in
    overall["distinct_items_input"] = distinct_in
    md_path = save_markdown(rows, overall, Path(args.out_dir))
    html_path = save_html(rows, overall, Path(args.out_dir))
    print(f"Report saved to: {md_path}")
    print(f"HTML report saved to: {html_path}")

    # Print concise metrics summary to console for quick inspection
    try:
        avg_sim = overall.get('average_similarity', 0.0)
        matched_items = overall.get('matched_items', 0)
        total_map = overall.get('total_items_map', 0)
        total_out = overall.get('total_items_output', 0)
        palletized_map = overall.get('palletized_items_map', 0)
        palletized_out = overall.get('palletized_items_output', 0)
        nonp_map = overall.get('nonpalletized_items_map', 0)
        nonp_out = overall.get('nonpalletized_items_output', 0)
        distinct_map = overall.get('distinct_items_map', 0)
        distinct_out = overall.get('distinct_items_output', 0)
        matched_pallets = overall.get('matched', 0)
        total_pallets_map = overall.get('total_codes_map', 0)

        pct_matched_pallets = (matched_pallets / total_pallets_map * 100.0) if total_pallets_map else 0.0

        print("\n=== Métricas Resumidas ===")
        print(f"Similaridade média: {avg_sim:.2f}%")
        print(f"Paletes correspondentes: {matched_pallets} / {total_pallets_map} ({pct_matched_pallets:.2f}%)")
        print(f"Itens correspondentes (quantidade): {matched_items} / {total_map} (map) | saída: {total_out}")
        print(f"Itens palletizados (map/out): {palletized_map} / {palletized_out}")
        print(f"Itens não-palletizados (map/out): {nonp_map} / {nonp_out}")
        print(f"Itens distintos (map/out): {distinct_map} / {distinct_out}")
        print("========================\n")
    except Exception as e:
        print(f"Erro ao imprimir métricas: {e}")


if __name__ == "__main__":
    run_reports()
