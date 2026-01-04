# debug_mapa_runner.py - Runner completo para debugar mapa específico

"""
Script runner completo para debugar um mapa específico.
Simula o fluxo do processar_massa_simples.sh:

FLUXO COMPLETO:
1. Converte XML → JSON (via API Converter)
2. Aplica Boxing/Marketplace (apply_boxing.py)
3. Gera config.json (via config_generator.py)
4. Executa paletização com todas as rules (via palletizing_processor)
5. Gera TXT final
6. Valida marcações BinPack

USO:
    1. Configure MAPA_NUM abaixo
    2. Adicione breakpoints nos arquivos que quer debugar:
       - apply_boxing.py → para debugar boxing
       - ocp_wms_core/ocp_score-main/service/palletizing_processor.py
       - ocp_wms_core/ocp_score-main/rules/route/*.py
    3. Pressione F5
"""

import sys
import os
from pathlib import Path
import logging
import runpy

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

MAPA_NUM = 622704
XML_PATH = None  # Será detectado automaticamente baseado no MAPA_NUM

# Paths
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR
OCP_DIR = BASE_DIR / "ocp_wms_core" / "ocp_score-main"
MAPAS_IN = BASE_DIR / "mapas" / "in"
MAPAS_OUT = BASE_DIR / "mapas" / "out"
XML_DIR = MAPAS_IN / "xml"  # Diretório com XMLs

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def buscar_xml_por_mapa(mapa_num: int) -> Path:
    """
    Busca XML automaticamente baseado no número do mapa.
    Procura em mapas/in/xml/ por arquivo contendo m_mapa_{MAPA_NUM}_
    """
    xml_dir = XML_DIR
    
    if not xml_dir.exists():
        raise FileNotFoundError(f"Diretório XML não encontrado: {xml_dir}")
    
    # Padrão: *m_mapa_{MAPA_NUM}_*.xml
    pattern = f"*m_mapa_{mapa_num}_*.xml"
    xml_files = list(xml_dir.glob(pattern))
    
    if not xml_files:
        raise FileNotFoundError(
            f"XML não encontrado para mapa {mapa_num}\n"
            f"Procurado em: {xml_dir}\n"
            f"Padrão: {pattern}"
        )
    
    if len(xml_files) > 1:
        logger.warning(f"Múltiplos XMLs encontrados para mapa {mapa_num}, usando o primeiro:")
        for xml in xml_files:
            logger.warning(f"  - {xml.name}")
    
    return xml_files[0]


def instalar_dependencias():
    """Instala dependências necessárias"""
    import subprocess
    
    # Verifica se multipledispatch está instalado
    try:
        import multipledispatch
        return  # Já instalado
    except ImportError:
        pass
    
    logger.info("Instalando dependências Python...")
    
    # Procura requirements.txt
    requirements_paths = [
        OCP_DIR / "requirements.txt",
        OCP_DIR / "src" / "requirements.txt",
        BASE_DIR / "requirements.txt"
    ]
    
    for req_path in requirements_paths:
        if req_path.exists():
            logger.info(f"Instalando de {req_path}")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_path)],
                check=False
            )
            logger.info("✓ Dependências instaladas")
            return
    
    # Se não achar requirements, instala as principais
    logger.info("Instalando pacotes essenciais...")
    packages = [
        "multipledispatch",
        "pandas",
        "openpyxl",
        "requests"
    ]
    subprocess.run(
        [sys.executable, "-m", "pip", "install"] + packages,
        check=False
    )
    logger.info("✓ Pacotes instalados")


