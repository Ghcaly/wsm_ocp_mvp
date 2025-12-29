#!/usr/bin/env python3
"""
Helper script para aplicar boxing via API.
Transforma o inputcompleto.json no formato esperado pela API de boxing.
"""

import json
import sys
import requests
from pathlib import Path


def load_marketplace_skus():
    """Carrega lista de SKUs marketplace."""
    candidates = [
        Path("/mnt/c/prd_debian/data 2(Export).csv"),  # path correto no WSL
        Path("/home/prd_debian/data 2(Export).csv"),   # fallback antigo
    ]

    marketplace_skus = set()

    for csv_file in candidates:
        if not csv_file.exists():
            continue

        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(csv_file, 'r', encoding=encoding, newline='') as f:
                    next(f, None)  # header
                    for line in f:
                        parts = line.strip().replace('\r', '').split(',')
                        # Formato: Cod_Produto,Desc_Embalagem,...,Cluster_Premium
                        if len(parts) >= 6 and parts[-1].strip() == 'MKTP':
                            sku = parts[0].strip()
                            marketplace_skus.add(sku)
                            try:
                                marketplace_skus.add(str(int(sku)))  # normaliza
                            except ValueError:
                                pass
                break
            except UnicodeDecodeError:
                continue

        if marketplace_skus:
            break

    print(f"DEBUG: Carregados {len(marketplace_skus)} SKUs marketplace", file=sys.stderr)
    return marketplace_skus


def transform_to_boxing_format(input_data, marketplace_skus):
    """Transforma inputcompleto.json para formato da API de boxing."""
    marketplace_items = {}
    total_items = 0
    marketplace_matched = 0

    orders = input_data.get('Orders', [])
    if not orders:
        print("DEBUG: Nenhum pedido encontrado no input", file=sys.stderr)
        return None

    for order in orders:
        client_code = order.get('Client', {}).get('Code', '0')
        items = order.get('Items', [])

        for item in items:
            total_items += 1
            sku_code = str(item.get('Code', ''))
            quantity = item.get('Quantity', {})

            sales = quantity.get('Sales', 0)
            unit = quantity.get('Unit', 0)
            detached = quantity.get('Detached', 0)
            total_qty = (sales * unit) + detached if sales > 0 else unit + detached

            is_marketplace = (
                sku_code in marketplace_skus
                or (sku_code.isdigit() and str(int(sku_code)) in marketplace_skus)
            )

            if is_marketplace and total_qty > 0:
                marketplace_matched += 1
                if client_code not in marketplace_items:
                    marketplace_items[client_code] = {}
                marketplace_items[client_code][sku_code] = marketplace_items[client_code].get(sku_code, 0) + total_qty

    print(f"DEBUG: Total itens: {total_items}, Marketplace: {marketplace_matched}", file=sys.stderr)

    if not marketplace_items:
        print("DEBUG: Nenhum produto marketplace identificado no input", file=sys.stderr)
        return None

    clients = []
    for client_code, items in marketplace_items.items():
        client_skus = []
        for sku, qty in items.items():
            try:
                client_skus.append({"code": int(sku), "quantity": int(qty)})
            except (ValueError, TypeError):
                continue

        if client_skus:
            try:
                clients.append({"code": int(client_code), "skus": client_skus})
            except (ValueError, TypeError):
                continue

    skus_list = []
    unique_skus = set(sku for items in marketplace_items.values() for sku in items.keys())
    for sku_code in unique_skus:
        try:
            skus_list.append({
                "code": int(sku_code),
                "length": 10.0,
                "height": 25.0,
                "width": 10.0,
                "units_in_boxes": 12,
                "is_bottle": True,
                "gross_weight": 1.5
            })
        except (ValueError, TypeError):
            continue

    boxes = [
        {
            "code": 1,
            "length": 0,
            "width": 0,
            "height": 0,
            "box_slots": 9,
            "box_slot_diameter": 10.392304
        },
        {
            "code": 2,
            "length": 40,
            "width": 58,
            "height": 34,
            "box_slots": 0,
            "box_slot_diameter": 0
        }
    ]

    return {
        "maps": [{"code": 1, "clients": clients}],
        "skus": skus_list,
        "boxes": boxes
    }


def apply_boxing(input_file):
    """Aplica boxing e retorna resultado."""
    try:
        with open(input_file, 'r') as f:
            input_data = json.load(f)

        marketplace_skus = load_marketplace_skus()
        boxing_input = transform_to_boxing_format(input_data, marketplace_skus)

        if not boxing_input:
            print(json.dumps({"success": False, "error": "No marketplace items", "marketplace_count": 0}))
            return 1

        total_mktp_items = sum(len(c.get('skus', [])) for m in boxing_input.get('maps', []) for c in m.get('clients', []))
        print(f"DEBUG: {total_mktp_items} produtos marketplace detectados", file=sys.stderr)

        response = requests.post(
            "http://localhost:8001/api/items-boxing/v1/calculate/",
            json=boxing_input,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(json.dumps({"success": True, "result": result}))
            return 0
        else:
            print(json.dumps({"success": False, "error": response.text}))
            return 1

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"success": False, "error": "Usage: apply_boxing.py <input_file>"}))
        sys.exit(1)

    sys.exit(apply_boxing(sys.argv[1]))
