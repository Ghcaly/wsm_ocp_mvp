#!/usr/bin/env python3
"""
Flask API - API completa para processamento de mapas

Endpoints:
    POST /process-xml - Upload e processamento completo de XML
    POST /process-json - Processamento a partir de JSON
    GET /result/<map_number> - Baixar resultado TXT
    GET /health - Health check
    GET / - Documentação

Uso:
    source /home/wms_core/wms_venv/bin/activate
    cd /home/wms_core/wsm_ocp_mvp/ocp_wms_core/ocp_score-main
    python api_flask_complete.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
import json
import sys
import requests
from pathlib import Path
from datetime import datetime
import tempfile
import traceback

# Adiciona path
sys.path.insert(0, str(Path(__file__).parent))

from service.palletizing_processor import PalletizingProcessor
from service.config_generator import ConfigGenerator

# Configuração
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
WMS_CONVERTER_URL = "http://localhost:8002/convert"
OUTPUT_DIR = Path("/tmp/ocp_results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/', methods=['GET'])
def root():
    """Documentação da API"""
    return jsonify({
        "service": "API de Paletização OCP (Flask)",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "POST /process-xml": "Upload e processamento completo de XML",
            "POST /process-json": "Processamento a partir de JSON convertido",
            "GET /result/<map_number>": "Download do resultado TXT",
            "GET /json/<map_number>": "Download do resultado JSON",
            "GET /health": "Health check"
        },
        "workflow": [
            "1. Upload XML via POST /process-xml",
            "2. Sistema converte XML → JSON (WMS Converter)",
            "3. Gera configuração automaticamente",
            "4. Executa paletização (51 regras)",
            "5. Gera saída TXT profissional",
            "6. Retorna URLs para download"
        ],
        "example": {
            "curl_upload": "curl -X POST http://localhost:5001/process-xml -F 'file=@mapa.xml'",
            "curl_download": "curl http://localhost:5001/result/448111 -o resultado.txt"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    try:
        response = requests.get("http://localhost:8002/", timeout=2)
        wms_converter_ok = response.status_code == 200
    except:
        wms_converter_ok = False
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "ok",
            "wms_converter": "ok" if wms_converter_ok else "unavailable"
        }
    })


@app.route('/process-xml', methods=['POST'])
def process_xml():
    """
    Upload e processamento completo de arquivo XML
    
    Form data:
        file: Arquivo XML do mapa
        
    Returns:
        JSON com resultado do processamento
    """
    start_time = datetime.now()
    
    try:
        # Valida arquivo
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "Nenhum arquivo enviado"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "Nome de arquivo vazio"
            }), 400
        
        if not file.filename.endswith('.xml'):
            return jsonify({
                "success": False,
                "error": "Arquivo deve ser XML"
            }), 400
        
        logger.info(f"📥 Recebendo arquivo: {file.filename}")
        
        # Salva arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
            file.save(tmp_file.name)
            tmp_xml_path = Path(tmp_file.name)
        
        logger.info(f"💾 Arquivo salvo: {tmp_xml_path}")
        
        # STEP 1: Converte XML → JSON
        logger.info("🔄 STEP 1: Convertendo XML → JSON")
        
        with open(tmp_xml_path, 'rb') as f:
            files = {'file': (file.filename, f, 'application/xml')}
            response = requests.post(WMS_CONVERTER_URL, files=files, timeout=30)
        
        if response.status_code != 200:
            tmp_xml_path.unlink()
            return jsonify({
                "success": False,
                "error": f"Erro ao converter XML: {response.text}"
            }), 500
        
        json_data = response.json()
        map_number = json_data.get('MapNumber', 0)
        
        logger.info(f"✅ JSON convertido - Mapa: {map_number}")
        
        # Salva JSON
        json_file = OUTPUT_DIR / f"{map_number}_input.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # STEP 2: Gera configuração
        logger.info("⚙️  STEP 2: Gerando configuração")
        
        config_generator = ConfigGenerator()
        config_file = OUTPUT_DIR / f"config_{map_number}.json"
        config_generator.generate_config_file(
            input_file=str(json_file),
            output_file=str(config_file),
            overwrite=True
        )
        
        logger.info(f"✅ Configuração gerada: {config_file}")
        
        # STEP 3-4: Processa paletização
        logger.info("🎯 STEP 3-4: Processando paletização e gerando TXT")
        
        processor = PalletizingProcessor()
        result = processor.run_complete_palletizing_process(
            config_file=str(config_file),
            data_file=str(json_file),
            output_dir=str(OUTPUT_DIR)
        )
        
        # Extrai estatísticas
        context = result.get('context')
        pallets_count = len(context.MountedSpaces) if context else 0
        
        units_palletized = 0
        total_weight = 0.0
        if context and context.MountedSpaces:
            for space in context.MountedSpaces:
                for container in space.Containers:
                    for product in container.Products:
                        units_palletized += product.Amount
                        total_weight += float(product.Weight or 0)
        
        # Arquivos de saída
        txt_file = OUTPUT_DIR / f"{map_number}-ocp-map.txt"
        json_output = OUTPUT_DIR / f"{map_number}-ocp-map.json"
        
        # Tempo de processamento
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Remove arquivo temporário
        tmp_xml_path.unlink()
        
        logger.info(f"✅ Processamento concluído em {processing_time:.2f}s")
        logger.info(f"   📦 {pallets_count} paletes, {units_palletized} unidades, {total_weight:.2f}kg")
        
        return jsonify({
            "success": True,
            "map_number": map_number,
            "message": "Processamento concluído com sucesso",
            "statistics": {
                "pallets_count": pallets_count,
                "units_palletized": units_palletized,
                "total_weight": round(total_weight, 2),
                "processing_time": round(processing_time, 2)
            },
            "files": {
                "txt": str(txt_file),
                "json": str(json_output),
                "config": str(config_file)
            },
            "download_urls": {
                "txt": f"/result/{map_number}",
                "json": f"/json/{map_number}"
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "detail": traceback.format_exc()
        }), 500


@app.route('/process-json', methods=['POST'])
def process_json():
    """
    Processamento a partir de JSON já convertido
    
    Body (JSON):
        JSON do mapa já convertido
        
    Returns:
        JSON com resultado do processamento
    """
    start_time = datetime.now()
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "JSON inválido ou vazio"
            }), 400
        
        map_number = data.get('MapNumber', 0)
        
        if not map_number:
            return jsonify({
                "success": False,
                "error": "MapNumber não encontrado no JSON"
            }), 400
        
        logger.info(f"🔄 Processando JSON do mapa: {map_number}")
        
        # Salva JSON
        json_file = OUTPUT_DIR / f"{map_number}_input.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Gera configuração
        logger.info("⚙️  Gerando configuração")
        config_generator = ConfigGenerator()
        config_file = OUTPUT_DIR / f"config_{map_number}.json"
        config_generator.generate_config_file(
            input_file=str(json_file),
            output_file=str(config_file),
            overwrite=True
        )
        
        # Processa paletização
        logger.info("🎯 Processando paletização")
        processor = PalletizingProcessor()
        result = processor.run_complete_palletizing_process(
            config_file=str(config_file),
            data_file=str(json_file),
            output_dir=str(OUTPUT_DIR)
        )
        
        # Extrai estatísticas
        context = result.get('context')
        pallets_count = len(context.MountedSpaces) if context else 0
        
        units_palletized = 0
        total_weight = 0.0
        if context and context.MountedSpaces:
            for space in context.MountedSpaces:
                for container in space.Containers:
                    for product in container.Products:
                        units_palletized += product.Amount
                        total_weight += float(product.Weight or 0)
        
        txt_file = OUTPUT_DIR / f"{map_number}-ocp-map.txt"
        json_output = OUTPUT_DIR / f"{map_number}-ocp-map.json"
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Processamento concluído em {processing_time:.2f}s")
        
        return jsonify({
            "success": True,
            "map_number": map_number,
            "message": "Processamento concluído com sucesso",
            "statistics": {
                "pallets_count": pallets_count,
                "units_palletized": units_palletized,
                "total_weight": round(total_weight, 2),
                "processing_time": round(processing_time, 2)
            },
            "files": {
                "txt": str(txt_file),
                "json": str(json_output),
                "config": str(config_file)
            },
            "download_urls": {
                "txt": f"/result/{map_number}",
                "json": f"/json/{map_number}"
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "detail": traceback.format_exc()
        }), 500


@app.route('/result/<int:map_number>', methods=['GET'])
def get_result(map_number):
    """
    Download do arquivo TXT resultado
    
    Args:
        map_number: Número do mapa
        
    Returns:
        Arquivo TXT para download
    """
    txt_file = OUTPUT_DIR / f"{map_number}-ocp-map.txt"
    
    if not txt_file.exists():
        return jsonify({
            "success": False,
            "error": f"Resultado não encontrado para mapa {map_number}"
        }), 404
    
    return send_file(
        txt_file,
        as_attachment=True,
        download_name=f"{map_number}-ocp-map.txt",
        mimetype="text/plain"
    )


@app.route('/json/<int:map_number>', methods=['GET'])
def get_json(map_number):
    """
    Download do arquivo JSON resultado
    
    Args:
        map_number: Número do mapa
        
    Returns:
        Arquivo JSON para download
    """
    json_file = OUTPUT_DIR / f"{map_number}-ocp-map.json"
    
    if not json_file.exists():
        return jsonify({
            "success": False,
            "error": f"JSON não encontrado para mapa {map_number}"
        }), 404
    
    return send_file(
        json_file,
        as_attachment=True,
        download_name=f"{map_number}-ocp-map.json",
        mimetype="application/json"
    )


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 API Flask - Paletização OCP")
    print("=" * 70)
    print(f"📍 URL: http://localhost:5001")
    print(f"📂 Output: {OUTPUT_DIR}")
    print(f"🔧 WMS Converter: {WMS_CONVERTER_URL}")
    print("=" * 70)
    print("\nEndpoints disponíveis:")
    print("  POST /process-xml - Upload e processa XML")
    print("  POST /process-json - Processa JSON")
    print("  GET /result/<map> - Download TXT")
    print("  GET /json/<map> - Download JSON")
    print("  GET /health - Health check")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
