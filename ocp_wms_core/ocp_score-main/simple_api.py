#!/usr/bin/env python3
"""
Simple API - Servidor REST básico para paletização

Uso:
    cd /home/prd_debian/ocp_wms_core
    source wms_venv/bin/activate
    export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
    python ocp_score-main/simple_api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import sys
from pathlib import Path
from datetime import datetime

# Adiciona path
sys.path.insert(0, str(Path(__file__).parent))

# Configura app
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Caminhos dos mapas
MAPAS_DIR = Path("/home/prd_debian/mapas/in")
MAPAS_OUT_DIR = Path("/home/prd_debian/mapas/out")

# Cria pasta out se não existir
MAPAS_OUT_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/', methods=['GET'])
def index():
    """Página inicial com documentação"""
    return jsonify({
        "service": "API de Paletização",
        "version": "1.0.0",
        "status": "running",
        "mapas_directory": str(MAPAS_DIR),
        "endpoints": {
            "GET /": "Esta documentação",
            "GET /health": "Health check",
            "GET /mapas/list": "Listar arquivos disponíveis na pasta de mapas (input)",
            "GET /mapas/outputs": "Listar arquivos de resultado gerados (output)",
            "POST /mapas/process/<filename>": "Processar arquivo específico da pasta (?format=txt&data_file=outro.json)",
            "POST /mapas/process-auto": "Buscar e processar automaticamente pares de arquivos",
            "POST /palletize": "Executar paletização (JSON no body)",
            "POST /palletize/files": "Executar paletização (upload de 2 arquivos)",
            "POST /validate": "Validar JSON de entrada"
        },
        "usage": {
            "curl_list_mapas": "curl http://localhost:5000/mapas/list",
            "curl_list_outputs": "curl http://localhost:5000/mapas/outputs",
            "curl_process_mapa": "curl -X POST 'http://localhost:5000/mapas/process/config.json?format=txt'",
            "curl_process_auto": "curl -X POST http://localhost:5000/mapas/process-auto -H 'Content-Type: application/json' -d '{\"format\":\"txt\"}'",
            "curl_health": "curl http://localhost:5000/health",
            "curl_palletize_files": "curl -X POST http://localhost:5000/palletize/files -F 'config_file=@config.json' -F 'data_file=@data.json' -F 'format=txt'"
        }
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "palletization-api"
    }), 200


@app.route('/validate', methods=['POST'])
def validate():
    """Valida JSON de entrada sem executar"""
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Content-Type deve ser application/json"}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Body vazio"}), 400
        
        # Validações básicas
        errors = []
        warnings = []
        
        if 'Type' not in data:
            warnings.append("Campo 'Type' não encontrado. Assumindo 'route'")
        
        context_type = data.get('Type', 'route').lower()
        valid_types = ['route', 'as', 'mixed', 'crossdocking', 't4']
        
        if context_type not in valid_types:
            errors.append(f"Type inválido: {context_type}. Válidos: {', '.join(valid_types)}")
        
        return jsonify({
            "success": len(errors) == 0,
            "valid": len(errors) == 0,
            "type": context_type,
            "errors": errors,
            "warnings": warnings,
            "fields_found": list(data.keys())
        }), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/palletize', methods=['POST'])
def palletize():
    """
    Endpoint principal - executa paletização
    
    Este é um endpoint simplificado para demonstração.
    Para execução real, use o run_palletization.py
    """
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Content-Type deve ser application/json"}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Body vazio"}), 400
        
        context_type = data.get('Type', 'route').lower()
        
        log.info(f"Requisição de paletização recebida - Type: {context_type}")
        
        # NOTA: Aqui você importaria e executaria o serviço real
        # Para demonstração, retorna estrutura simulada
        
        try:
            # Tenta importar e executar o serviço real
            from service.calculator_palletizing_service import CalculatorPalletizingService
            from domain.context import Context
            
            log.info("Módulos importados com sucesso. Executando paletização...")
            
            # Cria contexto
            context = Context()
            
            # TODO: Carregar dados do JSON no contexto
            
            # Inicializa serviço
            service = CalculatorPalletizingService()
            
            # Executa cadeias conforme tipo
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
            
            # Common chain sempre no final
            context = service.execute_chain(service.common_chain, context)
            
            # Prepara resultado
            result = {
                "success": True,
                "message": "Paletização executada com sucesso",
                "timestamp": datetime.now().isoformat(),
                "type": context_type,
                "statistics": {
                    "total_mounted_spaces": len(context.MountedSpaces) if hasattr(context, 'MountedSpaces') else 0
                }
            }
            
            # Salva resultado em arquivo
            output_file = save_result_to_file(result, 'json', f'palletize_{context_type}')
            result['output_file'] = str(output_file)
            result['output_filename'] = output_file.name
            
            log.info(f"Paletização concluída: {result['statistics']['total_mounted_spaces']} mounted spaces")
            return jsonify(result), 200
        
        except ImportError as ie:
            log.warning(f"Não foi possível importar módulos: {ie}")
            log.info("Retornando resposta simulada...")
            
            # Resposta simulada para demonstração
            result = {
                "success": True,
                "message": "Requisição recebida (modo demonstração)",
                "note": "Para execução real, configure PYTHONPATH corretamente",
                "timestamp": datetime.now().isoformat(),
                "type": context_type,
                "received_data": {
                    "fields": list(data.keys()),
                    "type": context_type
                },
                "chains_to_execute": get_chains_for_type(context_type)
            }
            
            # Salva resultado em arquivo
            ctx = result.get('_context')
            output_file = save_result_to_file(result, 'json', f'palletize_{context_type}', ctx)
            result['output_file'] = str(output_file)
            result['output_filename'] = output_file.name
            
            return jsonify(result), 200
    
    except Exception as e:
        log.error(f"Erro ao processar requisição: {e}")
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/palletize/files', methods=['POST'])
def palletize_files():
    """
    Endpoint para receber dois arquivos (config e data) e retornar TXT
    
    Form Data:
        config_file: arquivo JSON de configuração do mapa
        data_file: arquivo JSON de entrada/dados
        format: 'json' ou 'txt' (padrão: json)
        
    Returns:
        JSON com resultados ou TXT formatado
    """
    try:
        # Valida presença dos arquivos
        if 'config_file' not in request.files:
            return jsonify({
                "success": False,
                "error": "Arquivo 'config_file' não enviado"
            }), 400
        
        if 'data_file' not in request.files:
            return jsonify({
                "success": False,
                "error": "Arquivo 'data_file' não enviado"
            }), 400
        
        config_file = request.files['config_file']
        data_file = request.files['data_file']
        output_format = request.form.get('format', 'json').lower()
        
        if config_file.filename == '' or data_file.filename == '':
            return jsonify({
                "success": False,
                "error": "Nome de arquivo vazio"
            }), 400
        
        log.info(f"Recebidos arquivos: config={config_file.filename}, data={data_file.filename}")
        
        # Lê conteúdo dos arquivos
        config_content = config_file.read().decode('utf-8')
        data_content = data_file.read().decode('utf-8')
        
        config_data = json.loads(config_content)
        data_json = json.loads(data_content)
        
        # Tenta executar paletização
        try:
            from service.calculator_palletizing_service import CalculatorPalletizingService
            from domain.context import Context
            
            log.info("Criando contexto com arquivos...")
            
            # Salva temporariamente os arquivos
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_config:
                json.dump(config_data, tmp_config)
                tmp_config_path = tmp_config.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_data:
                json.dump(data_json, tmp_data)
                tmp_data_path = tmp_data.name
            
            try:
                # Cria contexto com os arquivos
                context = Context(config_path=tmp_config_path, json_path=tmp_data_path)
                
                context_type = getattr(context, 'Type', 'route').lower()
                log.info(f"Tipo detectado: {context_type}")
                
                # Inicializa serviço
                service = CalculatorPalletizingService()
                
                # Executa cadeias apropriadas
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
                
                # Common chain sempre no final
                context = service.execute_chain(service.common_chain, context)
                
                # Prepara resultado
                mounted_spaces = []
                total_products = 0
                total_occupation = 0.0
                
                if hasattr(context, 'MountedSpaces') and context.MountedSpaces:
                    for ms in context.MountedSpaces:
                        products_count = sum(len(c.Products) for c in ms.Containers)
                        total_products += products_count
                        
                        occupation = getattr(ms, 'Occupation', 0)
                        total_occupation += occupation
                        
                        ms_data = {
                            "side": getattr(ms.Space, 'Side', 'N/A'),
                            "bay": getattr(ms.Space, 'Number', 'N/A'),
                            "occupation": occupation,
                            "products_count": products_count,
                            "containers": len(ms.Containers)
                        }
                        mounted_spaces.append(ms_data)
                
                avg_occupation = total_occupation / len(context.MountedSpaces) if context.MountedSpaces else 0
                
                result = {
                    "success": True,
                    "message": "Paletização executada com sucesso",
                    "timestamp": datetime.now().isoformat(),
                    "type": context_type,
                    "files": {
                        "config": config_file.filename,
                        "data": data_file.filename
                    },
                    "statistics": {
                        "total_mounted_spaces": len(context.MountedSpaces) if hasattr(context, 'MountedSpaces') else 0,
                        "total_orders": len(context.orders) if hasattr(context, 'orders') else 0,
                        "total_products": total_products,
                        "average_occupation": avg_occupation
                    },
                    "mounted_spaces": mounted_spaces
                }
                
                # Remove arquivos temporários
                os.unlink(tmp_config_path)
                os.unlink(tmp_data_path)
                
                # Salva resultado em arquivo
                ctx = result.get('_context')
                output_file = save_result_to_file(result, output_format, config_file.filename, ctx)
                result['output_file'] = str(output_file)
                result['output_filename'] = output_file.name
                
                # Remove context antes de retornar
                result.pop('_context', None)
                
                # Retorna em formato solicitado
                if output_format == 'txt':
                    return generate_txt_report(result), 200, {'Content-Type': 'text/plain; charset=utf-8'}
                else:
                    return jsonify(result), 200
            
            finally:
                # Garante limpeza dos arquivos temporários
                try:
                    if os.path.exists(tmp_config_path):
                        os.unlink(tmp_config_path)
                    if os.path.exists(tmp_data_path):
                        os.unlink(tmp_data_path)
                except:
                    pass
        
        except ImportError as ie:
            log.warning(f"Módulos não disponíveis: {ie}")
            
            # Resposta simulada
            result = {
                "success": True,
                "message": "Arquivos recebidos (modo demonstração)",
                "note": "Configure PYTHONPATH para execução real",
                "timestamp": datetime.now().isoformat(),
                "files": {
                    "config": config_file.filename,
                    "data": data_file.filename
                },
                "config_fields": list(config_data.keys()),
                "data_fields": list(data_json.keys()),
                "type": config_data.get('Type', data_json.get('Type', 'unknown'))
            }
            
            # Salva resultado em arquivo
            ctx = result.get('_context')
            output_file = save_result_to_file(result, output_format, config_file.filename, ctx)
            result['output_file'] = str(output_file)
            result['output_filename'] = output_file.name
            
            # Remove context antes de retornar
            result.pop('_context', None)
            
            if output_format == 'txt':
                return generate_txt_report(result), 200, {'Content-Type': 'text/plain; charset=utf-8'}
            else:
                return jsonify(result), 200
    
    except json.JSONDecodeError as e:
        return jsonify({
            "success": False,
            "error": f"JSON inválido: {str(e)}"
        }), 400
    
    except Exception as e:
        log.error(f"Erro ao processar arquivos: {e}")
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


def generate_txt_report(result: dict) -> str:
    """Gera relatório em formato TXT"""
    lines = []
    lines.append("="*80)
    lines.append("RELATÓRIO DE PALETIZAÇÃO")
    lines.append("="*80)
    lines.append("")
    lines.append(f"Timestamp: {result.get('timestamp', 'N/A')}")
    lines.append(f"Status: {'SUCESSO' if result.get('success') else 'ERRO'}")
    
    if 'type' in result:
        result_type = str(result['type']).upper() if result['type'] else 'N/A'
        lines.append(f"Tipo: {result_type}")
    
    if 'files' in result:
        lines.append("")
        lines.append("Arquivos processados:")
        lines.append(f"  - Config: {result['files'].get('config', 'N/A')}")
        lines.append(f"  - Data:   {result['files'].get('data', 'N/A')}")
    
    if 'statistics' in result:
        stats = result['statistics']
        lines.append("")
        lines.append("-"*80)
        lines.append("ESTATÍSTICAS")
        lines.append("-"*80)
        lines.append(f"Total de Mounted Spaces: {stats.get('total_mounted_spaces', 0)}")
        lines.append(f"Total de Orders:         {stats.get('total_orders', 0)}")
        lines.append(f"Total de Produtos:       {stats.get('total_products', 0)}")
        lines.append(f"Ocupação Média:          {stats.get('average_occupation', 0):.2f}%")
    
    if 'mounted_spaces' in result and result['mounted_spaces']:
        lines.append("")
        lines.append("-"*80)
        lines.append("MOUNTED SPACES")
        lines.append("-"*80)
        lines.append("")
        lines.append(f"{'#':<4} {'Lado':<6} {'Baia':<6} {'Ocupação':<12} {'Produtos':<10} {'Containers':<10}")
        lines.append("-"*80)
        
        for i, ms in enumerate(result['mounted_spaces'], 1):
            lines.append(
                f"{i:<4} "
                f"{ms.get('side', 'N/A'):<6} "
                f"{str(ms.get('bay', 'N/A')):<6} "
                f"{ms.get('occupation', 0):>10.2f}% "
                f"{ms.get('products_count', 0):<10} "
                f"{ms.get('containers', 0):<10}"
            )
    
    if 'message' in result:
        lines.append("")
        lines.append("-"*80)
        lines.append(f"Mensagem: {result['message']}")
    
    if 'note' in result:
        lines.append(f"Nota: {result['note']}")
    
    lines.append("")
    lines.append("="*80)
    
    return "\n".join(lines)


def save_result_to_file(result: dict, format: str, source_filename: str, context=None) -> Path:
    """
    Salva resultado em arquivo na pasta out
    
    Args:
        result: Resultado da paletização
        format: 'json' ou 'txt'
        source_filename: Nome do arquivo de origem
        context: Context da paletização (opcional, necessário para TXT)
        
    Returns:
        Path do arquivo salvo
    """
    try:
        # Gera nome do arquivo de saída
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = Path(source_filename).stem
        
        if format == 'txt':
            # Usa o adaptador oficial para gerar TXT no formato correto
            if context is not None:
                try:
                    from adapters.palletize_text_report import PalletizeTextReport
                    output_path = PalletizeTextReport.save_text(context, MAPAS_OUT_DIR)
                    log.info(f"Resultado TXT salvo em: {output_path}")
                    return Path(output_path)
                except Exception as e:
                    log.warning(f"Erro ao usar PalletizeTextReport: {e}")
            
            # Fallback: usa formato simplificado
            output_filename = f"{base_name}_result_{timestamp}.txt"
            output_path = MAPAS_OUT_DIR / output_filename
            txt_content = generate_txt_report(result)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(txt_content)
        else:
            output_filename = f"{base_name}_result_{timestamp}.json"
            output_path = MAPAS_OUT_DIR / output_filename
            
            # Salva JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        log.info(f"Resultado salvo em: {output_path}")
        return output_path
    
    except Exception as e:
        log.error(f"Erro ao salvar resultado: {e}")
        return None


@app.route('/mapas/list', methods=['GET'])
def list_mapas():
    """
    Lista arquivos JSON disponíveis na pasta de mapas
    
    Returns:
        JSON com lista de arquivos
    """
    try:
        if not MAPAS_DIR.exists():
            return jsonify({
                "success": False,
                "error": f"Diretório não encontrado: {MAPAS_DIR}",
                "note": "Crie o diretório ou ajuste MAPAS_DIR no código"
            }), 404
        
        # Lista arquivos JSON
        json_files = sorted(MAPAS_DIR.glob("*.json"))
        
        files_info = []
        for file_path in json_files:
            try:
                stat = file_path.stat()
                files_info.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                log.warning(f"Erro ao ler info de {file_path.name}: {e}")
        
        return jsonify({
            "success": True,
            "directory": str(MAPAS_DIR),
            "total_files": len(files_info),
            "files": files_info
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/mapas/outputs', methods=['GET'])
def list_outputs():
    """
    Lista arquivos de saída gerados no diretório out
    
    Returns:
        JSON com lista de arquivos de resultado
    """
    try:
        if not MAPAS_OUT_DIR.exists():
            return jsonify({
                "success": False,
                "error": f"Diretório não encontrado: {MAPAS_OUT_DIR}",
                "note": "Nenhum processamento realizado ainda"
            }), 404
        
        # Lista todos os arquivos (JSON e TXT)
        all_files = sorted(MAPAS_OUT_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        files_info = []
        for file_path in all_files:
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    files_info.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "extension": file_path.suffix,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception as e:
                    log.warning(f"Erro ao ler info de {file_path.name}: {e}")
        
        return jsonify({
            "success": True,
            "directory": str(MAPAS_OUT_DIR),
            "total_files": len(files_info),
            "files": files_info
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/mapas/process/<filename>', methods=['POST'])
def process_mapa_single(filename):
    """
    Processa um arquivo específico da pasta de mapas
    
    Args:
        filename: Nome do arquivo JSON
        
    Query params:
        format: 'json' ou 'txt' (padrão: json)
        data_file: Nome do segundo arquivo (opcional)
        
    Returns:
        Resultado da paletização
    """
    try:
        output_format = request.args.get('format', 'json').lower()
        data_filename = request.args.get('data_file', None)
        
        config_path = MAPAS_DIR / filename
        
        if not config_path.exists():
            return jsonify({
                "success": False,
                "error": f"Arquivo não encontrado: {filename}",
                "directory": str(MAPAS_DIR)
            }), 404
        
        # Se data_file não foi especificado, usa o mesmo arquivo
        if data_filename:
            data_path = MAPAS_DIR / data_filename
            if not data_path.exists():
                return jsonify({
                    "success": False,
                    "error": f"Arquivo data não encontrado: {data_filename}"
                }), 404
        else:
            data_path = config_path
        
        log.info(f"Processando: config={filename}, data={data_path.name}")
        
        # Lê arquivos
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
        
        # Processa
        result = process_palletization(config_data, data_json, config_path.name, data_path.name)
        
        # Salva resultado em arquivo
        ctx = result.get('_context')
        output_file = save_result_to_file(result, output_format, filename, ctx)
        if output_file:
            result['output_file'] = str(output_file)
            result['output_filename'] = output_file.name
        
        # Remove context antes de retornar (não é serializável)
        result.pop('_context', None)
        
        # Retorna em formato solicitado
        if output_format == 'txt':
            txt_content = generate_txt_report(result)
            return txt_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            return jsonify(result), 200
    
    except json.JSONDecodeError as e:
        return jsonify({
            "success": False,
            "error": f"JSON inválido: {str(e)}"
        }), 400
    
    except Exception as e:
        log.error(f"Erro ao processar {filename}: {e}")
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/mapas/process-auto', methods=['POST'])
def process_mapa_auto():
    """
    Busca e processa automaticamente pares de arquivos (config + data)
    
    Body:
        {
            "pattern": "padrão para buscar arquivos",
            "config_pattern": "padrão específico para config",
            "data_pattern": "padrão específico para data",
            "format": "json" ou "txt"
        }
        
    Returns:
        Resultado da paletização
    """
    try:
        data = request.get_json() or {}
        
        pattern = data.get('pattern', '*.json')
        config_pattern = data.get('config_pattern', '*config*.json')
        data_pattern = data.get('data_pattern', '*data*.json')
        output_format = data.get('format', 'json').lower()
        
        if not MAPAS_DIR.exists():
            return jsonify({
                "success": False,
                "error": f"Diretório não encontrado: {MAPAS_DIR}"
            }), 404
        
        # Busca arquivos
        config_files = sorted(MAPAS_DIR.glob(config_pattern))
        data_files = sorted(MAPAS_DIR.glob(data_pattern))
        
        if not config_files:
            return jsonify({
                "success": False,
                "error": f"Nenhum arquivo de config encontrado com padrão: {config_pattern}",
                "directory": str(MAPAS_DIR)
            }), 404
        
        # Usa o primeiro arquivo encontrado de cada
        config_path = config_files[0]
        data_path = data_files[0] if data_files else config_path
        
        log.info(f"Auto-processando: config={config_path.name}, data={data_path.name}")
        
        # Lê arquivos
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
        
        # Processa
        result = process_palletization(config_data, data_json, config_path.name, data_path.name)
        
        # Salva resultado em arquivo
        ctx = result.get('_context')
        output_file = save_result_to_file(result, output_format, config_path.name, ctx)
        result['output_file'] = str(output_file)
        result['output_filename'] = output_file.name
        
        # Remove context antes de retornar (não é serializável)
        result.pop('_context', None)
        
        # Retorna em formato solicitado
        if output_format == 'txt':
            return generate_txt_report(result), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            return jsonify(result), 200
    
    except Exception as e:
        log.error(f"Erro no processamento automático: {e}")
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


def process_palletization(config_data: dict, data_json: dict, config_name: str, data_name: str) -> dict:
    """
    Função auxiliar para processar paletização
    
    Args:
        config_data: Dados de configuração
        data_json: Dados de entrada
        config_name: Nome do arquivo de config
        data_name: Nome do arquivo de data
        
    Returns:
        Resultado da paletização
    """
    try:
        from service.calculator_palletizing_service import CalculatorPalletizingService
        from domain.context import Context
        
        log.info("Criando contexto...")
        
        # Salva temporariamente os arquivos
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_config:
            json.dump(config_data, tmp_config)
            tmp_config_path = tmp_config.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_data:
            json.dump(data_json, tmp_data)
            tmp_data_path = tmp_data.name
        
        try:
            # Cria contexto com os arquivos
            context = Context(config_path=tmp_config_path, json_path=tmp_data_path)
            
            context_type = getattr(context, 'Type', 'route').lower()
            log.info(f"Tipo detectado: {context_type}")
            
            # Inicializa serviço
            service = CalculatorPalletizingService()
            
            # Executa cadeias apropriadas
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
            
            # Common chain sempre no final
            context = service.execute_chain(service.common_chain, context)
            
            # Prepara resultado
            mounted_spaces = []
            total_products = 0
            total_occupation = 0.0
            
            if hasattr(context, 'MountedSpaces') and context.MountedSpaces:
                for ms in context.MountedSpaces:
                    products_count = sum(len(c.Products) for c in ms.Containers)
                    total_products += products_count
                    
                    occupation = getattr(ms, 'Occupation', 0)
                    total_occupation += occupation
                    
                    ms_data = {
                        "side": getattr(ms.Space, 'Side', 'N/A'),
                        "bay": getattr(ms.Space, 'Number', 'N/A'),
                        "occupation": occupation,
                        "products_count": products_count,
                        "containers": len(ms.Containers)
                    }
                    mounted_spaces.append(ms_data)
            
            avg_occupation = total_occupation / len(context.MountedSpaces) if context.MountedSpaces else 0
            
            result = {
                "success": True,
                "message": "Paletização executada com sucesso",
                "timestamp": datetime.now().isoformat(),
                "type": context_type,
                "files": {
                    "config": config_name,
                    "data": data_name
                },
                "statistics": {
                    "total_mounted_spaces": len(context.MountedSpaces) if hasattr(context, 'MountedSpaces') else 0,
                    "total_orders": len(context.orders) if hasattr(context, 'orders') else 0,
                    "total_products": total_products,
                    "average_occupation": avg_occupation
                },
                "mounted_spaces": mounted_spaces,
                "_context": context  # Adiciona context para geração de TXT
            }
            
            # Remove arquivos temporários
            os.unlink(tmp_config_path)
            os.unlink(tmp_data_path)
            
            return result
        
        finally:
            # Garante limpeza dos arquivos temporários
            try:
                if os.path.exists(tmp_config_path):
                    os.unlink(tmp_config_path)
                if os.path.exists(tmp_data_path):
                    os.unlink(tmp_data_path)
            except:
                pass
    
    except ImportError as ie:
        log.warning(f"Módulos não disponíveis: {ie}")
        
        # Resposta simulada
        return {
            "success": True,
            "message": "Arquivos processados (modo demonstração)",
            "note": "Configure PYTHONPATH para execução real",
            "timestamp": datetime.now().isoformat(),
            "files": {
                "config": config_name,
                "data": data_name
            },
            "config_fields": list(config_data.keys()),
            "data_fields": list(data_json.keys()),
            "type": config_data.get('Type', data_json.get('Type', 'unknown'))
        }


def get_chains_for_type(context_type: str) -> list:
    """Retorna lista de cadeias a serem executadas para o tipo"""
    chains = []
    
    if context_type in ['route', 'mixed']:
        chains.extend(['principal_route_chain', 'route_chain'])
    
    if context_type == 'as' or context_type == 'mixed':
        chains.append('as_chain')
    
    if context_type == 'mixed':
        chains.append('mixed_chain')
    
    if context_type == 'crossdocking':
        chains.append('crossdocking_chain')
    
    if context_type == 't4':
        chains.append('t4_chain')
    
    chains.append('common_chain')
    
    return chains


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint não encontrado",
        "available": [
            "/", 
            "/health", 
            "/validate", 
            "/palletize", 
            "/palletize/files",
            "/mapas/list",
            "/mapas/process/<filename>",
            "/mapas/process-auto"
        ]
    }), 404


def main():
    print("="*80)
    print("API DE PALETIZAÇÃO - SERVIDOR SIMPLIFICADO")
    print("="*80)
    print()
    print("Servidor iniciando em http://localhost:5000")
    print(f"Pasta de mapas: {MAPAS_DIR}")
    print(f"Pasta existe: {'✓' if MAPAS_DIR.exists() else '✗'}")
    print()
    print("Endpoints:")
    print("  GET  /                      - Documentação")
    print("  GET  /health                - Health check")
    print("  GET  /mapas/list            - Listar arquivos disponíveis")
    print("  POST /mapas/process/<file>  - Processar arquivo específico")
    print("  POST /mapas/process-auto    - Processar automaticamente")
    print("  POST /validate              - Validar JSON")
    print("  POST /palletize             - Executar paletização (JSON)")
    print("  POST /palletize/files       - Executar paletização (upload)")
    print()
    print("Testes rápidos:")
    print("  # Listar arquivos na pasta de mapas")
    print("  curl http://localhost:5000/mapas/list")
    print()
    print("  # Processar arquivo específico (retorna TXT)")
    print("  curl -X POST 'http://localhost:5000/mapas/process/config.json?format=txt'")
    print()
    print("  # Processar automaticamente (busca arquivos)")
    print("  curl -X POST http://localhost:5000/mapas/process-auto \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"format\":\"txt\"}'")
    print()
    print("  # Upload de 2 arquivos")
    print("  curl -X POST http://localhost:5000/palletize/files \\")
    print("    -F 'config_file=@config.json' \\")
    print("    -F 'data_file=@data.json' \\")
    print("    -F 'format=txt'")
    print()
    print("="*80)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
