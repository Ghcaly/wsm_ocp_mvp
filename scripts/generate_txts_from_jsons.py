#!/usr/bin/env python3
"""
Gera TXTs simples a partir dos JSONs em `wms_converter/out_jsons`.

Formato de saída (por mapa):
  Codigo;Quantidade

Arquivo salvo em: `mapas/out/processamento_massa/sucesso/{JsonName}.txt`
"""
from pathlib import Path
import json

REPO = Path(__file__).resolve().parent.parent
JSON_DIR = REPO / 'wms_converter' / 'out_jsons'
OUTPUT_DIR = REPO / 'mapas' / 'out' / 'processamento_massa' / 'sucesso'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def qty_from_item(item):
    q = 0
    if isinstance(item, dict):
        qty = item.get('Quantity') or item.get('Quantidade') or {}
        if isinstance(qty, dict):
            for key in ('Unit','unit','Sales','sales','Un','qtUn','qtUnVenda'):
                if key in qty and qty[key] is not None:
                    try:
                        return int(qty[key])
                    except Exception:
                        try:
                            return int(float(qty[key]))
                        except Exception:
                            continue
    return 0

def process_json(path: Path):
    try:
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return False, f'error reading json: {e}'

    number = data.get('Number') or data.get('MapNumber') or path.stem
    counter = {}

    for order in data.get('Orders', []):
        for item in order.get('Items', []):
            code = item.get('Code') or item.get('Codigo') or item.get('cdItem')
            if not code:
                continue
            q = qty_from_item(item)
            counter[code] = counter.get(code, 0) + q

    out_path = OUTPUT_DIR / f"{path.stem}.txt"
    with out_path.open('w', encoding='utf-8') as f:
        f.write(f"Mapa: {number}\n")
        f.write(f"Produtos únicos: {len(counter)}\n\n")
        f.write('Codigo;Quantidade\n')
        for code, qty in sorted(counter.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else x[0]):
            f.write(f"{code};{qty}\n")

    return True, out_path

def main():
    jsons = sorted(JSON_DIR.glob('*.json'))
    if not jsons:
        print('No JSONs found in', JSON_DIR)
        return

    succ = 0
    err = 0
    for j in jsons:
        ok, msg = process_json(j)
        if ok:
            succ += 1
        else:
            err += 1
            print('Error:', j.name, msg)

    print('Done. Generated', succ, 'txts, errors', err)
    print('Output dir:', OUTPUT_DIR)

if __name__ == '__main__':
    main()