def preparar_arquivos():
    """Prepara arquivos necessários - FLUXO COMPLETO"""
    logger.info("=" * 80)
    logger.info(f"🐛 Preparando debug do mapa {MAPA_NUM}")
    logger.info("=" * 80)
    logger.info("")
    
    MAPAS_IN.mkdir(parents=True, exist_ok=True)
    MAPAS_OUT.mkdir(parents=True, exist_ok=True)
    
    # PASSO 1: XML → JSON (via Converter API)
    json_path = MAPAS_IN / "inputcompleto.json"
    
    # Busca XML automaticamente se não foi especificado
    xml_path = None
    if XML_PATH:
        xml_path = Path(XML_PATH)
        if not xml_path.exists():
            raise FileNotFoundError(f"XML especificado não encontrado: {xml_path}")
    else:
        # Busca automaticamente baseado no número do mapa
        try:
            xml_path = buscar_xml_por_mapa(MAPA_NUM)
            logger.info(f"📁 XML detectado automaticamente: {xml_path.name}")
        except FileNotFoundError as e:
            # Se não encontrar, tenta usar JSON existente
            if json_path.exists():
                logger.info(f"⚠️  {e}")
                logger.info(f"📄 Usando JSON existente: {json_path}")
                xml_path = None
            else:
                raise
    
    if xml_path and xml_path.exists():
        logger.info("")
        logger.info("📄 PASSO 1: Convertendo XML → JSON")
        logger.info(f"  XML: {xml_path.name}")
        
        import requests
        import json
        
        try:
            with open(xml_path, 'rb') as f:
                response = requests.post(
                    "http://localhost:8002/convert", 
                    files={'file': f},
                    timeout=30
                )
            
            if response.status_code == 200:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(response.json(), f, indent=2, ensure_ascii=False)
                logger.info(f"  ✓ JSON salvo: {json_path}")
            else:
                raise Exception(f"Converter retornou erro: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            logger.error("  ❌ Converter não está rodando!")
            logger.error("  Inicie com: cd wms_converter && python api.py")
            raise
    else:
        if not json_path.exists():
            raise FileNotFoundError(
                f"Nenhuma fonte de dados encontrada!\n"
                f"- XML não encontrado em: {XML_DIR}\n"
                f"- JSON não encontrado: {json_path}\n"
                f"Certifique-se de ter o XML em mapas/in/xml/ ou JSON em mapas/in/"
            )
        logger.info("")
        logger.info(f"📄 PASSO 1: Usando JSON existente: {json_path.name}")
    
    logger.info("")
    
    # PASSO 2: Boxing/Marketplace (apply_boxing.py)
    logger.info("📦 PASSO 2: Aplicando Boxing/Marketplace")
    logger.info("  Verificando produtos marketplace...")
    
    boxing_result_path = MAPAS_IN / "boxing_result.json"
    usou_boxing = False
    marketplace_count = 0
    
    # Adiciona BASE_DIR ao path para importar apply_boxing
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        import apply_boxing
        
        # 🔍 BREAKPOINT AQUI - Step Into (F11) para debugar boxing
        result = apply_boxing.apply_boxing(str(json_path), str(boxing_result_path))
        
        if result == 0 and boxing_result_path.exists():
            import json
            with open(boxing_result_path, 'r') as f:
                boxing_data = json.load(f)
            
            if boxing_data.get('success'):
                # Conta caixas e pacotes
                result_data = boxing_data.get('result', [{}])[0].get('result', {})
                boxes = result_data.get('boxes', [])
                packages = result_data.get('packages', [])
                
                boxes_count = len(boxes)
                packages_count = sum(p.get('quantity', 0) for p in packages)
                marketplace_count = boxes_count + packages_count
                
                logger.info(f"  ✓ Boxing aplicado com sucesso!")
                logger.info(f"    - Caixas: {boxes_count}")
                logger.info(f"    - Pacotes: {packages_count}")
                logger.info(f"    - Total itens marketplace: {marketplace_count}")
                usou_boxing = True
            else:
                logger.info("  ⚠️  Boxing retornou erro (continuando sem boxing)")
        else:
            logger.info("  ℹ️  Sem produtos marketplace detectados")
    
    except Exception as e:
        logger.warning(f"  ⚠️  Erro no boxing (continuando): {e}")
    
    logger.info("")
    
    # PASSO 3: Gerar config.json (via config_generator.py)
    logger.info("⚙️  PASSO 3: Gerando configuração")
    config_path = MAPAS_IN / "config_completo.json"
    
    try:
        # Muda para o diretório do OCP temporariamente
        original_cwd = os.getcwd()
        os.chdir(OCP_DIR)
        
        # Adiciona ao path
        if str(OCP_DIR) not in sys.path:
            sys.path.insert(0, str(OCP_DIR))
        
        # Importa e executa config_generator
        from service.config_generator import ConfigGenerator
        
        generator = ConfigGenerator(database_path=OCP_DIR / "database")
        generator.generate_config_file(
            input_file=json_path,
            output_file=config_path,
            overwrite=True
        )
        
        os.chdir(original_cwd)
        logger.info(f"  ✓ Config gerada: {config_path}")
    
    except Exception as e:
        os.chdir(original_cwd)
        logger.error(f"  ❌ Erro ao gerar config: {e}")
        raise
    
    logger.info("")
    logger.info("📋 Resumo da preparação:")
    logger.info(f"  ✓ Input JSON: {json_path}")
    logger.info(f"  ✓ Config: {config_path}")
    logger.info(f"  ✓ Boxing: {'SIM' if usou_boxing else 'NÃO'}")
    logger.info(f"  ✓ Produtos Marketplace: {marketplace_count}")
    logger.info(f"  ✓ Output: {MAPAS_OUT}")
    logger.info("")
    
    return config_path, json_path, usou_boxing, marketplace_count

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executa fluxo completo de processamento"""
    
    try:
        # Instala dependências primeiro
        instalar_dependencias()
        
        # PREPARAÇÃO: XML → JSON → Boxing → Config
        config_path, input_path, usou_boxing, marketplace_count = preparar_arquivos()
        
        # Define env var para o processor
        os.environ['MAPA_NUM'] = str(MAPA_NUM)
        
        # PASSO 4: Paletização (executa todas as rules)
        logger.info("=" * 80)
        logger.info("🚀 PASSO 4: Executando Paletização")
        logger.info("=" * 80)
        logger.info("👉 Adicione breakpoints nas rules que quer debugar!")
        logger.info("   Exemplos:")
        logger.info("   - rules/route/layer_rule.py")
        logger.info("   - rules/route/box_template_rule.py (boxing)")
        logger.info("   - rules/route/remount_rule.py")
        logger.info("")
        
        # Muda para o diretório PARENT do ocp_score-main
        original_cwd = os.getcwd()
        ocp_parent = OCP_DIR.parent  # ocp_wms_core
        os.chdir(ocp_parent)
        
        # Adiciona o parent ao path (não o ocp_score-main diretamente)
        sys.path.insert(0, str(ocp_parent))
        
        # Salva sys.argv
        old_argv = sys.argv.copy()
        sys.argv = ['palletizing_processor']
        
        try:
            # 🎯 EXECUTA PALLETIZAÇÃO
            # Breakpoints nos arquivos das rules/processor serão respeitados!
            runpy.run_module('ocp_score-main.service.palletizing_processor', run_name='__main__')
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ Paletização concluída!")
            logger.info("=" * 80)
            logger.info("")
            
        finally:
            sys.argv = old_argv
            os.chdir(original_cwd)
        
        # PASSO 5: Validação do TXT gerado
        logger.info("📊 PASSO 5: Validando resultado")
        logger.info("")
        
        txt_path = MAPAS_OUT / f"palletize_result_map_{MAPA_NUM}.txt"
        
        if txt_path.exists():
            with open(txt_path, 'r', encoding='utf-8') as f:
                txt_content = f.read()
            
            # Conta marcações BinPack
            binpack_count = txt_content.count("BinPack")
            
            logger.info("=" * 80)
            logger.info("📈 RESUMO FINAL")
            logger.info("=" * 80)
            logger.info(f"📄 Arquivo TXT: {txt_path.name}")
            logger.info(f"📦 Boxing aplicado: {'SIM' if usou_boxing else 'NÃO'}")
            logger.info(f"🏷️  Produtos marketplace detectados: {marketplace_count}")
            logger.info(f"✨ Marcações BinPack no TXT: {binpack_count}")
            logger.info("")
            
            if binpack_count > 0:
                logger.info("✅ MARKETPLACE PROCESSADO COM SUCESSO!")
                logger.info("")
                logger.info("Exemplos de linhas com BinPack:")
                
                lines_with_binpack = [line for line in txt_content.split('\n') if 'BinPack' in line]
                for i, line in enumerate(lines_with_binpack[:5], 1):
                    logger.info(f"  {i}. {line.strip()[:100]}")
            else:
                if marketplace_count > 0:
                    logger.warning("⚠️  Boxing foi aplicado mas não há marcações BinPack no TXT!")
                    logger.warning("    Possível problema na BoxTemplateRule")
                else:
                    logger.info("ℹ️  Sem produtos marketplace (comportamento esperado)")
            
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"✅ DEBUG CONCLUÍDO - TXT: {txt_path}")
            logger.info("=" * 80)
            
            return 0
        else:
            logger.error("=" * 80)
            logger.error("❌ ERRO: TXT não foi gerado!")
            logger.error("=" * 80)
            logger.error(f"Esperado: {txt_path}")
            logger.error("Verifique os logs acima para identificar o problema")
            return 1
    
    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ EXCEPTION DURANTE PROCESSAMENTO!")
        logger.error("=" * 80)
        logger.exception(e)
        return 1


if __name__ == "__main__":
    main()
