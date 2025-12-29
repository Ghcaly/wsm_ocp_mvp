#!/usr/bin/env python3
"""
Run Palletization - Executa paletização recebendo JSON

Uso:
    python run_palletization.py input.json
    python run_palletization.py config.json data.json
"""

import sys
import json
import logging
from pathlib import Path
from typing import Optional

from service.calculator_palletizing_service import CalculatorPalletizingService
from domain.context import Context


def setup_logging():
    """Configura logging básico"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)


def detect_context_type(json_path: Path) -> str:
    """
    Detecta o tipo de contexto baseado no JSON
    
    Returns:
        Tipo: 'route', 'as', 'mixed', 't4', 'crossdocking'
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verifica campo Type
        context_type = data.get('Type', '').lower()
        if context_type:
            return context_type
        
        # Fallback para 'route' se não especificado
        return 'route'
    
    except Exception:
        return 'route'


def execute_palletization(context: Context, service: CalculatorPalletizingService, log: logging.Logger) -> Context:
    """
    Executa as cadeias de regras apropriadas baseado no tipo do contexto
    
    Args:
        context: Contexto carregado
        service: Serviço de paletização
        log: Logger
        
    Returns:
        Context processado
    """
    context_type = getattr(context, 'Type', 'route').lower()
    
    log.info(f"Tipo de contexto: {context_type}")
    log.info("Iniciando execução das regras...")
    
    # Executa principal_route_chain primeiro (se aplicável)
    if context_type in ['route', 'mixed']:
        log.info("▶ Executando Principal Route Chain...")
        context = service.execute_chain(service.principal_route_chain, context)
    
    # Executa route_chain
    if context_type == 'route' or context_type == 'mixed':
        log.info("▶ Executando Route Chain...")
        context = service.execute_chain(service.route_chain, context)
    
    # Executa AS chain
    if context_type == 'as' or context_type == 'mixed':
        log.info("▶ Executando AS Chain...")
        context = service.execute_chain(service.as_chain, context)
    
    # Executa Mixed chain
    if context_type == 'mixed':
        log.info("▶ Executando Mixed Chain...")
        context = service.execute_chain(service.mixed_chain, context)
    
    # Executa CrossDocking chain
    if context_type == 'crossdocking':
        log.info("▶ Executando CrossDocking Chain...")
        context = service.execute_chain(service.crossdocking_chain, context)
    
    # Executa T4 chain
    if context_type == 't4':
        log.info("▶ Executando T4 Chain...")
        context = service.execute_chain(service.t4_chain, context)
    
    # Sempre executa Common chain no final
    log.info("▶ Executando Common Chain...")
    context = service.execute_chain(service.common_chain, context)
    
    return context


def save_results(context: Context, output_path: Optional[Path] = None, log: logging.Logger = None):
    """
    Salva resultados da paletização
    
    Args:
        context: Contexto processado
        output_path: Caminho para salvar resultado (opcional)
        log: Logger
    """
    if not output_path:
        return
    
    try:
        # Prepara dados de saída
        results = {
            "MapNumber": getattr(context, 'MapNumber', 'unknown'),
            "Type": getattr(context, 'Type', 'unknown'),
            "TotalMountedSpaces": len(context.MountedSpaces) if hasattr(context, 'MountedSpaces') else 0,
            "TotalOrders": len(context.orders) if hasattr(context, 'orders') else 0,
            "MountedSpaces": []
        }
        
        # Adiciona detalhes dos mounted spaces
        if hasattr(context, 'MountedSpaces') and context.MountedSpaces:
            for ms in context.MountedSpaces:
                ms_data = {
                    "Side": getattr(ms.Space, 'Side', 'N/A'),
                    "Bay": getattr(ms.Space, 'Number', 'N/A'),
                    "Occupation": getattr(ms, 'Occupation', 0),
                    "TotalProducts": sum(len(c.Products) for c in ms.Containers)
                }
                results["MountedSpaces"].append(ms_data)
        
        # Salva em JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        if log:
            log.info(f"✓ Resultados salvos em: {output_path}")
    
    except Exception as e:
        if log:
            log.error(f"Erro ao salvar resultados: {e}")


def main():
    """Função principal"""
    log = setup_logging()
    
    # Valida argumentos
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python run_palletization.py input.json")
        print("  python run_palletization.py config.json data.json")
        print("  python run_palletization.py input.json --output result.json")
        sys.exit(1)
    
    # Parse argumentos
    input_files = []
    output_file = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--output' or arg == '-o':
            if i + 1 < len(sys.argv):
                output_file = Path(sys.argv[i + 1])
                i += 2
            else:
                log.error("--output requer um arquivo")
                sys.exit(1)
        else:
            input_files.append(Path(arg))
            i += 1
    
    # Valida arquivos de entrada
    for file_path in input_files:
        if not file_path.exists():
            log.error(f"Arquivo não encontrado: {file_path}")
            sys.exit(1)
    
    try:
        log.info("="*80)
        log.info("SISTEMA DE PALETIZAÇÃO")
        log.info("="*80)
        
        # Carrega contexto
        log.info(f"Carregando dados de: {', '.join(str(f) for f in input_files)}")
        
        if len(input_files) == 1:
            # Um arquivo: assume que é o JSON de entrada
            context = Context(json_path=input_files[0])
        else:
            # Dois arquivos: config e data
            context = Context(config_path=input_files[0], json_path=input_files[1])
        
        log.info("✓ Contexto carregado")
        
        # Inicializa serviço
        log.info("Inicializando serviço de paletização...")
        service = CalculatorPalletizingService()
        log.info("✓ Serviço inicializado")
        
        # Estado inicial
        initial_spaces = len(context.MountedSpaces) if hasattr(context, 'MountedSpaces') else 0
        log.info(f"Estado inicial: {initial_spaces} mounted spaces")
        
        # Executa paletização
        log.info("-"*80)
        context = execute_palletization(context, service, log)
        log.info("-"*80)
        
        # Estado final
        final_spaces = len(context.MountedSpaces) if hasattr(context, 'MountedSpaces') else 0
        log.info(f"Estado final: {final_spaces} mounted spaces (Δ +{final_spaces - initial_spaces})")
        
        # Estatísticas
        if hasattr(context, 'MountedSpaces') and context.MountedSpaces:
            total_products = sum(
                sum(len(c.Products) for c in ms.Containers)
                for ms in context.MountedSpaces
            )
            log.info(f"Total de produtos paletizados: {total_products}")
            
            total_occupation = sum(
                getattr(ms, 'Occupation', 0)
                for ms in context.MountedSpaces
            )
            avg_occupation = total_occupation / len(context.MountedSpaces)
            log.info(f"Ocupação média: {avg_occupation:.2f}%")
        
        # Salva resultados
        if output_file:
            save_results(context, output_file, log)
        
        log.info("="*80)
        log.info("✓ PALETIZAÇÃO CONCLUÍDA COM SUCESSO")
        log.info("="*80)
        
    except Exception as e:
        log.error("="*80)
        log.error(f"✗ ERRO: {e}")
        log.error("="*80)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()