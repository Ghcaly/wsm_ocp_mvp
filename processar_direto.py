#!/usr/bin/env python3
"""
Processador em Massa - Chamada Direta aos Módulos Python
Não depende de APIs REST
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Configurações
INPUT_DIR = Path("C:/prd_debian/meus_xmls")
OUTPUT_DIR = Path("C:/prd_debian/mapas/out/processamento_massa")
SUCCESS_DIR = OUTPUT_DIR / "sucesso"
ERROR_DIR = OUTPUT_DIR / "erro"
WORK_DIR = Path("C:/prd_debian/mapas/in")

# Criar diretórios
SUCCESS_DIR.mkdir(parents=True, exist_ok=True)
ERROR_DIR.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)

# Paths
CONVERTER_PATH = Path("C:/prd_debian/wms_converter/convert.py")
OCP_ROOT = Path("C:/prd_debian/ocp_wms_core/ocp_score-main")

def processar_xml(xml_path):
    """Processa um XML MAPA"""
    try:
        # 1. Converter XML -> JSON
        json_path = WORK_DIR / "input.json"
        result = subprocess.run(
            ["python", str(CONVERTER_PATH), "-i", str(xml_path), "-o", str(json_path)],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0 or not json_path.exists():
            return False, f"Falha conversao: {result.stderr[:100]}"
        
        # 2. Extrair mapa_num do JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mapa_num = data.get('Number', data.get('MapNumber', 'unknown'))
        warehouse = data.get('Warehouse', {}).get('UnbCode', '916')
        
        # 3. Criar config.json
        config = {
            "Settings": {
                "UseBaySmallerThan35": "False",
                "KegExclusivePallet": "False",
                "IncludeTopOfPallet": "True",
                "MinimumOccupationPercentage": "0",
                "AllowEmptySpaces": "False",
                "AllowVehicleWithoutBays": "False",
                "DistributeItemsOnEmptySpaces": "False",
                "MinimumQuantityOfSKUsToDistributeOnEmptySpaces": "0",
                "AdjustReassemblesAfterWater": "False",
                "JoinDisposableContainers": "False",
                "OccupationToJoinMountedSpaces": "0",
                "OrderByItemsSequence": "False",
                "OrderPalletByProductGroup": "False",
                "OrderProductsForAutoServiceMap": "False",
                "DistributeMixedRouteOnASCalculus": "False",
                "OrderPalletByPackageCodeOccupation": "True",
                "OrderPalletByCancha": "True",
                "GroupComplexLoads": "True",
                "LimitPackageGroups": "True",
                "CombinedGroups": "(10, 20, 50, 90, 100, 200); (30, 40, 60, 70, 80)",
                "MinimumVolumeInComplexLoads": "42",
                "QuantitySkuInComplexLoads": "30",
                "UseItemsExclusiveOfWarehouse": "False",
                "EnableSafeSideRule": "False",
                "BulkAllPallets": "False",
                "NotMountBulkPallets": "True",
                "ReturnableAndDisposableSplitRuleDisabled": "True",
                "IsotonicTopPalletCustomOrderRule": "True",
                "ReassignmentOfNonPalletizedItems": "True",
                "SideBalanceRule": "True",
                "ReduceVolumePallets": "False",
                "PercentageReductionInPalletOccupancy": "0",
                "QuantityOfPackagingOnSamePallet": "0",
                "LoadControlEnabled": "False",
                "DebugStackBuilderEnabled": "False",
                "PalletizeDetached": "True",
                "MaxPackageGroups": "6",
                "OrderPalletByGroupSubGroupAndPackagingItem": "True",
                "ShouldLimitPackageGroups": "True",
                "OccupationAdjustmentToPreventExcessHeight": "False",
                "PalletEqualizationRule": "False",
                "ProductGroupSpecific": "",
                "PercentOccupationMinByDivision": "0",
                "PercentOccupationMinBySelectionPalletDisassembly": "0"
            },
            "MapNumber": mapa_num,
            "NotPalletizedItems": [],
            "Type": "Route"
        }
        
        # 4. Preparar diretório de trabalho
        route_dir = OCP_ROOT / "data" / "route" / str(mapa_num)
        output_dir = route_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar input.json
        import shutil
        shutil.copy(json_path, route_dir / "input.json")
        
        # Salvar config.json diretamente no route_dir (sem copiar)
        config_route_path = route_dir / "config.json"
        with open(config_route_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        # Salvar backup no WORK_DIR também
        config_backup = WORK_DIR / "config.json"
        with open(config_backup, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        # 5. Executar paletização via módulo Python (bash)
        env = os.environ.copy()
        env['MAPA_NUM'] = str(mapa_num)
        env['PYTHONUTF8'] = '1'
        
        # Usar bash para executar como módulo Python corretamente
        bash_cmd = f"cd /mnt/c/prd_debian/ocp_wms_core && MAPA_NUM={mapa_num} python3 -m ocp_score-main.service.palletizing_processor"
        
        result = subprocess.run(
            ["bash", "-c", bash_cmd],
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='ignore'
        )
        
        # SEMPRE salvar stdout/stderr para debug (mesmo quando returncode == 0)
        debug_file = ERROR_DIR / f"{xml_path.stem}.debug"
        debug_file.write_text(
            f"MAPA: {mapa_num}\n"
            f"RETURNCODE: {result.returncode}\n"
            f"OUTPUT_DIR: {output_dir}\n\n"
            f"=== STDERR ===\n{result.stderr}\n\n"
            f"=== STDOUT ===\n{result.stdout}",
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            # Salvar erro em arquivo para debug
            err_file = ERROR_DIR / f"{xml_path.stem}.err"
            err_file.write_text(f"RETURNCODE: {result.returncode}\n\nSTDERR:\n{result.stderr}\n\nSTDOUT:\n{result.stdout}", encoding='utf-8')
            return False, f"Falha paletizacao: {error_msg[:200]}"
        
        # 6. Procurar TXT gerado
        txt_files = list(output_dir.glob("*palletize_result*.txt"))
        if not txt_files:
            # Debug: listar o que tem no output_dir
            all_files = list(output_dir.glob("*"))
            debug_msg = f"TXT nao gerado. Output_dir: {output_dir}. Arquivos: {[f.name for f in all_files]}"
            err_file = ERROR_DIR / f"{xml_path.stem}.err"
            err_file.write_text(debug_msg, encoding='utf-8')
            return False, debug_msg
        
        # Copiar TXT para pasta de sucesso
        txt_src = txt_files[0]
        txt_name = xml_path.stem + ".txt"
        txt_dst = SUCCESS_DIR / txt_name
        shutil.copy(txt_src, txt_dst)
        
        return True, f"OK - {txt_name}"
        
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, f"Erro: {str(e)[:100]}"

def main():
    # Listar XMLs
    xml_files = sorted(INPUT_DIR.glob("*.xml"))
    total = len(xml_files)
    
    if total == 0:
        print(f"ERRO: Nenhum XML encontrado em {INPUT_DIR}")
        return
    
    print("=" * 80)
    print(f"PROCESSAMENTO DIRETO - {total} XMLs MAPA")
    print("=" * 80)
    print(f"Entrada: {INPUT_DIR}")
    print(f"Saida: {SUCCESS_DIR}")
    print("=" * 80)
    print()
    
    # Estatísticas
    sucesso = 0
    erro = 0
    inicio = time.time()
    
    for i, xml_path in enumerate(xml_files, 1):
        ok, msg = processar_xml(xml_path)
        
        if ok:
            sucesso += 1
            status = "OK"
        else:
            erro += 1
            status = "FAIL"
            # Salvar erro
            err_path = ERROR_DIR / (xml_path.stem + ".err")
            with open(err_path, 'w', encoding='utf-8') as f:
                f.write(msg)
        
        # Estatísticas
        elapsed = time.time() - inicio
        rate = i / elapsed if elapsed > 0 else 0
        remaining = (total - i) / rate if rate > 0 else 0
        
        print(f"[{i:4d}/{total}] {status:4s} | {xml_path.name[:50]:50s} | "
              f"{rate:4.1f} xml/s | ~{int(remaining/60):2d}min")
    
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

if __name__ == "__main__":
    main()
