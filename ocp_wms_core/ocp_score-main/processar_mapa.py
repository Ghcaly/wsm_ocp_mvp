#!/usr/bin/env python3
"""
Wrapper para processar um mapa específico
"""
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Uso: python3 processar_mapa.py <numero_mapa>")
    sys.exit(1)

mapa_num = sys.argv[1]

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from service.palletizing_processor import PalletizingProcessor

# Criar processor
processor = PalletizingProcessor(debug_enabled=False)

# Definir paths
base_dir = Path(__file__).parent / f'data/route/{mapa_num}'
config_file = base_dir / 'config.json'
data_file = base_dir / 'input.json'
output_dir = base_dir / 'output'

# Verificar arquivos
if not config_file.exists():
    print(f"❌ Config não encontrado: {config_file}")
    sys.exit(1)

if not data_file.exists():
    print(f"❌ Input não encontrado: {data_file}")
    sys.exit(1)

# Processar
print(f"Processando mapa {mapa_num}...")
result = processor.run_complete_palletizing_process(
    config_file=str(config_file),
    data_file=str(data_file),
    output_dir=str(output_dir),
    validation_file=str(output_dir / 'output.json')
)

if result['success']:
    print(f"✅ Sucesso! Mapa {mapa_num}")
    sys.exit(0)
else:
    print(f"❌ Erro: {result.get('error', 'Desconhecido')}")
    sys.exit(1)
