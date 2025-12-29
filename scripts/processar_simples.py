#!/usr/bin/env python3
"""
Processador simples que não depende de venv quebrado
"""
import sys
import os
import json
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, '/mnt/c/prd_debian/ocp_wms_core/ocp_score-main')

def processar_xml(xml_path):
    """Processa um XML completo: converte e paletiza"""
    
    print(f"\n{'='*80}")
    print(f"PROCESSANDO: {Path(xml_path).name}")
    print('='*80)
    
    # 1. Converter XML -> JSON
    print("\n[1/3] Convertendo XML para JSON...")
    import subprocess
    result = subprocess.run(
        ['python3', '/mnt/c/prd_debian/wms_converter/convert.py', 
         '-i', xml_path, 
         '-o', '/mnt/c/prd_debian/mapas/in/input.json'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Erro na conversão: {result.stderr}")
        return False
    
    print("✓ Conversão OK")
    
    # 2. Criar config mínimo
    print("\n[2/3] Preparando configuração...")
    config_path = '/mnt/c/prd_debian/mapas/in/config.json'
    
    # Ler input para pegar warehouse
    with open('/mnt/c/prd_debian/mapas/in/input.json', 'r') as f:
        input_data = json.load(f)
    
    warehouse = input_data.get('Warehouse', {}).get('UnbCode', '916')
    mapa_num = input_data.get('Number', 'unknown')
    
    config = {
        "warehouse": warehouse,
        "delivery_date": "2025-12-23"
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    print(f"✓ Config criado (Warehouse: {warehouse}, Mapa: {mapa_num})")
    
    # 3. Paletizar
    print("\n[3/3] Executando paletização...")
    
    try:
        # Import aqui para capturar erros
        from service.palletizing_processor import PalletizingProcessor
        
        processor = PalletizingProcessor(debug_enabled=False)
        
        # Criar diretório de trabalho
        work_dir = f'/mnt/c/prd_debian/ocp_wms_core/ocp_score-main/data/route/{mapa_num}'
        os.makedirs(work_dir, exist_ok=True)
        
        # Copiar arquivos
        import shutil
        shutil.copy('/mnt/c/prd_debian/mapas/in/config.json', f'{work_dir}/config.json')
        shutil.copy('/mnt/c/prd_debian/mapas/in/input.json', f'{work_dir}/input.json')
        
        # Processar
        context = processor.load_configuration_and_data(
            f'{work_dir}/config.json',
            f'{work_dir}/input.json'
        )
        
        result = processor.palletize(context)
        
        # Verificar output
        output_files = list(Path(work_dir).glob('output/*.txt'))
        
        if output_files:
            txt_path = output_files[0]
            # Copiar para pasta de sucesso
            success_dir = '/mnt/c/prd_debian/mapas/out/processamento_massa/sucesso'
            os.makedirs(success_dir, exist_ok=True)
            
            output_name = Path(xml_path).stem + '.txt'
            shutil.copy(txt_path, f'{success_dir}/{output_name}')
            
            print(f"✓ TXT gerado: {output_name}")
            return True
        else:
            print("❌ TXT não foi gerado")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("\nDependências faltando. Instale com:")
        print("  cd /mnt/c/prd_debian/ocp_wms_core")
        print("  python3 -m pip install pandas --user")
        return False
    except Exception as e:
        print(f"❌ Erro na paletização: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 processar_simples.py <arquivo.xml>")
        sys.exit(1)
    
    xml_path = sys.argv[1]
    
    if not os.path.exists(xml_path):
        print(f"❌ Arquivo não encontrado: {xml_path}")
        sys.exit(1)
    
    sucesso = processar_xml(xml_path)
    sys.exit(0 if sucesso else 1)
