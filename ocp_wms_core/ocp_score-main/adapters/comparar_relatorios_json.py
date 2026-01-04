"""
Comparator that mirrors comparar_relatorios.py but reads JSON outputs
instead of TXT. Produces the same Excel layout (Comparação, Por Tipo, Consolidado).

Usage:
    from ocp_score_ia.adapters.comparar_relatorios_json import CompararRelatoriosJSON
    CompararRelatoriosJSON.compare(wms_json_path, api_json_path, output_excel_path)

This is a focused port: it extracts products from the JSON structure produced by
the palletizer (`Pallets` -> `Items`) and then reuses the same formatting
helpers from `comparar_relatorios.py` (formatar_excel).
"""
from pathlib import Path
import json
from typing import List, Dict, Any
import pandas as pd

# reuse formatting from existing module
from .comparar_relatorios import formatar_excel, _MAPEAMENTO_ARQUIVOS


def _extract_products_from_json(json_path: Path) -> List[Dict[str, Any]]:
    """Extract a flat list of products from the palletize JSON.

    Returns records compatible with the original TXT extractor:
    { number_mapa, pallet_code, product_code, product_name, quantity, atributo, ocupacao }
    """
    data = json.loads(Path(json_path).read_text(encoding='utf-8'))
    produtos = []

    # try several places for map number
    number_mapa = None
    for key in ('DocumentNumber', 'DocumentNumber', 'map_number', 'MapNumber'):
        if isinstance(data.get(key), (str, int)) and data.get(key):
            number_mapa = str(data.get(key))
            break
    # fallback: try filename
    if not number_mapa:
        import re
        m = re.search(r'map[_-]?(\d+)', json_path.name)
        if m:
            number_mapa = m.group(1)

    pallets = data.get('Pallets') or data.get('pallets') or []
    for p in pallets:
        pallet_code = p.get('Code') or p.get('code') or ''
        # if pallet has Items
        for item in p.get('Items', []) or []:
            prod_code = item.get('Code') or item.get('code') or ''
            prod_name = item.get('Description') or item.get('description') or ''
            qty = item.get('Quantity') or item.get('quantity') or 0
            # atributo: try common fields; keep empty string if unknown
            atributo = item.get('Atributo') or item.get('atributo') or item.get('Marketplace') or item.get('MarketPlace') or ''
            ocup = item.get('Occupation') or item.get('ocupacao') or item.get('OccupationPercent') or 0

            try:
                qv = float(qty)
            except Exception:
                try:
                    qv = float(str(qty).replace(',', '.'))
                except Exception:
                    qv = 0.0

            try:
                ov = float(ocup)
            except Exception:
                try:
                    ov = float(str(ocup).replace(',', '.'))
                except Exception:
                    ov = 0.0

            produtos.append({
                'number_mapa': number_mapa,
                'pallet_code': pallet_code,
                'product_code': str(prod_code),
                'product_name': prod_name,
                'quantity': qv,
                'atributo': atributo or '',
                'ocupacao': ov,
            })

    return produtos


class CompararRelatoriosJSON:
    """Produces the same comparison Excel as comparar_relatorios.py but
    consuming JSON files (palletize_result_map_*.json and output.json).
    """

    @staticmethod
    def compare(wms_json: str, api_json: str, output_excel: str, append: bool = False):
        wms_path = Path(wms_json)
        api_path = Path(api_json)
        out_path = Path(output_excel)

        print(f"[JSON-COMP] Lendo WMS JSON: {wms_path}")
        produtos_wms = _extract_products_from_json(wms_path)
        print(f"[JSON-COMP] Lendo API JSON: {api_path}")
        produtos_api = _extract_products_from_json(api_path)

        print(f"[JSON-COMP] Produtos WMS: {len(produtos_wms)} | Produtos API: {len(produtos_api)}")

        # normalize number_mapa and register mapping like the TXT comparator
        number_mapa = None
        if produtos_api and produtos_api[0].get('number_mapa'):
            number_mapa = produtos_api[0]['number_mapa']
        elif produtos_wms and produtos_wms[0].get('number_mapa'):
            number_mapa = produtos_wms[0]['number_mapa']
        if not number_mapa:
            import re
            m = re.search(r'map[_-]?(\d+)', api_path.name)
            if m:
                number_mapa = m.group(1)

        if number_mapa:
            for p in produtos_wms:
                p['number_mapa'] = number_mapa
            for p in produtos_api:
                p['number_mapa'] = number_mapa

        # Create DataFrames similar to comparar_relatorios.criar_excel_comparacao
        df_wms_new = pd.DataFrame(produtos_wms)
        df_api_new = pd.DataFrame(produtos_api)

        # ensure expected columns
        colunas = ['number_mapa', 'pallet_code', 'product_code', 'product_name', 'quantity', 'atributo', 'ocupacao']
        for df in (df_wms_new, df_api_new):
            for c in colunas:
                if c not in df.columns:
                    df[c] = ''
        df_wms = df_wms_new[colunas]
        df_api = df_api_new[colunas]

        # horizontal concat: WMS + separator + API
        max_linhas = max(len(df_wms), len(df_api))
        if len(df_wms) < max_linhas:
            df_wms = pd.concat([df_wms, pd.DataFrame('', index=range(max_linhas - len(df_wms)), columns=df_wms.columns)], ignore_index=True)
        if len(df_api) < max_linhas:
            df_api = pd.concat([df_api, pd.DataFrame('', index=range(max_linhas - len(df_api)), columns=df_api.columns)], ignore_index=True)

        df_separador = pd.DataFrame({'': [''] * max_linhas})
        df_final = pd.concat([df_wms, df_separador, df_api], axis=1, ignore_index=False)
        df_final = df_final.fillna('')

        # register mapping for batch summary lookup used by formatar functions
        if number_mapa:
            try:
                _MAPEAMENTO_ARQUIVOS[str(number_mapa)] = (str(wms_path), str(api_path))
            except Exception:
                pass

        # write to excel same way as original
        with pd.ExcelWriter(out_path, engine='openpyxl', mode='w') as writer:
            df_final.to_excel(writer, sheet_name='Comparação', index=False, startrow=11)

        # call the same formatter to create additional sheets
        try:
            formatar_excel(out_path, atributos_wms=sorted(df_wms['atributo'].unique().tolist()),
                           atributos_api=sorted(df_api['atributo'].unique().tolist()),
                           pallets_wms=df_wms[df_wms['pallet_code'] != '']['pallet_code'].drop_duplicates().tolist(),
                           pallets_api=df_api[df_api['pallet_code'] != '']['pallet_code'].drop_duplicates().tolist(),
                           is_append=append, wms_file=wms_path, api_file=api_path, criar_aba_nao_paletizados_flag=True)
        except Exception as e:
            print(f"[JSON-COMP] erro ao formatar excel: {e}")

        print(f"[JSON-COMP] Relatório gerado: {out_path}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print('Usage: comparar_relatorios_json.py <wms_json> <api_json> <output.xlsx>')
    else:
        CompararRelatoriosJSON.compare(sys.argv[1], sys.argv[2], sys.argv[3])