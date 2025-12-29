"""
Script para processar múltiplos mapas de paletização em lote.

Este script percorre uma pasta raiz, identifica subpastas com arquivos de entrada
(input.json, config.json, output.txt) e executa o processo de paletização para cada mapa.
Os resultados são salvos em uma pasta 'output' dentro de cada subpasta processada.

Uso:
    python -m ocp_score_ia.service.run_all <caminho_pasta_raiz>
    
Exemplo:
    python -m ocp_score_ia.service.run_all "C:/data/mapas"
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime
import json
import traceback
from ocp_score_ia.adapters.comparar_relatorios import processar_batch_mapas
from .palletizing_processor import PalletizingProcessor


COMPARACAO_DISPONIVEL = True

class BatchPalletizingProcessor:
    """
    Processador em lote para múltiplos mapas de paletização.
    """
    
    def __init__(self, root_folder: str, debug_enabled: bool = True):
        """
        Inicializa o processador em lote.
        
        Args:
            root_folder: Pasta raiz contendo subpastas com mapas
            debug_enabled: Habilitar logging detalhado
        """
        self.root_folder = Path(root_folder)
        self.debug_enabled = debug_enabled
        self.logger = self._setup_logging()
        self.results_summary: List[Dict[str, Any]] = []
        
    def _setup_logging(self) -> logging.Logger:
        """Configura logging para processamento em lote."""
        level = logging.DEBUG if self.debug_enabled else logging.INFO
        
        # Cria logger específico para batch processing
        logger = logging.getLogger(f"{__name__}.batch")
        logger.setLevel(level)
        
        # Remove handlers existentes
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - BATCH - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (log geral do processamento em lote)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.root_folder / f'batch_processing_{timestamp}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def find_map_folders(self) -> List[Path]:
        """
        Encontra todas as subpastas que contêm arquivos de mapa válidos.
        
        Uma pasta é considerada válida se contém pelo menos:
        - input.json
        - config.json
        
        Returns:
            Lista de caminhos para pastas válidas
        """
        self.logger.info("=" * 80)
        self.logger.info(f"Procurando mapas em: {self.root_folder}")
        self.logger.info("=" * 80)
        
        if not self.root_folder.exists():
            self.logger.error(f"Pasta raiz não encontrada: {self.root_folder}")
            return []
        
        valid_folders = []
        
        # Percorre todas as subpastas (1 nível de profundidade)
        for folder in self.root_folder.iterdir():
            if not folder.is_dir():
                continue
            
            # Verifica se contém arquivos necessários
            input_file = folder / 'input.json'
            config_file = folder / 'config.json'
            
            # Arquivo de validação pode ser output.txt ou output.json
            validation_file = None
            if (folder / 'output.txt').exists():
                validation_file = folder / 'output.txt'
            elif (folder / 'output.json').exists():
                validation_file = folder / 'output.json'
            
            # Valida presença dos arquivos essenciais
            if input_file.exists() and config_file.exists():
                self.logger.info(f"✓ Mapa encontrado: {folder.name}")
                self.logger.info(f"  - input.json: {'✓' if input_file.exists() else '✗'}")
                self.logger.info(f"  - config.json: {'✓' if config_file.exists() else '✗'}")
                self.logger.info(f"  - validação: {'✓ ' + validation_file.name if validation_file else '✗ (opcional)'}")
                
                valid_folders.append(folder)
            else:
                missing = []
                if not input_file.exists():
                    missing.append('input.json')
                if not config_file.exists():
                    missing.append('config.json')
                
                self.logger.warning(f"✗ Pasta incompleta: {folder.name} (faltando: {', '.join(missing)})")
        
        self.logger.info("=" * 80)
        self.logger.info(f"Total de mapas válidos encontrados: {len(valid_folders)}")
        self.logger.info("=" * 80)
        
        return sorted(valid_folders, reverse=True)
    
    def process_single_map(self, map_folder: Path) -> Dict[str, Any]:
        """
        Processa um único mapa de paletização.
        
        Args:
            map_folder: Pasta contendo os arquivos do mapa
            
        Returns:
            Dict com resultado do processamento
        """
        map_name = map_folder.name
        
        self.logger.info("")
        self.logger.info("*" * 80)
        self.logger.info(f"PROCESSANDO MAPA: {map_name}")
        self.logger.info("*" * 80)
        
        start_time = datetime.now()
        
        # Prepara caminhos dos arquivos
        input_file = map_folder / 'input.json'
        config_file = map_folder / 'config.json'
        output_dir = map_folder / 'output'
        
        # Encontra arquivo de validação
        validation_file = None
        if (map_folder / 'output.txt').exists():
            validation_file = map_folder / 'output.txt'
        elif (map_folder / 'output.json').exists():
            validation_file = map_folder / 'output.json'
        
        # Cria diretório de saída
        output_dir.mkdir(exist_ok=True)
        
        result = {
            'map_name': map_name,
            'map_folder': str(map_folder),
            'success': False,
            'error': None,
            'start_time': start_time.isoformat(),
            'end_time': None,
            'duration_seconds': None,
            'statistics': {},
            'output_files': []
        }
        
        try:
            # Cria processador para este mapa
            processor = PalletizingProcessor(debug_enabled=self.debug_enabled)
            
            # Executa processamento completo
            processing_result = processor.run_complete_palletizing_process(
                config_file=str(config_file),
                data_file=str(input_file),
                output_dir=str(output_dir),
                validation_file=str(validation_file) if validation_file else None
            )
            
            # Atualiza resultado
            result['success'] = processing_result.get('success', False)
            result['statistics'] = processing_result.get('statistics', {})
            
            # Lista arquivos gerados no output_dir
            if output_dir.exists():
                result['output_files'] = [str(f.name) for f in output_dir.iterdir() if f.is_file()]
            
            if result['success']:
                self.logger.info(f"✅ Mapa {map_name} processado com SUCESSO")
            else:
                result['error'] = processing_result.get('error', 'Erro desconhecido')
                self.logger.error(f"❌ Mapa {map_name} falhou: {result['error']}")
                
        except Exception as e:
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()
            self.logger.error(f"❌ Erro ao processar mapa {map_name}:")
            self.logger.error(traceback.format_exc())
        
        finally:
            end_time = datetime.now()
            result['end_time'] = end_time.isoformat()
            result['duration_seconds'] = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Tempo de processamento: {result['duration_seconds']:.2f}s")
            self.logger.info("*" * 80)
        
        return result
    
    def process_all_maps(self) -> List[Dict[str, Any]]:
        """
        Processa todos os mapas encontrados na pasta raiz.
        
        Returns:
            Lista com resultados de cada processamento
        """
        overall_start = datetime.now()
        
        self.logger.info("")
        self.logger.info("🚀" * 40)
        self.logger.info("INICIANDO PROCESSAMENTO EM LOTE DE MAPAS")
        self.logger.info("🚀" * 40)
        self.logger.info("")
        
        exclude_maps = ["621425", "121758", "622148", "622075"]
        # Encontra mapas válidos
        map_folders = [mf for mf in self.find_map_folders() if mf.name not in exclude_maps]
        
        map_folders = [
                mf for mf in self.find_map_folders()
                if mf.name.isdigit()
                and 599 <= int(mf.name[:3]) <= 629
                and mf.name not in exclude_maps
            ]

        if not map_folders:
            self.logger.warning("⚠️ Nenhum mapa válido encontrado!")
            return []
        
        # Processa cada mapa
        results = []
        for i, map_folder in enumerate(map_folders, 1):
            self.logger.info(f"\n📍 Progresso: {i}/{len(map_folders)} mapas")
            
            result = self.process_single_map(map_folder)
            results.append(result)
            
            self.results_summary.append(result)
        
        # Gera resumo final
        overall_end = datetime.now()
        overall_duration = (overall_end - overall_start).total_seconds()
        
        self._generate_summary_report(results, overall_duration)
        
        # NOVO: Gera planilha consolidada de comparação WMS vs API
        self._generate_consolidated_comparison()
        
        return results
    
    def _generate_summary_report(self, results: List[Dict[str, Any]], total_duration: float):
        """
        Gera relatório resumido do processamento em lote.
        
        Args:
            results: Lista de resultados de cada mapa
            total_duration: Duração total do processamento em segundos
        """
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("RESUMO DO PROCESSAMENTO EM LOTE")
        self.logger.info("=" * 80)
        
        total_maps = len(results)
        successful = sum(1 for r in results if r['success'])
        failed = total_maps - successful
        
        self.logger.info(f"📊 Total de mapas processados: {total_maps}")
        self.logger.info(f"✅ Sucessos: {successful}")
        self.logger.info(f"❌ Falhas: {failed}")
        self.logger.info(f"⏱️ Tempo total: {total_duration:.2f}s ({total_duration/60:.2f} minutos)")
        
        if total_maps > 0:
            avg_time = total_duration / total_maps
            self.logger.info(f"⏱️ Tempo médio por mapa: {avg_time:.2f}s")
        
        # Detalhes de falhas
        if failed > 0:
            self.logger.info("")
            self.logger.info("❌ MAPAS QUE FALHARAM:")
            for result in results:
                if not result['success']:
                    self.logger.info(f"  - {result['map_name']}: {result['error']}")
        
        # Estatísticas agregadas
        if successful > 0:
            self.logger.info("")
            self.logger.info("📈 ESTATÍSTICAS AGREGADAS (MAPAS BEM-SUCEDIDOS):")
            
            total_orders = sum(r['statistics'].get('orders_processed', 0) for r in results if r['success'])
            total_pallets = sum(r['statistics'].get('pallets_created', 0) for r in results if r['success'])
            total_items = sum(r['statistics'].get('total_items', 0) for r in results if r['success'])
            
            self.logger.info(f"  - Total de orders: {total_orders}")
            self.logger.info(f"  - Total de pallets: {total_pallets}")
            self.logger.info(f"  - Total de itens: {total_items}")
        
        # Salva resumo em JSON
        self._save_summary_json(results, total_duration)
        
        self.logger.info("=" * 80)
    
    def _save_summary_json(self, results: List[Dict[str, Any]], total_duration: float):
        """
        Salva resumo detalhado em arquivo JSON.
        
        Args:
            results: Lista de resultados
            total_duration: Duração total em segundos
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = self.root_folder / f'batch_summary_{timestamp}.json'
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'root_folder': str(self.root_folder),
            'total_duration_seconds': total_duration,
            'total_maps': len(results),
            'successful_maps': sum(1 for r in results if r['success']),
            'failed_maps': sum(1 for r in results if not r['success']),
            'results': results
        }
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📄 Resumo JSON salvo em: {summary_file}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar resumo JSON: {e}")
    
    def _generate_consolidated_comparison(self):
        """
        Gera planilha consolidada comparando WMS vs API para todos os mapas processados.
        """
        if not COMPARACAO_DISPONIVEL:
            self.logger.warning("⚠️ Módulo de comparação não disponível. Pulando geração de planilha consolidada.")
            return
        
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("GERANDO PLANILHA CONSOLIDADA WMS vs API")
        self.logger.info("=" * 80)
        
        try:
            output_file = processar_batch_mapas(self.root_folder)
            
            if output_file and output_file.exists():
                self.logger.info("")
                self.logger.info(f"✅ Planilha consolidada gerada com sucesso!")
                self.logger.info(f"📊 Arquivo: {output_file}")
            else:
                self.logger.warning("⚠️ Nenhuma planilha consolidada foi gerada.")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar planilha consolidada: {e}")
            self.logger.error(traceback.format_exc())
        
        self.logger.info("=" * 80)


def main():
    """
    Função principal para execução via linha de comando.
    """
    # if len(sys.argv) < 2:
    #     print("Uso: python -m ocp_score_ia.service.run_all <caminho_pasta_raiz>")
    #     print("")
    #     print("Exemplo:")
    #     print("  python -m ocp_score_ia.service.run_all C:/data/mapas")
    #     print("  python -m ocp_score_ia.service.run_all ../data/route")
    #     sys.exit(1)
    
    root_folder = r"C:\Users\BRKEY864393\Downloads\route\route"
    root_folder = r"C:\Users\BRKEY864393\Downloads\route_test"
    root_folder = r"C:\Users\BRKEY864393\Downloads\route_em_massa"
    # root_folder = r"C:\Users\BRKEY864393\Downloads\routes_2k\routes"
    # Processa todos os mapas
    batch_processor = BatchPalletizingProcessor(root_folder=root_folder, debug_enabled=True)
    results = batch_processor.process_all_maps()
    
    # Retorna código de saída baseado em sucesso
    if results:
        failed_count = sum(1 for r in results if not r['success'])
        sys.exit(0 if failed_count == 0 else 1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
