#!/usr/bin/env python3
"""
Processador em Massa via API Master Orchestrator
Envia XMLs para http://localhost:9000/process-xml-file
"""

import os
import sys
import time
import requests
from pathlib import Path

# Configurações
API_URL = "http://localhost:9000/process-xml-file"
INPUT_DIR = Path("C:/prd_debian/meus_xmls")
OUTPUT_DIR = Path("C:/prd_debian/mapas/out/processamento_massa")
SUCCESS_DIR = OUTPUT_DIR / "sucesso"
ERROR_DIR = OUTPUT_DIR / "erro"

# Criar diretórios
SUCCESS_DIR.mkdir(parents=True, exist_ok=True)
ERROR_DIR.mkdir(parents=True, exist_ok=True)

def processar_xml(xml_path):
    """Processa um XML via API Master Orchestrator"""
    try:
        with open(xml_path, 'rb') as f:
            files = {'file': (xml_path.name, f, 'application/xml')}
            response = requests.post(API_URL, files=files, timeout=120)
        
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    
    except Exception as e:
        return False, str(e)

def main():
    # Listar XMLs
    xml_files = sorted(INPUT_DIR.glob("*.xml"))
    total = len(xml_files)
    
    if total == 0:
        print(f"ERRO: Nenhum XML encontrado em {INPUT_DIR}")
        return
    
    print("=" * 80)
    print(f"PROCESSAMENTO EM MASSA VIA API - {total} XMLs MAPA")
    print("=" * 80)
    print(f"API: {API_URL}")
    print(f"Entrada: {INPUT_DIR}")
    print(f"Saida Sucesso: {SUCCESS_DIR}")
    print(f"Saida Erro: {ERROR_DIR}")
    print("=" * 80)
    print()
    
    # Estatísticas
    sucesso = 0
    erro = 0
    inicio = time.time()
    
    for i, xml_path in enumerate(xml_files, 1):
        # Nome do arquivo TXT de saída
        txt_name = xml_path.stem + ".txt"
        
        # Processar
        ok, resultado = processar_xml(xml_path)
        
        if ok:
            # Salvar TXT
            txt_path = SUCCESS_DIR / txt_name
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(resultado)
            
            sucesso += 1
            status = "OK"
        else:
            # Salvar erro
            err_path = ERROR_DIR / (xml_path.stem + ".err")
            with open(err_path, 'w', encoding='utf-8') as f:
                f.write(resultado)
            
            erro += 1
            status = "FAIL"
        
        # Estatísticas
        elapsed = time.time() - inicio
        rate = i / elapsed if elapsed > 0 else 0
        remaining = (total - i) / rate if rate > 0 else 0
        
        print(f"[{i:4d}/{total}] {status:4s} | {xml_path.name[:55]:55s} | "
              f"{rate:4.1f} xml/s | Resta: ~{int(remaining/60):2d}min")
    
    # Resumo final
    tempo_total = time.time() - inicio
    minutos = int(tempo_total / 60)
    segundos = int(tempo_total % 60)
    
    print()
    print("=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print(f"  Total:    {total:4d}")
    print(f"  Sucesso:  {sucesso:4d} ({sucesso*100/total:.1f}%)")
    print(f"  Erro:     {erro:4d} ({erro*100/total:.1f}%)")
    print(f"  Tempo:    {minutos}m {segundos}s")
    print("=" * 80)
    print(f"\nArquivos TXT em: {SUCCESS_DIR}")

if __name__ == "__main__":
    main()
