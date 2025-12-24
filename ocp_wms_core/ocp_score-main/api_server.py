#!/usr/bin/env python3
"""
API Server - Endpoint REST para paletização

Endpoints:
    POST /palletize - Executa paletização
    GET /health - Health check
    GET / - Documentação

Uso:
    python api_server.py
    
    Servidor rodando em: http://localhost:5000
"""

import sys
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any

# Imports do projeto
import service.calculator_palletizing_service as calc_service
import domain.context as ctx

CalculatorPalletizingService = calc_service.CalculatorPalletizingService
Context = ctx.Context

# Configuração
app = Flask(__name__)
CORS(app)  # Permite CORS para testes
app.config['JSON_AS_ASCII'] = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


def execute_palletization(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa paletização com os dados recebidos
    
    Args:
        data: Dados do JSON recebido
        
    Returns:
        Resultado da paletização
    """
    # Cria contexto a partir dos dados
    context = Context()
    
    # Carrega dados no contexto (você pode precisar adaptar isso)
    if 'orders' in data:
        context._orders = data['orders']
    if 'spaces' in data:
        context._spaces = data['spaces']
    if 'settings' in data:
        context.settings = data['settings']
    
    # Detecta tipo
    context_type = data.get('Type', 'route').lower()
    
    # Inicializa serviço
    service = CalculatorPalletizingService()
    
    # Executa cadeias apropriadas
    log.info(f"Executando paletização tipo: {context_type}")
    
    if context_type in ['route', 'mixed']:
        context = service.execute_chain(service.principal_route_chain, context)
        context = service.execute_chain(service.route_chain, context)
    
    if context_type == 'as' or context_type == 'mixed':
        context = service.execute_chain(service.as_chain, context)
    
    if context_type == 'mixed':
        context = service.execute_chain(service.mixed_chain, context)
    
    if context_type == 'crossdocking':
        context = service.execute_chain(service.crossdocking_chain, context)
    
    if context_type == 't4':
        context = service.execute_chain(service.t4_chain, context)
    
    # Sempre executa common no final
    context = service.execute_chain(service.common_chain, context)
    
    # Prepara resposta
    result = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "type": context_type,
        "statistics": {
            "total_mounted_spaces": len(context.MountedSpaces) if hasattr(context, 'MountedSpaces') else 0,
            "total_orders": len(context.orders) if hasattr(context, 'orders') else 0,
        },
        "mounted_spaces": []
    }
    
    # Adiciona detalhes dos mounted spaces
    if hasattr(context, 'MountedSpaces') and context.MountedSpaces:
        total_products = 0
        total_occupation = 0.0
        
        for ms in context.MountedSpaces:
            products_count = sum(len(c.Products) for c in ms.Containers)
            total_products += products_count
            
            occupation = getattr(ms, 'Occupation', 0)
            total_occupation += occupation
            
            ms_data = {
                "side": getattr(ms.Space, 'Side', 'N/A'),
                "bay": getattr(ms.Space, 'Number', 'N/A'),
                "occupation": occupation,
                "products_count": products_count
            }
            result["mounted_spaces"].append(ms_data)
        
        result["statistics"]["total_products"] = total_products
        result["statistics"]["average_occupation"] = total_occupation / len(context.MountedSpaces)
    
    return result


@app.route('/', methods=['GET'])
def index():
    """Documentação da API"""
    docs = {
        "name": "API de Paletização",
        "version": "1.0.0",
        "endpoints": {
            "POST /palletize": {
                "description": "Executa paletização",
                "body": {
                    "Type": "route | as | mixed | crossdocking | t4",
                    "orders": "Lista de pedidos",
                    "spaces": "Lista de espaços/baias",
                    "settings": "Configurações"
                },
                "response": {
                    "success": "boolean",
                    "statistics": "Estatísticas da paletização",
                    "mounted_spaces": "Lista de pallets montados"
                }
            },
            "GET /health": {
                "description": "Health check do servidor",
                "response": {
                    "status": "ok"
                }
            }
        },
        "examples": {
            "curl": "curl -X POST http://localhost:5000/palletize -H 'Content-Type: application/json' -d @input.json"
        }
    }
    return jsonify(docs), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "palletization-api"
    }), 200


@app.route('/palletize', methods=['POST'])
def palletize():
    """
    Endpoint principal - recebe JSON e executa paletização
    
    Body:
        JSON com dados de entrada
        
    Returns:
        JSON com resultados da paletização
    """
    try:
        # Valida request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type deve ser application/json"
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Body vazio"
            }), 400
        
        log.info(f"Recebida requisição de paletização - Tipo: {data.get('Type', 'route')}")
        
        # Executa paletização
        result = execute_palletization(data)
        
        log.info(f"Paletização concluída - {result['statistics']['total_mounted_spaces']} mounted spaces")
        
        return jsonify(result), 200
    
    except Exception as e:
        log.error(f"Erro ao processar requisição: {e}")
        log.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/palletize/file', methods=['POST'])
def palletize_file():
    """
    Endpoint alternativo - recebe arquivo JSON
    
    Form Data:
        file: arquivo JSON
        
    Returns:
        JSON com resultados
    """
    try:
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
        
        # Lê conteúdo do arquivo
        content = file.read().decode('utf-8')
        data = json.loads(content)
        
        log.info(f"Recebido arquivo: {file.filename}")
        
        # Executa paletização
        result = execute_palletization(data)
        
        return jsonify(result), 200
    
    except json.JSONDecodeError as e:
        return jsonify({
            "success": False,
            "error": f"JSON inválido: {str(e)}"
        }), 400
    
    except Exception as e:
        log.error(f"Erro ao processar arquivo: {e}")
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handler para rotas não encontradas"""
    return jsonify({
        "success": False,
        "error": "Endpoint não encontrado",
        "available_endpoints": ["/", "/health", "/palletize", "/palletize/file"]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handler para erros internos"""
    return jsonify({
        "success": False,
        "error": "Erro interno do servidor"
    }), 500


def main():
    """Inicia o servidor"""
    print("="*80)
    print("API DE PALETIZAÇÃO")
    print("="*80)
    print()
    print("Servidor iniciando...")
    print()
    print("Endpoints disponíveis:")
    print("  • GET  /          - Documentação")
    print("  • GET  /health    - Health check")
    print("  • POST /palletize - Executar paletização (JSON no body)")
    print("  • POST /palletize/file - Executar paletização (arquivo)")
    print()
    print("Exemplos de uso:")
    print("  curl http://localhost:5000/health")
    print("  curl -X POST http://localhost:5000/palletize -H 'Content-Type: application/json' -d @input.json")
    print("  curl -X POST http://localhost:5000/palletize/file -F 'file=@input.json'")
    print()
    print("="*80)
    print()
    
    # Inicia servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )


if __name__ == '__main__':
    main()
