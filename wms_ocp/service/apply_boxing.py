#!/usr/bin/env python3
"""
Helper script para aplicar boxing via API.
Transforma o inputcompleto.json no formato esperado pela API de boxing.
"""

import json
import sys
import requests
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os 
import math
import numpy as np

load_dotenv()
HOST_ITEMS_BOXSING = os.getenv('HOST_ITEMS_BOXSING', 'http://localhost:8001/api/items-boxing/v1/calculate/')

def sanitize_for_json(obj):
    if obj is None:
        return None

    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]

    return obj
    
def buscar_item(df, sku_code, UnbCode=None):
    """Busca o item no DataFrame pelo código."""

    code = str(sku_code)
    row_data = df.loc[code] 

    if isinstance(row_data, pd.DataFrame):
        if UnbCode is not None:
            result = row_data[(row_data['Código Unb'] == UnbCode) | (row_data['Código Unb'] == str(UnbCode))]
            if result is not None and len(result) > 0:
                return result.iloc[0]
            
        if len(row_data) > 1:
            row_data = row_data[(row_data['Código Unb'] == 'None') | (row_data['Código Unb'] == 'nan')]
            return row_data.iloc[0]
        elif len(row_data) == 1:
            return row_data.iloc[0]
        else:
            return row_data.iloc[0]

    return row_data

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


def transform_to_boxing_format_2(orders, df):
    """Transforma inputcompleto.json para formato da API de boxing."""
    marketplace_items = {}
    total_items = 0
    marketplace_matched = 0

    if not orders:
        print("DEBUG: Nenhum pedido encontrado no input", file=sys.stderr)
        return None
 
    for order in orders:
        # client_code = order.get('Client', {}).get('Code', '0')
        client_code = "0"
        for item in order.Items:
            total_items += 1
            sku_code = str(item.Code)
            total_qty = item.Amount
            client_code = item.Customer

            is_marketplace = False

            if item and item.Product and item.Product.ItemMarketplace is not None and (item.Product.ItemMarketplace.box_type is not None or item.Product.ItemMarketplace.units_per_box >0):
                is_marketplace = True

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
            row = buscar_item(df, sku_code)
            val = row.get("Quantidade de unidades por caixa")

            if val is None or pd.isna(val) or str(val).strip().lower() == "nan":
                units = 0
            else:
                units = int(val)
                
            skus_list.append({
                "code": int(sku_code),
                "length": row.get("Comprimento do item", None),
                "height": row.get("Altura do item", None),
                "width": row.get("Largura do item", None),
                "units_in_boxes": units,
                "is_bottle": row.get("Tipo Caixa", None)=='Garrafeira',
                "gross_weight": row.get("Peso bruto do item", None)
            })
        except (ValueError, TypeError):
            continue

    base_dir = Path(__file__).parent.parent / 'database'
    df = pd.read_csv(base_dir / "boxes_completo_merge.csv")
    df = df.where(pd.notnull(df), None).astype(object)
    df_boxs = df[(df.WarehouseId=='401') | (df.WarehouseId==401)]
    boxes=[]
    for idx, row in df_boxs.iterrows():
        boxes.append({
            "code": int(row["ItemCode"]),
            "length": float(row["Length"]),
            "width": float(row["Width"]),
            "height": float(row["Height"]),
            "box_slots": int(row["HiveQuantity"]),
            "box_slot_diameter": float(row["HiveDiameter"])
        })

    return sanitize_for_json({
        "maps": [{"code": 1, "clients": clients}],
        "skus": skus_list,
        "boxes": boxes
    })

def apply_boxing_2(order, df):
    """Aplica boxing e retorna resultado."""
    try:
        boxing_input = transform_to_boxing_format_2(order, df)

        if not boxing_input:
            print(json.dumps({"success": False, "error": "No marketplace items", "marketplace_count": 0}))
            return 1

        total_mktp_items = sum(len(c.get('skus', [])) for m in boxing_input.get('maps', []) for c in m.get('clients', []))
        print(f"DEBUG: {total_mktp_items} produtos marketplace detectados", file=sys.stderr)

        response = requests.post(
            HOST_ITEMS_BOXSING,
            json=boxing_input,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(json.dumps({"success": True, "result": result})) 
            return result

        else:
            print(json.dumps({"success": False, "error": response.text})) 
            return {"success": False, "error": response.text}

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        return 1
    
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
            HOST_ITEMS_BOXSING,
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
