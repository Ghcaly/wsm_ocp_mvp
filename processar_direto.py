#!/usr/bin/env python3
"""
PROCESSAMENTO DIRETO - Sem APIs
XML → JSON → Produtos → Regras → TXT
"""

import sys
from pathlib import Path

# Adiciona paths necessários
sys.path.insert(0, str(Path(__file__).parent / "wms_converter" / "modules"))
sys.path.insert(0, str(Path(__file__).parent / "ocp_wms_core" / "ocp_score-main"))

import json
import pandas as pd
from datetime import datetime

# Imports
from converter import XmlConverter
from service.calculator_palletizing_service import CalculatorPalletizingService
from domain.context import Context
from adapters.database import enrich_items

print("=" * 80)
print("🚀 PROCESSAMENTO DIRETO - XML → REGRAS → TXT")
print("=" * 80)
print()

# XML de entrada
xml_file = "/home/wms_core/wms_xml_in/023c4f1b660f49cf86900cc0022df5d1_m_mapa_448111_0970_20260105234547.xml"

# ===== PASSO 1: XML → JSON =====
print("[1/5] Convertendo XML...")
converter = XmlConverter()
json_data = converter.convert(xml_file, None)

# Corrigir Type
if isinstance(json_data.get('Type'), int):
    json_data['Type'] = {1: 'route', 2: 'as', 3: 'mixed', 4: 'crossdocking'}.get(json_data['Type'], 'route')

print(f"   ✓ {len(json_data.get('Orders', []))} pedidos convertidos")

# ===== PASSO 2: Criar Context =====
print("[2/5] Carregando dados...")
context = Context()
context.load_json_input(json_data)
print(f"   ✓ {len(context.Orders)} pedidos, {len(context.Spaces)} espaços")

# ===== PASSO 3: Carregar produtos =====
print("[3/5] Carregando catálogo...")
product_db = Path(__file__).parent / "ocp_wms_core" / "ocp_score-main" / "database" / "product_master.csv"

try:
    df = pd.read_csv(product_db, index_col='ItemCode', dtype={'ItemCode': str}, on_bad_lines='skip')
    print(f"   ✓ {len(df)} produtos carregados")
    
    total_items = 0
    for order in context.Orders:
        enrich_items(order.Items, {}, "", df)
        total_items += len(order.Items)
    print(f"   ✓ {total_items} items enriquecidos")
except Exception as e:
    print(f"   ⚠ Catálogo não carregado: {e}")

# ===== PASSO 4: Executar regras =====
print("[4/5] Executando regras de paletização...")
service = CalculatorPalletizingService()
context_type = json_data.get('Type', 'route').lower()

if context_type in ['route', 'mixed']:
    print("   → principal_route_chain")
    context = service.execute_chain(service.principal_route_chain, context)
    print("   → route_chain")
    context = service.execute_chain(service.route_chain, context)

if context_type in ['as', 'mixed']:
    print("   → as_chain")
    context = service.execute_chain(service.as_chain, context)

print("   → common_chain")
context = service.execute_chain(service.common_chain, context)

mounted = len(context.MountedSpaces) if hasattr(context, 'MountedSpaces') else 0
print(f"   ✓ {mounted} mounted spaces criados")

# ===== PASSO 5: Gerar TXT =====
print("[5/5] Gerando relatório...")
output = Path("/tmp/RESULTADO_PALETIZACAO.txt")

with open(output, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("RELATÓRIO DE PALETIZAÇÃO\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Tipo: {context_type}\n")
    f.write(f"Mapa: {json_data.get('Number', 'N/A')}\n")
    f.write(f"Veículo: {json_data.get('Vehicle', {}).get('Plate', 'N/A')}\n\n")
    f.write(f"📦 Mounted Spaces: {mounted}\n")
    f.write(f"📋 Pedidos: {len(context.Orders)}\n")
    f.write(f"🚛 Bays: {len(context.Spaces)}\n\n")
    
    if mounted > 0:
        f.write("=" * 80 + "\n")
        f.write("MOUNTED SPACES\n")
        f.write("=" * 80 + "\n\n")
        
        for idx, ms in enumerate(context.MountedSpaces[:50], 1):
            space_id = ms.space.id if hasattr(ms, 'space') else 'N/A'
            f.write(f"[{idx}] Space: {space_id}\n")
            
            if hasattr(ms, 'GetProducts'):
                products = ms.GetProducts()
                f.write(f"    Produtos: {len(products)}\n")
                for p in products[:10]:
                    code = getattr(p, 'Code', 'N/A')
                    qty = getattr(p, 'Amount', 'N/A')
                    f.write(f"      • {code}: {qty} un\n")
            f.write("\n")

print(f"   ✓ Salvo: {output}")
print()
print("=" * 80)
print("✅ CONCLUÍDO!")
print("=" * 80)
print(f"\nArquivo: {output}")
