import re
from pathlib import Path
from typing import List, Dict, Any

# reuse report building utilities from check.py to produce identical .md/.html output
from service.check import (
    build_table,
    save_markdown,
    save_html,
    load_json,
    count_input_items,
)
from service.check import normalize_code, aggregate_items_list, count_item_attributes


def _normalize_json_code_for_match(code: str) -> str:
    if not code:
        return ''
    # remove digits after leading 'P' so P01_A_... -> P_A_...
    return re.sub(r'^P\d+_', 'P_', str(code))


def _parse_txt_pallets(path: Path) -> List[Dict[str, Any]]:
    """Parse the TXT report and return a list of pallets with header code and items.

    Each returned pallet is {'code': '<header>', 'items': [{'code': str, 'quantity': int}, ...]}
    The parser expects pallet header lines starting with 'P_' or 'P_' anywhere at line start.
    Product lines are matched with a best-effort regex based on the project's TXT layout.
    """
    pallets = []
    cur = None
    # regex to capture header code: begins with P_ and continues until space or ' -'
    header_re = re.compile(r'^(P_[^\s-]+)')
    # product line regex: pipe, index, code (non-space), name (fixed width), qty (digits)
    prod_re = re.compile(r"\|\s*\d+\s+(\S{1,13})\s+(.{1,42})\s+(\d+)\s")

    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line:
                # blank line separates pallets sometimes
                continue

            m = header_re.match(line.strip())
            if m:
                code = m.group(1).strip()
                # start new pallet
                if cur:
                    pallets.append(cur)
                cur = {'code': code, 'items': []}
                continue

            if cur:
                pm = prod_re.search(line)
                if pm:
                    sku = pm.group(1).strip()
                    qty_text = pm.group(3).strip()
                    try:
                        qty = int(qty_text)
                    except Exception:
                        try:
                            qty = int(float(qty_text.replace(',', '.')))
                        except Exception:
                            qty = 0
                    cur['items'].append({'code': sku, 'quantity': qty})

    if cur:
        pallets.append(cur)

    return pallets


