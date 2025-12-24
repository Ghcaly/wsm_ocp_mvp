import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any

# reuse report building utilities from check.py to produce identical .md/.html output
from ..service.check import (
    build_table,
    save_markdown,
    save_html,
    load_json,
    count_input_items,
)


def _load_xml(path: Path) -> ET.Element:
    tree = ET.parse(path)
    return tree.getroot()


def _parse_xml_pallets(root: ET.Element) -> List[Dict[str, Any]]:
    pallets = []
    for p in root.findall('.//pallet'):
        lado = (p.findtext('cdLado') or '').strip()
        nr = p.findtext('nrBaiaGaveta') or p.findtext('nrBaia') or ''
        entrega = p.findtext('entregaSegregada') or ''
        itens_node = p.find('itens')
        items = []
        if itens_node is not None:
            for it in itens_node.findall('item'):
                qty_text = it.findtext('qtUnVenda') or it.findtext('qtUnVenda') or '0'
                try:
                    qty = int(qty_text)
                except Exception:
                    try:
                        qty = int(float(qty_text))
                    except Exception:
                        qty = 0
                code = it.findtext('cdItem') or it.findtext('cd_item') or it.findtext('codigo') or ''
                items.append({'code': code, 'quantity': qty})

        pallets.append({'side': lado, 'number': nr, 'entrega': entrega, 'items': items})
    return pallets


def _xml_to_pallet_dicts(xml_pallets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for xp in xml_pallets:
        num = xp.get('number') or ''
        side = xp.get('side') or ''
        # create a synthetic code that follows the map-like naming so reports group by code
        try:
            num_int = int(num)
            code = f"P{num_int:02d}_{side}_XML"
        except Exception:
            code = f"XML_{side}_{num}"

        items = []
        for it in xp.get('items', []) or []:
            # keep keys compatible with check.aggregate_items_list (accepts 'code' or 'Code')
            items.append({'code': it.get('code') or it.get('cdItem') or it.get('cd_item') or '', 'quantity': int(it.get('quantity') or it.get('qty') or it.get('Quantity') or 0)})

        out.append({'code': code, 'items': items, 'occupation': None, 'weight': None, 'isClosed': False})
    return out


def run_reports_xml(xml_path: str, map_json_path: str, input_path: str = None, out_dir: str = 'reports') -> int:
    xml_p = Path(xml_path)
    map_p = Path(map_json_path)
    outdir_p = Path(out_dir)

    if not xml_p.exists():
        print(f"XML file not found: {xml_path}")
        return 2
    if not map_p.exists():
        print(f"Map JSON file not found: {map_json_path}")
        return 2

    root = _load_xml(xml_p)
    xml_pallets = _parse_xml_pallets(root)
    out_pallets = _xml_to_pallet_dicts(xml_pallets)

    # load the map JSON (reference)
    map_data = load_json(map_p)
    map_pallets = map_data.get('pallets') or map_data.get('Pallets') or []

    rows, overall = build_table(map_pallets, out_pallets)

    # augment overall with input counts if provided
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

    # also print concise metrics like check.py
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

        print("\n=== Métricas Resumidas (XML vs Map) ===")
        print(f"Similaridade média: {avg_sim:.2f}%")
        print(f"Paletes correspondentes: {matched_pallets} / {total_pallets_map} ({pct_matched_pallets:.2f}%)")
        print(f"Itens correspondentes (quantidade): {matched_items} / {total_map} (map) | saída(XML): {total_out}")
        print(f"Itens palletizados (map/out): {palletized_map} / {palletized_out}")
        print(f"Itens não-palletizados (map/out): {nonp_map} / {nonp_out}")
        print(f"Itens distintos (map/out): {distinct_map} / {distinct_out}")
        print("========================\n")
    except Exception as e:
        print(f"Erro ao imprimir métricas: {e}")

    return 0


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate the same check report but comparing XML response to a map JSON')
    parser.add_argument('--xml', required=True, help='Path to XML response file (xmlresposta_*.txt)')
    parser.add_argument('--json', required=True, help='Path to generated palletize_result_map_*.json (map reference)')
    parser.add_argument('--input', required=False, help='Optional input JSON to compute input totals')
    parser.add_argument('--out-dir', required=False, default='reports', help='Output directory for reports')
    args = parser.parse_args()

    exit(run(args.xml, args.json, args.input, args.out_dir))
