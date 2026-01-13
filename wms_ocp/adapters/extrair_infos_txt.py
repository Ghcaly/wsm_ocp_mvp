import re
import argparse
from pathlib import Path
from typing import List, Dict
import pandas as pd

COLUMN_KEYS = [
    "Pallet", "L", "Código", "UN", "Entrega", "Nome",
    "Qtd", "Embalagem", "Grp/Sub", "Peso", "Atributo", "Ocupação"
]

def _find_header_index(lines: List[str]) -> int:
    for i, l in enumerate(lines):
        if "Pallet" in l and "Ocupação" in l:
            return i
    raise ValueError("Header line not found")

def _compute_columns_positions(header_line: str, keys=COLUMN_KEYS) -> Dict[str,int]:
    starts = {}
    for key in keys:
        idx = header_line.find(key)
        if idx != -1:
            starts[key] = idx
    # ensure ascending order by position
    ordered = dict(sorted(starts.items(), key=lambda kv: kv[1]))
    return ordered

def _slice_by_positions(line: str, positions: Dict[str,int]) -> Dict[str,str]:
    keys = list(positions.keys())
    result = {}
    for i, k in enumerate(keys):
        start = positions[k]
        end = positions[keys[i+1]] if i+1 < len(keys) else None
        piece = line[start:end].rstrip() if end else line[start:].rstrip()
        result[k] = piece.strip()
    return result

def _try_float(s: str) -> float:
    if s is None:
        return 0.0
    s = s.strip().replace(".", "").replace(",", ".")  # handle "1.234,56" or "1234.56"
    try:
        return float(s)
    except Exception:
        # fallback extract digits
        m = re.search(r"[-+]?\d*[,\.]?\d+", s)
        return float(m.group(0).replace(",", ".")) if m else 0.0

def parse_output_txt_to_dataframe(txt_path: Path) -> pd.DataFrame:
    """Robust parser that extracts pallet code and product lines into a DataFrame.

    Returns DataFrame with columns:
      `pallet_code`, `product_code`, `product_name`, `quantity`, `atributo`
    """
    text = Path(txt_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    pallet_re = re.compile(r'^(?P<pallet>\S+)\s+-')
    prod_re = re.compile(
        r"^\s*\|\s*0\s+(?P<sku>\d+)\s+(?P<name>.*?)\s+(?P<qty>\d+)\s+.*?(?P<peso>[0-9.,]+)\s+(?P<atributo>[A-Za-zÀ-ÿ]+)\s+[0-9.,]+\s*$"
    )

    # locate header and column positions for reliable column slicing
    try:
        header_idx = _find_header_index(text)
        header_line = text[header_idx]
        positions = _compute_columns_positions(header_line)
    except Exception:
        header_idx = None
        positions = None

    rows = []
    current_pallet = None
    for line in text:
        if not line.strip():
            continue
        m = pallet_re.match(line)
        if m:
            current_pallet = m.group('pallet')
            continue

        # product lines contain '| 0'
        if '| 0' in line:
            # prefer column-slicing when header positions are known
            if positions:
                try:
                    parsed_cols = _slice_by_positions(line, positions)
                    # extract fields from parsed columns
                    codigo_col = parsed_cols.get('Código') or parsed_cols.get('Código UN') or ''
                    sku = codigo_col.strip().split()[0] if codigo_col else ''
                    name = (parsed_cols.get('Nome') or '').strip()
                    qty_raw = (parsed_cols.get('Qtd') or '').strip()
                    qty = None
                    if qty_raw:
                        # try integer then float
                        try:
                            qty = int(qty_raw.replace('.', '').replace(',', ''))
                        except Exception:
                            try:
                                qty = int(float(qty_raw.replace(',', '.')))
                            except Exception:
                                m = re.search(r'\d+', qty_raw)
                                qty = int(m.group(0)) if m else 0
                    atributo = (parsed_cols.get('Atributo') or '').strip()
                    rows.append({
                        'pallet_code': format_code_pallet(current_pallet),
                        'product_code': sku,
                        'product_name': name,
                        'quantity': qty or 0,
                        'atributo': atributo,
                    })
                    continue
                except Exception:
                    # fallthrough to regex/token parsing
                    pass

            # try strong regex first
            m2 = prod_re.search(line)
            if m2 and current_pallet:
                sku = m2.group('sku')
                name = re.sub(r"\s+", " ", m2.group('name')).strip()
                qty = int(m2.group('qty'))
                atributo = m2.group('atributo').strip()
                rows.append({
                    'pallet_code': format_code_pallet(current_pallet),
                    'product_code': sku,
                    'product_name': name,
                    'quantity': qty,
                    'atributo': atributo,
                })
                continue

            # fallback parsing using tokenization
            parts = [p.strip() for p in line.split('|') if p.strip()]
            content = None
            for p in parts:
                if p.startswith('0 '):
                    content = p
                    break
            if not content or not current_pallet:
                continue
            tokens = content.split()
            if len(tokens) < 4:
                continue
            sku = tokens[1]
            # attempt to find qty as first integer after name start (tokens[2:])
            qty = None
            atributo = ''
            for t in tokens[2:]:
                if t.isdigit():
                    qty = int(t)
                    break

            name = ' '.join(tokens[2:])
            if qty is not None:
                name_parts = []
                for t in tokens[2:]:
                    if t == str(qty):
                        break
                    name_parts.append(t)
                name = ' '.join(name_parts)

            rows.append({
                'pallet_code': format_code_pallet(current_pallet),
                'product_code': sku,
                'product_name': name,
                'quantity': qty or 0,
                'atributo': atributo,
            })

    df = pd.DataFrame(rows, columns=['pallet_code', 'product_code', 'product_name', 'quantity', 'atributo'])
    return df

def format_code_pallet(s):
    partes = s.split('_')

    if re.match(r"P\d+_", s):
        return s
    
    numero = partes[2]
    partes[0] = f"{partes[0]}{numero}"
    return "_".join(partes)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse route output TXT and save as XLSX')
    parser.add_argument('validacao', nargs='?', default=r"c:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\route\620768\output.txt", help='Path to output TXT')
    parser.add_argument('input', nargs='?', default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\route\620768\output\palletize_result_map_620768.txt", help='Path to output TXT')
    parser.add_argument('--output', '-o', default=None, help='Output XLSX path (optional)')
    args = parser.parse_args()

    validacao_path = Path(args.validacao)
    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    #validacao
    df = parse_output_txt_to_dataframe(validacao_path)
    out_path = Path(args.output) if args.output else validacao_path.parent / 'validacao_620768.xlsx'
    try:
        df.to_excel(out_path, index=False)
        print(f'Wrote XLSX: {out_path}')
    except Exception as e:
        # fallback to CSV if openpyxl not available
        csv_path = out_path.with_suffix('.csv')
        df.to_csv(csv_path, index=False)
        print(f'Failed to write XLSX ({e}). Wrote CSV: {csv_path}')

    #validacao
    df = parse_output_txt_to_dataframe(in_path)
    out_path = Path(args.output) if args.output else in_path.parent / 'result_620768.xlsx'
    try:
        df.to_excel(out_path, index=False)
        print(f'Wrote XLSX: {out_path}')
    except Exception as e:
        # fallback to CSV if openpyxl not available
        csv_path = out_path.with_suffix('.csv')
        df.to_csv(csv_path, index=False)
        print(f'Failed to write XLSX ({e}). Wrote CSV: {csv_path}')