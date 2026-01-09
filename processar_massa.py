#!/usr/bin/env python3
"""Processa todos os XMLs MAPA da pasta meus_xmls"""
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Configurações
BASE_DIR = Path(r"C:\prd_debian")
XML_DIR = BASE_DIR / "meus_xmls"
OUT_DIR = BASE_DIR / "mapas" / "out" / "processamento_massa" / "sucesso"
ERR_DIR = BASE_DIR / "mapas" / "out" / "processamento_massa" / "erro"
CONFIG_JSON = BASE_DIR / "mapas" / "in" / "config.json"
INPUT_JSON = BASE_DIR / "mapas" / "in" / "input.json"

# Criar pastas
OUT_DIR.mkdir(parents=True, exist_ok=True)
ERR_DIR.mkdir(parents=True, exist_ok=True)

def processar_xml(xml_path: Path):
    """Processa um XML: converte -> gera config -> paletiza -> TXT"""
    try:
        # 1. Converter XML -> JSON
        result = subprocess.run([
            "python", str(BASE_DIR / "wms_converter" / "convert.py"),
            "-i", str(xml_path),
            "-o", str(INPUT_JSON)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0 or not INPUT_JSON.exists():
            return False, "Conversão falhou"
        
        # 2. Gerar config.json
        subprocess.run([
            "python", "-c",
            f"import json; f=open(r'{INPUT_JSON}'); d=json.load(f); w=d['Warehouse']['UnbCode']; "
            f"c=open(r'{CONFIG_JSON}','w'); json.dump({{'Settings':{{'UseBaySmallerThan35':'False','KegExclusivePallet':'False','IncludeTopOfPallet':'True','MinimumOccupationPercentage':'0','AllowEmptySpaces':'False','AllowVehicleWithoutBays':'False','DistributeItemsOnEmptySpaces':'False','MinimumQuantityOfSKUsToDistributeOnEmptySpaces':'0'}}}}, c)"
        ], timeout=5, check=True)
        
        # 3. Paletizar
        result = subprocess.run([
            "python", str(BASE_DIR / "ocp_wms_core" / "ocp_score-main" / "run.py"),
            "-ij", str(INPUT_JSON),
            "-cj", str(CONFIG_JSON),
            "-o", str(OUT_DIR / f"{xml_path.stem}.txt")
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return False, f"Paletização falhou: {result.stderr[:100]}"
        
        return True, "OK"
        
    except Exception as e:
        return False, str(e)[:100]


def main():
    # Pegar apenas XMLs MAPA
    xmls = sorted([x for x in XML_DIR.glob("*.xml") if "_m_mapa_" in x.name.lower()])
    total = len(xmls)
    
    print(f"{'='*70}")
    print(f"  PROCESSAMENTO EM MASSA - {total} XMLs MAPA")
    print(f"{'='*70}\n")
    
    sucesso = 0
    erro = 0
    inicio = datetime.now()
    
    for i, xml in enumerate(xmls, 1):
        ok, msg = processar_xml(xml)
        status = "OK" if ok else "FAIL"
        print(f"[{i:5}/{total}] {status:4} {xml.name[:55]:<55}")
        
        if ok:
            sucesso += 1
        else:
            erro += 1
        
        if i % 100 == 0:
            elapsed = (datetime.now() - inicio).total_seconds()
            rate = i / elapsed
            remaining = (total - i) / rate / 60
            print(f"          Velocidade: {rate:.1f} xml/s | Resta: ~{remaining:.0f} min\n")
    
    tempo = (datetime.now() - inicio).total_seconds()
    print(f"\n{'='*70}")
    print(f"  CONCLUIDO")
    print(f"{'='*70}")
    print(f"  [OK] Sucesso: {sucesso} ({sucesso/total*100:.1f}%)")
    print(f"  [X]  Erro:    {erro} ({erro/total*100:.1f}%)")
    print(f"  Tempo:       {tempo/60:.1f} min")
    print(f"\nPasta: {OUT_DIR}\n")


if __name__ == "__main__":
    main()
