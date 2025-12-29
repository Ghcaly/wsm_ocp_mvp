import re
import csv
from pathlib import Path
import argparse


def parse_pallet_file(path: Path):
    """Parse a TXT report produced by `generate_pallet_summary` style output.

    Returns dict: {pallet_code: {sku: {'name':..., 'qty': int, 'emb_grp':..., 'peso':..., 'atributo':..., 'ocupacao':...}}}
    """
    pallets = {}
    current = None
    header_re = re.compile(r'^(?P<pallet>\S+)\s+-\s+(?P<ocup>[0-9.,]+)')

    with path.open('r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            if not line:
                continue

            # detect pallet header
            m = header_re.match(line.strip())
            if m:
                current = m.group('pallet')
                pallets.setdefault(current, {})
                continue

            # product lines are inside pipes and contain a leading '0' token
            if '|' in line and ' 0 ' in line:
                # split and find the part that starts with 0
                parts = [p.strip() for p in line.split('|') if p.strip()]
                content = None
                for p in parts:
                    if p.startswith('0 '):
                        content = p
                        break
                if not content or current is None:
                    continue

                tokens = content.split()
                # safety: require a minimal token count
                if len(tokens) < 6:
                    continue

                try:
                    sku = tokens[1]
                    # qty is placed before emb/grp/peso/atr/ocu in the formatted output -> take 5th from the end
                    qty_token = tokens[-5]
                    qty = int(qty_token.replace(',', ''))
                except Exception:
                    # fallback: try to find first integer after sku
                    qty = None
                    for t in tokens[2:]:
                        if t.isdigit():
                            qty = int(t)
                            break
                name = ' '.join(tokens[2:-5]) if len(tokens) > 5 else ''
                emb_grp = tokens[-4] if len(tokens) >= 4 else ''
                peso = tokens[-3] if len(tokens) >= 3 else ''
                atributo = tokens[-2] if len(tokens) >= 2 else ''
                ocupacao = tokens[-1] if len(tokens) >= 1 else ''

                pallets[current].setdefault(sku, {})
                pallets[current][sku].update({'name': name, 'qty': qty or 0, 'emb_grp': emb_grp, 'peso': peso, 'atributo': atributo, 'ocupacao': ocupacao})

    return pallets


def build_comparison(left: dict, right: dict):
    """Combine two parsed pallet dicts into rows for comparison.

    Returns list of rows: dicts with keys: pallet, sku, name, qty_left, qty_right
    """
    rows = []
    pallet_codes = sorted(set(list(left.keys()) + list(right.keys())))
    for p in pallet_codes:
        left_skus = left.get(p, {})
        right_skus = right.get(p, {})
        sku_codes = sorted(set(list(left_skus.keys()) + list(right_skus.keys())), key=lambda x: (len(x), x))
        for sku in sku_codes:
            l = left_skus.get(sku, {})
            r = right_skus.get(sku, {})
            name = l.get('name') or r.get('name') or ''
            rows.append({
                'pallet': p,
                'sku': sku,
                'produto': name,
                'qty_left': l.get('qty', 0),
                'qty_right': r.get('qty', 0),
                'emb_grp_left': l.get('emb_grp', ''),
                'emb_grp_right': r.get('emb_grp', ''),
            })
    return rows


def write_csv(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Palete', 'SKU', 'Produto', 'Quantidade_Validacao', 'Quantidade_Result', 'Embalagem_Validacao', 'Embalagem_Result'])
        for r in rows:
            w.writerow([r['pallet'], r['sku'], r['produto'], r['qty_left'], r['qty_right'], r['emb_grp_left'], r['emb_grp_right']])


def main():
    parser = argparse.ArgumentParser(description='Compare two pallet TXT reports and produce a CSV comparison')
    parser.add_argument('valid_txt', help='Path to validation TXT (e.g., output.txt)')
    parser.add_argument('result_txt', help='Path to result TXT (e.g., palletize_result_map_*.txt)')
    parser.add_argument('--output', help='Output CSV path (defaults to compare_pallets.csv next to result)', default=None)
    args = parser.parse_args()

    valid_path = Path(args.valid_txt)
    result_path = Path(args.result_txt)
    if not valid_path.exists() or not result_path.exists():
        raise SystemExit('Input files not found')

    left = parse_pallet_file(valid_path)
    right = parse_pallet_file(result_path)
    rows = build_comparison(left, right)

    out = Path(args.output) if args.output else result_path.parent / 'compare_pallets.csv'
    write_csv(rows, out)
    print(f'Wrote comparison CSV to: {out}')


if __name__ == '__main__':
    main()
