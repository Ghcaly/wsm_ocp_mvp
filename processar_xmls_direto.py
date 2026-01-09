#!/usr/bin/env python3
"""
Processa XMLs diretamente sem depender de APIs/serviços externos
Converte XML → JSON → Paletiza → Gera TXT
"""

import subprocess
import sys
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

BASE_DIR = Path(__file__).resolve().parent
XML_INPUT_DIR = Path("C:/mapas_xml_saidas/last_5_days")
OUTPUT_DIR = BASE_DIR / "mapas" / "out" / "processamento_massa" / "sucesso"
ERROR_DIR = BASE_DIR / "mapas" / "out" / "processamento_massa" / "erro"
TEMP_DIR = BASE_DIR / "mapas" / "in"

# Criar diretórios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ERROR_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def extract_mapa_number(filename):
    """Extrai número do mapa do arquivo"""
    import re
    match = re.search(r'mapa_(\d+)', filename)
    return match.group(1) if match else "unknown"

def processar_xml(xml_file):
    """Processa um único XML: converte e paletiza"""
    filename = xml_file.stem
    mapa_num = extract_mapa_number(filename)
    
    try:
        # 1. Converter XML para JSON
        json_temp = TEMP_DIR / f"input_{mapa_num}.json"
        cmd_convert = [
            "python", str(BASE_DIR / "wms_converter" / "convert.py"),
            "-i", str(xml_file),
            "-o", str(json_temp)
        ]
        
        result = subprocess.run(cmd_convert, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return (filename, False, "Erro na conversão")
        
        if not json_temp.exists():
            return (filename, False, "JSON não gerado")
        
        # 2. Criar config mínimo
        config_temp = TEMP_DIR / f"config_{mapa_num}.json"
        config = {
            "warehouse": "916",
            "delivery_date": "2026-01-05"
        }
        with open(config_temp, "w") as f:
            json.dump(config, f)
        
        # 3. Preparar diretório de trabalho
        work_dir = BASE_DIR / "ocp_wms_core" / "ocp_score-main" / "data" / "route" / mapa_num
        work_dir.mkdir(parents=True, exist_ok=True)
        output_dir = work_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Copiar arquivos
        import shutil
        shutil.copy(json_temp, work_dir / "input.json")
        shutil.copy(config_temp, work_dir / "config.json")
        
        # 4. Executar paletização
        os.environ["PYTHONPATH"] = str(BASE_DIR / "ocp_wms_core" / "ocp_score-main")
        cmd_process = [
            "python", "-m", "service.palletizing_processor"
        ]
        
        result = subprocess.run(
            cmd_process,
            cwd=str(BASE_DIR / "ocp_wms_core"),
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "MAPA_NUM": mapa_num}
        )
        
        # 5. Verificar TXT gerado
        txt_files = list(output_dir.glob("*.txt"))
        if txt_files:
            txt_file = txt_files[0]
            output_txt = OUTPUT_DIR / f"{filename}.txt"
            shutil.copy(txt_file, output_txt)
            
            # Limpar temporários
            json_temp.unlink(missing_ok=True)
            config_temp.unlink(missing_ok=True)
            
            return (filename, True, f"TXT: {output_txt.name}")
        else:
            return (filename, False, "TXT não gerado")
            
    except subprocess.TimeoutExpired:
        return (filename, False, "Timeout")
    except Exception as e:
        return (filename, False, f"Erro: {str(e)[:50]}")

def main():
    print("="*70)
    print("   PROCESSAMENTO DIRETO - XMLs -> TXTs")
    print("="*70 + "\n")
    
    # Listar XMLs
    xml_files = list(XML_INPUT_DIR.glob("*.xml"))
    if not xml_files:
        print(f"❌ Nenhum XML encontrado em {XML_INPUT_DIR}")
        sys.exit(1)
    
    total = len(xml_files)
    print(f"📊 Total de XMLs: {total}")
    print(f"📁 Entrada: {XML_INPUT_DIR}")
    print(f"📁 Saída: {OUTPUT_DIR}\n")
    
    # Processar em paralelo (4 workers)
    print("🚀 Processando...\n")
    
    sucesso = 0
    erros = 0
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(processar_xml, xml): xml for xml in xml_files}
        
        for i, future in enumerate(as_completed(futures), 1):
            filename, success, msg = future.result()
            
            if success:
                sucesso += 1
                status = "✅"
            else:
                erros += 1
                status = "❌"
            
            if i % 50 == 0 or not success:
                print(f"[{i}/{total}] {status} {filename[:60]}")
    
    print("\n" + "="*80)
    print("📊 RESULTADOS FINAIS")
    print("="*80)
    print(f"✅ Sucesso: {sucesso}")
    print(f"❌ Erros: {erros}")
    print(f"📈 Taxa: {(sucesso/total*100):.1f}%\n")
    print(f"📁 TXTs gerados em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
