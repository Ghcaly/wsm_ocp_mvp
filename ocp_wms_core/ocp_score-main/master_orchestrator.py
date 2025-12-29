#!/usr/bin/env python3
"""
Master Orchestrator - Fluxo Completo de Processamento

Orquestra todo o fluxo: XML → JSON → Config → Marketplace Check → Boxing → Paletização → TXT
"""

import sys
import os
from pathlib import Path
import logging
import requests
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile

# Imports dos módulos
from service.config_generator import ConfigGenerator
from service.marketplace_detector import get_detector
from service.boxing_integrator import get_integrator
# Não importar diretamente devido a imports relativos
# from service.calculator_palletizing_service import CalculatorPalletizingService
# from adapters.palletize_text_report import PalletizeTextReport
import subprocess

# Configuração
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


class MasterOrchestrator:
    """Orquestrador master do fluxo completo"""
    
    def __init__(self):
        self.converter_url = "http://localhost:8000"
        self.boxing_url = "http://localhost:8001"
        self.config_generator = ConfigGenerator()
        self.marketplace_detector = get_detector()
        self.boxing_integrator = get_integrator()
        self.temp_dir = Path("/tmp/ocp_processing")
        self.temp_dir.mkdir(exist_ok=True)
    
    def process_complete_flow(self, xml_content: str, 
                             output_format: str = "txt") -> Dict[str, Any]:
        """
        Processa fluxo completo: XML → TXT final
        
        Args:
            xml_content: Conteúdo do XML
            output_format: Formato de saída ('txt', 'json', 'both')
            
        Returns:
            Dict com resultados e caminhos dos arquivos
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.temp_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        log.info(f"=== INICIANDO PROCESSAMENTO COMPLETO [{session_id}] ===")
        
        try:
            # PASSO 1: Converter XML → JSON
            log.info("[1/7] Convertendo XML para JSON...")
            json_data = self._convert_xml_to_json(xml_content)
            
            # Salvar JSON intermediário
            input_json_path = session_dir / "input.json"
            with open(input_json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            log.info(f"✓ JSON salvo: {input_json_path}")
            
            # PASSO 2: Gerar config.json
            log.info("[2/7] Gerando arquivo de configuração...")
            config_path = self._generate_config(input_json_path, session_dir)
            log.info(f"✓ Config gerado: {config_path}")
            
            # PASSO 3: Verificar produtos marketplace
            log.info("[3/7] Verificando produtos marketplace...")
            marketplace_analysis = self.marketplace_detector.analyze_input(json_data)
            log.info(f"✓ Análise marketplace: {marketplace_analysis['marketplace_count']}/{marketplace_analysis['total_items']} itens são marketplace")
            
            # PASSO 4: Processar boxing (se tiver marketplace)
            boxing_result = None
            if marketplace_analysis['has_marketplace']:
                log.info("[4/7] Processando boxing para produtos marketplace...")
                marketplace_items, _ = self._extract_marketplace_items(json_data, marketplace_analysis)
                boxing_result = self.boxing_integrator.process_boxing(marketplace_items)
                
                if boxing_result:
                    # Salvar resultado do boxing
                    boxing_path = session_dir / "boxing_result.json"
                    with open(boxing_path, 'w', encoding='utf-8') as f:
                        json.dump(boxing_result, f, indent=2, ensure_ascii=False)
                    log.info(f"✓ Boxing processado e salvo: {boxing_path}")
            else:
                log.info("[4/7] Nenhum produto marketplace detectado, pulando boxing")
            
            # PASSO 5: Executar paletização completa
            log.info("[5/7] Executando paletização...")
            output_dir = session_dir / "output"
            output_dir.mkdir(exist_ok=True)
            
            palletization_result = self._execute_palletization(
                config_path=config_path,
                input_path=input_json_path,
                output_dir=output_dir,
                boxing_result=boxing_result
            )
            log.info(f"✓ Paletização concluída")
            
            # PASSO 6: Gerar relatório TXT
            log.info("[6/7] Gerando relatório TXT...")
            txt_path = self._generate_txt_report(palletization_result, output_dir)
            log.info(f"✓ Relatório TXT gerado: {txt_path}")
            
            # PASSO 7: Preparar resultado final
            log.info("[7/7] Preparando resultado final...")
            result = {
                'success': True,
                'session_id': session_id,
                'processing_time': None,  # TODO: calcular tempo
                'marketplace_analysis': marketplace_analysis,
                'has_boxing': boxing_result is not None,
                'files': {
                    'input_json': str(input_json_path),
                    'config_json': str(config_path),
                    'output_json': str(output_dir / 'palletize_result.json'),
                    'output_txt': str(txt_path),
                },
                'result': palletization_result
            }
            
            log.info(f"=== PROCESSAMENTO COMPLETO [{session_id}] ===")
            
            return result
            
        except Exception as e:
            log.error(f"Erro no processamento: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    
    def _convert_xml_to_json(self, xml_content: str) -> Dict:
        """Converte XML para JSON usando wms_converter API"""
        try:
            # Salva XML temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml_content)
                xml_path = f.name
            
            # Chama API
            with open(xml_path, 'rb') as f:
                response = requests.post(
                    f"{self.converter_url}/convert",
                    files={'file': f},
                    timeout=30
                )
            
            os.unlink(xml_path)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erro no converter: {response.status_code} - {response.text}")
                
        except Exception as e:
            log.error(f"Erro ao converter XML: {e}")
            raise
    
    def _generate_config(self, input_json_path: Path, output_dir: Path) -> Path:
        """Gera arquivo de configuração"""
        output_path = output_dir / "config.json"
        self.config_generator.generate_config_file(
            str(input_json_path),
            str(output_path),
            overwrite=True
        )
        return output_path
    
    def _extract_marketplace_items(self, json_data: Dict, analysis: Dict) -> tuple:
        """Extrai itens marketplace do JSON"""
        all_items = []
        
        if 'Orders' in json_data:
            for order in json_data['Orders']:
                if 'Items' in order:
                    all_items.extend(order['Items'])
        elif 'Items' in json_data:
            all_items = json_data['Items']
        
        return self.marketplace_detector.filter_marketplace_items(all_items)
    
    def _execute_palletization(self, config_path: Path, input_path: Path,
                               output_dir: Path, boxing_result: Dict = None) -> Dict:
        """Executa paletização chamando a API ocp_wms_core (porta 5000)"""
        try:
            # TODO: Integrar boxing_result se disponível
            if boxing_result:
                log.info("Integrando resultado do boxing na paletização...")
                # Aqui você aplica as regras específicas do boxing
            
            # Chama API de paletização (porta 5000) que já está rodando
            with open(config_path, 'rb') as config_file, open(input_path, 'rb') as input_file:
                files = {
                    'config_file': ('config.json', config_file, 'application/json'),
                    'data_file': ('input.json', input_file, 'application/json')
                }
                data = {'format': 'json'}
                
                response = requests.post(
                    'http://localhost:5000/palletize/files',
                    files=files,
                    data=data,
                    timeout=300  # 5 minutos
                )
            
            if response.status_code == 200:
                result = response.json()
                
                # Salva resultado
                result_path = output_dir / 'palletize_result.json'
                with open(result_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                log.info(f"✓ Paletização concluída via API (porta 5000)")
                return result
            else:
                log.error(f"Erro na API de paletização: {response.status_code} - {response.text}")
                raise Exception(f"Paletização falhou: {response.text}")
            
        except Exception as e:
            log.error(f"Erro na paletização: {e}")
            raise
    
    def _generate_txt_report(self, palletization_result: Dict, output_dir: Path) -> Path:
        """Gera relatório TXT formatado"""
        try:
            # Procura por arquivos TXT já gerados
            txt_files = list(output_dir.glob('*-ocp-Rota.txt'))
            if txt_files:
                return txt_files[0]
            
            txt_files = list(output_dir.glob('palletize_result_map_*.txt'))
            if txt_files:
                return txt_files[0]
            
            # Se não encontrou, cria um simples
            map_number = palletization_result.get('MapNumber', 'unknown')
            txt_filename = f"{map_number}-ocp-Rota.txt"
            txt_path = output_dir / txt_filename
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("Relatório de Paletização\n")
                f.write("=" * 80 + "\n\n")
                f.write(json.dumps(palletization_result, indent=2, ensure_ascii=False))
            
            return txt_path
            
        except Exception as e:
            log.error(f"Erro ao gerar TXT: {e}")
            raise


# Instância global
orchestrator = MasterOrchestrator()


# ========== ENDPOINTS DA API ==========

@app.route('/')
def home():
    """Documentação da API"""
    return jsonify({
        'service': 'Master Orchestrator API',
        'version': '1.0.0',
        'description': 'Orquestra fluxo completo: XML → JSON → Config → Marketplace → Boxing → Paletização → TXT',
        'endpoints': {
            'POST /process-xml': 'Processa XML completo e retorna TXT',
            'POST /process-xml-file': 'Upload de arquivo XML',
            'GET /health': 'Health check',
            'GET /status/<session_id>': 'Status de processamento'
        }
    })


@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'converter': orchestrator.converter_url,
            'boxing': orchestrator.boxing_url,
            'marketplace_products': len(orchestrator.marketplace_detector.marketplace_skus)
        }
    })


@app.route('/process-xml', methods=['POST'])
def process_xml():
    """
    Processa XML (raw text no body)
    
    Body: XML como texto
    Query params:
        - format: 'txt', 'json', 'both' (default: 'txt')
    """
    try:
        xml_content = request.data.decode('utf-8')
        output_format = request.args.get('format', 'txt')
        
        result = orchestrator.process_complete_flow(xml_content, output_format)
        
        if result['success']:
            # Retorna o TXT se solicitado
            if output_format == 'txt' and 'files' in result:
                txt_path = result['files']['output_txt']
                return send_file(txt_path, mimetype='text/plain', as_attachment=True)
            else:
                return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process-xml-file', methods=['POST'])
def process_xml_file():
    """
    Upload de arquivo XML
    
    Form data:
        - file: arquivo XML
        - format: 'txt', 'json', 'both' (opcional)
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        xml_content = file.read().decode('utf-8')
        output_format = request.form.get('format', 'txt')
        
        result = orchestrator.process_complete_flow(xml_content, output_format)
        
        if result['success']:
            if output_format == 'txt' and 'files' in result:
                txt_path = result['files']['output_txt']
                return send_file(txt_path, mimetype='text/plain', as_attachment=True)
            else:
                return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    print("=" * 80)
    print("MASTER ORCHESTRATOR - API de Processamento Completo")
    print("=" * 80)
    print()
    print("Serviço iniciando em http://localhost:9000")
    print()
    print("Endpoints:")
    print("  POST /process-xml          - Processa XML (raw text)")
    print("  POST /process-xml-file     - Upload de arquivo XML")
    print("  GET  /health               - Health check")
    print()
    print("Fluxo:")
    print("  XML → wms_converter → JSON → config.json → marketplace check")
    print("  → boxing (se necessário) → paletização → TXT")
    print()
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=9000, debug=True)
