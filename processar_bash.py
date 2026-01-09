#!/usr/bin/env python3
"""
Processador em Massa via Bash - Usa WSL
Chama o script bash que já funciona
"""

import os
import subprocess
import time
from pathlib import Path

# Configurações
INPUT_DIR = Path("C:/prd_debian/meus_xmls")
OUTPUT_DIR = Path("C:/prd_debian/mapas/out/processamento_massa")
SUCCESS_DIR = OUTPUT_DIR / "sucesso"
ERROR_DIR = OUTPUT_DIR / "erro"

# Criar diretórios
SUCCESS_DIR.mkdir(parents=True, exist_ok=True)
ERROR_DIR.mkdir(parents=True, exist_ok=True)

def main():
    # Listar XMLs
    xml_files = sorted(INPUT_DIR.glob("*.xml"))
    total = len(xml_files)
    
    if total == 0:
        print(f"ERRO: Nenhum XML encontrado em {INPUT_DIR}")
        return
    
    print("=" * 80)
    print(f"PROCESSAMENTO VIA BASH - {total} XMLs MAPA")
    print("=" * 80)
    print(f"Entrada: {INPUT_DIR}")
    print(f"Saida: {SUCCESS_DIR}")
    print("=" * 80)
    print()
    
    # Executar script bash
    inicio = time.time()
    
    result = subprocess.run(
        ["bash", "/mnt/c/prd_debian/scripts/PROCESSAR_TODOS_AGORA.sh"],
        cwd="/mnt/c/prd_debian",
        capture_output=False,  # Mostra output em tempo real
        text=True
    )
    
    # Tempo total
    tempo_total = time.time() - inicio
    minutos = int(tempo_total / 60)
    segundos = int(tempo_total % 60)
    
    # Contar resultados
    sucesso = len(list(SUCCESS_DIR.glob("*.txt")))
    erro = total - sucesso
    
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