def _txt_to_pallet_dicts(txt_pallets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for tp in txt_pallets:
        code = tp.get('code') or ''
        # ensure code uses same high-level pattern (P_...)
        norm_code = code
        items = []
        for it in tp.get('items', []) or []:
            items.append({'code': it.get('code') or it.get('Code') or '', 'quantity': int(it.get('quantity') or 0)})

        out.append({'code': norm_code, 'items': items, 'occupation': None, 'weight': None, 'isClosed': False})
    return out


def run(txt_path: str, map_json_path: str, input_path: str = None, out_dir: str = 'reports') -> int:
    t_p = Path(txt_path)
    m_p = Path(map_json_path)
    outdir_p = Path(out_dir)

    if not t_p.exists():
        print(f"TXT file not found: {txt_path}")
        return 2
    if not m_p.exists():
        print(f"Map JSON file not found: {map_json_path}")
        return 2

    txt_pallets = _parse_txt_pallets(t_p)
    out_pallets = _txt_to_pallet_dicts(txt_pallets)

    # load the map JSON (reference)
    map_data = load_json(m_p)
    map_pallets = map_data.get('pallets') or map_data.get('Pallets') or []

    def _is_excluded(p: dict) -> bool:
        code = normalize_code(p.get("code") or p.get("Code"))
        return (code or "").upper() == "Z_ITEM_NAO_PALLETIZADO"

    # filter excluded
    map_pallets = [p for p in (map_pallets or []) if not _is_excluded(p)]
    out_pallets = [p for p in (out_pallets or []) if not _is_excluded(p)]

    # build lookup for txt pallets by their code (txt code is like 'P_A_01_1/35')
    txt_lookup = {}
    for p in out_pallets:
        key = (p.get('code') or '').strip()
        # aggregate items in txt pallet
        codes, qty_map, total_qty, distinct = aggregate_items_list([{'code': it.get('code'), 'quantity': it.get('quantity')} for it in p.get('items', [])])
        txt_lookup[key] = {
            'raw': p,
            'items_qty': qty_map,
            'items_total': total_qty,
            'items_codes': codes,
            'items_raw': p.get('items', [])
        }

    rows = []
    total_items_map = 0.0
    total_items_out = 0.0
    nonp_map = 0.0
    nonp_out = 0.0
    distinct_map_set = set()
    distinct_out_set = set()
    matched_items_sum = 0.0

    for mp in map_pallets:
        map_code = mp.get('code') or mp.get('Code') or ''
        norm_map_code = _normalize_json_code_for_match(map_code)

        # try to find corresponding txt pallet: normalized json -> remove digits after P
        txt_p = txt_lookup.get(norm_map_code)

        # aggregate map pallet items
        m_codes, m_qty_map, m_total, m_distinct = aggregate_items_list(mp.get('items') or [])
        total_items_map += m_total
        distinct_map_set |= set(m_codes)

        out_qty_map = {}
        out_total = 0.0
        out_codes = set()
        out_items_raw = []
        if txt_p:
            out_qty_map = txt_p['items_qty']
            out_total = txt_p['items_total']
            out_codes = txt_p['items_codes']
            out_items_raw = txt_p['items_raw']

        total_items_out += out_total
        distinct_out_set |= set(out_codes)

        # matched quantity = sum(min(map_qty, out_qty) for codes in map)
        matched_qty = sum(min(m_qty_map.get(code, 0.0), out_qty_map.get(code, 0.0)) for code in m_qty_map.keys())
        matched_items_sum += matched_qty

        extra_qty = max(0.0, out_total - matched_qty)
        missing_qty = max(0.0, m_total - matched_qty)

        inter = len(set(m_codes) & set(out_codes))
        union = len(set(m_codes) | set(out_codes))
        diff_count = (union - inter) if union else 0

        total_map = float(m_total or 0.0)
        total_out = float(out_total or 0.0)
        matched_pct_map = round((matched_qty / total_map) * 100.0, 2) if total_map > 0 else (100.0 if total_out == 0 else 0.0)
        matched_pct_out = round((matched_qty / total_out) * 100.0, 2) if total_out > 0 else (100.0 if total_map == 0 else 0.0)
        missing_pct_map = round((missing_qty / total_map) * 100.0, 2) if total_map > 0 else 0.0

        # attribute counts (txt has limited attrs)
        a_attrs = count_item_attributes(mp.get('items') or [])
        b_attrs = count_item_attributes(out_items_raw)

        row_code = normalize_code(norm_map_code)
        rows.append({
            'code': row_code,
            'in_map': True,
            'in_output': bool(txt_p),
            'items_in_map': int(m_total),
            'items_in_output': int(out_total),
            'items_equal': inter,
            'distinct_in_map': int(m_distinct),
            'distinct_in_output': int(len(out_codes)),
            'distinct_equal': inter,
            'items_different': diff_count,
            'matched_qty': matched_qty,
            'extra_qty': extra_qty,
            'matched_pct_map': matched_pct_map,
            'matched_pct_out': matched_pct_out,
            'missing_qty': missing_qty,
            'missing_pct_map': missing_pct_map,
            'matched_distinct': inter,
            'matched_distinct_pct_out': round((inter / len(out_codes) * 100.0), 2) if out_codes else (100.0 if m_distinct == 0 else 0.0),
            'missing_distinct': max(0, int(m_distinct) - inter),
            'extra_distinct': max(0, int(len(out_codes)) - inter),
            'weight_map': float(mp.get('weight') or mp.get('Weight') or 0.0),
            'weight_output': None,
            'occupation_map': float(mp.get('occupation') or mp.get('Occupation') or 0.0),
            'occupation_output': None,
            'isClosed_map': bool(mp.get('isClosed') or mp.get('IsClosed') or False),
            'isClosed_output': None,
            'similarity_percent': round((matched_qty / total_map) * 100.0, 2) if total_map > 0 else (100.0 if total_out == 0 else 0.0),
            'isTopOfPallet_map': int(a_attrs.get('isTopOfPallet', 0)),
            'isTopOfPallet_out': int(b_attrs.get('isTopOfPallet', 0)),
            'isChopp_map': int(a_attrs.get('isChopp', 0)),
            'isChopp_out': int(b_attrs.get('isChopp', 0)),
            'isReturnable_map': int(a_attrs.get('isReturnable', 0)),
            'isReturnable_out': int(b_attrs.get('isReturnable', 0)),
            'isIsotonicWater_map': int(a_attrs.get('isIsotonicWater', 0)),
            'isIsotonicWater_out': int(b_attrs.get('isIsotonicWater', 0)),
            'marketplace_map': int(a_attrs.get('marketplace', 0)),
            'marketplace_out': int(b_attrs.get('marketplace', 0)),
            'segregated_map': int(a_attrs.get('segregated', 0)),
            'segregated_out': int(b_attrs.get('segregated', 0)),
            'realocated_map': int(a_attrs.get('realocated', 0)),
            'realocated_out': int(b_attrs.get('realocated', 0)),
        })

    # handle txt-only pallets (present in TXT but not in map)
    # add rows for them too
    map_norms = set(_normalize_json_code_for_match(p.get('code') or p.get('Code') or '') for p in map_pallets)
    for txt_key, txt_val in txt_lookup.items():
        if txt_key in map_norms:
            continue
        out_total = txt_val['items_total']
        total_items_out += out_total
        distinct_out_set |= set(txt_val['items_codes'])
        a_attrs = {}
        b_attrs = count_item_attributes(txt_val['items_raw'])
        rows.append({
            'code': normalize_code(txt_key),
            'in_map': False,
            'in_output': True,
            'items_in_map': 0,
            'items_in_output': int(out_total),
            'items_equal': 0,
            'distinct_in_map': 0,
            'distinct_in_output': int(len(txt_val['items_codes'])),
            'distinct_equal': 0,
            'items_different': int(len(txt_val['items_codes'])),
            'matched_qty': 0.0,
            'extra_qty': float(out_total),
            'matched_pct_map': 0.0,
            'matched_pct_out': 0.0,
            'missing_qty': 0.0,
            'missing_pct_map': 0.0,
            'matched_distinct': 0,
            'matched_distinct_pct_out': 0.0,
            'missing_distinct': 0,
            'extra_distinct': int(len(txt_val['items_codes'])),
            'weight_map': None,
            'weight_output': None,
            'occupation_map': None,
            'occupation_output': None,
            'isClosed_map': None,
            'isClosed_output': None,
            'similarity_percent': 0.0,
            'isTopOfPallet_map': 0,
            'isTopOfPallet_out': int(b_attrs.get('isTopOfPallet', 0)),
            'isChopp_map': 0,
            'isChopp_out': int(b_attrs.get('isChopp', 0)),
            'isReturnable_map': 0,
            'isReturnable_out': int(b_attrs.get('isReturnable', 0)),
            'isIsotonicWater_map': 0,
            'isIsotonicWater_out': int(b_attrs.get('isIsotonicWater', 0)),
            'marketplace_map': 0,
            'marketplace_out': int(b_attrs.get('marketplace', 0)),
            'segregated_map': 0,
            'segregated_out': int(b_attrs.get('segregated', 0)),
            'realocated_map': 0,
            'realocated_out': int(b_attrs.get('realocated', 0)),
        })

    matched_items = matched_items_sum
    avg_sim_pct = round((matched_items / total_items_map) * 100.0, 2) if total_items_map > 0 else 0.0

    overall = {
        'total_codes_map': len(map_pallets),
        'total_codes_output': len(out_pallets),
        'matched': sum(1 for r in rows if r['in_map'] and r['in_output']),
        'matched_items': int(matched_items),
        'average_similarity': avg_sim_pct,
        'total_items_map': int(total_items_map),
        'total_items_output': int(total_items_out),
        'distinct_items_map': len(distinct_map_set),
        'distinct_items_output': len(distinct_out_set),
        'palletized_items_map': int(total_items_map - nonp_map),
        'palletized_items_output': int(total_items_out - nonp_out),
        'nonpalletized_items_map': int(nonp_map),
        'nonpalletized_items_output': int(nonp_out),
    }

    # augment overall with input counts
    total_in = 0
    distinct_in = 0
    if input_path:
        ip = Path(input_path)
        if ip.exists():
            input_data = load_json(ip)
            total_in, distinct_in = count_input_items(input_data)
    overall['total_items_input'] = total_in
    overall['distinct_items_input'] = distinct_in

    md_path = save_markdown(rows, overall, outdir_p)
    html_path = save_html(rows, overall, outdir_p)

    print(f"Report saved to: {md_path}")
    print(f"HTML report saved to: {html_path}")

    return 0


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate check report comparing TXT output to map JSON')
    parser.add_argument('--txt', required=True, help='Path to textual result file (620768-Resultado.txt)')
    parser.add_argument('--json', required=True, help='Path to generated palletize_result_map_*.json (map reference)')
    parser.add_argument('--input', required=False, help='Optional input JSON to compute input totals')
    parser.add_argument('--out-dir', required=False, default='reports', help='Output directory for reports')
    args = parser.parse_args()

    exit(run(args.txt, args.json, args.input, args.out_dir))
