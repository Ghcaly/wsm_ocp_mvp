#!/usr/bin/env python3
"""
Detecta produtos marketplace e aplica Boxing (BinPack) quando necessário
Integra no fluxo de processamento em massa
"""
import sys
import json
import requests
from pathlib import Path

# Add ocp_wms_core to path
sys.path.insert(0, str(Path(__file__).parent / 'ocp_wms_core' / 'ocp_score-main'))

from service.marketplace_detector import get_detector
from service.boxing_integrator import get_integrator


def detect_and_process_marketplace(input_json_path: str) -> dict:
    """
    Detecta marketplace no input JSON e aplica boxing se necessário
    
    Args:
        input_json_path: Caminho do arquivo input.json
        
    Returns:
        Dict com:
        - has_marketplace: bool
        - marketplace_count: int
        - boxing_result: dict ou None
        - boxing_applied: bool
    """
    result = {
        'has_marketplace': False,
        'marketplace_count': 0,
        'boxing_result': None,
        'boxing_applied': False,
        'error': None
    }
    
    try:
        # Carrega input JSON
        with open(input_json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Detecta marketplace
        detector = get_detector()
        analysis = detector.analyze_input(json_data)
        
        result['has_marketplace'] = analysis['has_marketplace']
        result['marketplace_count'] = analysis['marketplace_count']
        
        # Se não tem marketplace, retorna
        if not analysis['has_marketplace']:
            return result
        
        print(f"✓ Marketplace detectado: {analysis['marketplace_count']} produtos", file=sys.stderr)
        
        # Extrai itens marketplace
        marketplace_items = []
        
        # Tenta extrair de Orders (estrutura route)
        if 'Orders' in json_data:
            for order in json_data.get('Orders', []):
                for item in order.get('Items', []):
                    code = str(item.get('Code', ''))
                    if detector.is_marketplace(code):
                        marketplace_items.append(item)
        
        # Tenta extrair de Items direto
        elif 'Items' in json_data:
            for item in json_data.get('Items', []):
                code = str(item.get('Code', ''))
                if detector.is_marketplace(code):
                    marketplace_items.append(item)
        
        if not marketplace_items:
            print("✗ Produtos marketplace detectados mas não encontrados no JSON", file=sys.stderr)
            return result
        
        # Aplica boxing
        print(f"→ Chamando Boxing API para {len(marketplace_items)} itens...", file=sys.stderr)
        integrator = get_integrator()
        
        boxing_result = integrator.process_boxing(marketplace_items)
        
        if boxing_result:
            result['boxing_result'] = boxing_result
            result['boxing_applied'] = True
            print(f"✓ Boxing aplicado com sucesso", file=sys.stderr)
            
            # Log detalhes
            if 'pacotes' in boxing_result:
                print(f"  - Pacotes: {len(boxing_result.get('pacotes', {}))}", file=sys.stderr)
            if 'caixas' in boxing_result:
                print(f"  - Caixas: {len(boxing_result.get('caixas', {}))}", file=sys.stderr)
        else:
            print("✗ Boxing API falhou", file=sys.stderr)
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        print(f"✗ Erro: {e}", file=sys.stderr)
        return result


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(json.dumps({'error': 'Usage: detect_and_box.py <input.json>'}))
        sys.exit(1)
    
    input_json = sys.argv[1]
    result = detect_and_process_marketplace(input_json)
    
    # Output JSON para stdout
    print(json.dumps(result, ensure_ascii=False))
    
    # Exit code: 0 se OK, 1 se erro
    sys.exit(0 if result['error'] is None else 1)
