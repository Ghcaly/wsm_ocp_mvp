#!/usr/bin/env python3
"""
Processa JSONs gerados por `wms_converter` e executa o processor
para gerar TXTs usando `ocp_score-main.service.palletizing_processor`.

Uso: python scripts/processar_jsons_windows.py
"""
from pathlib import Path
import json
import shutil
import subprocess
import os
import re

REPO = Path(__file__).resolve().parent.parent
JSON_DIR = REPO / 'wms_converter' / 'out_jsons'
WORK_ROOT = REPO / 'ocp_wms_core' / 'ocp_score-main' / 'data' / 'route'
OUTPUT_TXT_DIR = REPO / 'mapas' / 'out' / 'processamento_massa' / 'sucesso'

OUTPUT_TXT_DIR.mkdir(parents=True, exist_ok=True)
WORK_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
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
    "OrderPalletByPackageCodeOccupation": "True",
    "OrderPalletByCancha": "True",
    "GroupComplexLoads": "True",
    "LimitPackageGroups": "True",
    "CombinedGroups": "(10, 20, 50, 90, 100, 200); (30, 40, 60, 70, 80)",
    "MinimumVolumeInComplexLoads": "42",
    "QuantitySkuInComplexLoads": "30",
    "UseItemsExclusiveOfWarehouse": "False",
    "PalletizeDetached": "True",
    "MaxPackageGroups": "6"
  },
  "MapNumber": 0,
  "NotPalletizedItems": [],
  "Type": "Route"
}

def extract_map_number_from_json(path: Path):
    try:
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        num = data.get('Number') or data.get('MapNumber')
        if num:
            return str(num)
    except Exception:
        pass
    # fallback to filename regex
    m = re.search(r'JsonInMapsV2?(\d+)', path.name)
    if m:
        return m.group(1)
    m2 = re.search(r'mapa_(\d+)', path.name)
    if m2:
        return m2.group(1)
    return 'unknown'

def run_for_json(json_path: Path):
    mapa_num = extract_map_number_from_json(json_path)
    work_dir = WORK_ROOT / mapa_num
    output_dir = work_dir / 'output'
    work_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # copy input
    shutil.copy(json_path, work_dir / 'input.json')

    # write config
    config = DEFAULT_CONFIG.copy()
    try:
        config['MapNumber'] = int(mapa_num)
    except Exception:
        config['MapNumber'] = 0

    with open(work_dir / 'config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    env = os.environ.copy()
    env['MAPA_NUM'] = mapa_num

    try:
        result = subprocess.run([
            os.sys.executable, '-m', 'ocp_score-main.service.palletizing_processor'
        ], cwd=str(REPO / 'ocp_wms_core'), capture_output=True, text=True, env=env, timeout=300)

        # check output for errors
        if result.returncode != 0:
            return False, f"process failed: {result.returncode} stdout={result.stdout[:200]} stderr={result.stderr[:200]}"

        # find txt in output_dir
        txts = list(output_dir.glob('*.txt'))
        if not txts:
            return False, 'no txt generated'

        # copy first txt found
        out_name = json_path.stem + '.txt'
        shutil.copy(txts[0], OUTPUT_TXT_DIR / out_name)
        return True, out_name

    except subprocess.TimeoutExpired:
        return False, 'timeout'
    except Exception as e:
        return False, str(e)

def main():
    json_files = sorted(JSON_DIR.glob('*.json'))
    if not json_files:
        print('No JSON files found in', JSON_DIR)
        return

    total = len(json_files)
    success = 0
    errors = 0

    for i, j in enumerate(json_files, 1):
        print(f'[{i}/{total}] Processing {j.name}...')
        ok, msg = run_for_json(j)
        if ok:
            success += 1
            print('  ✓', msg)
        else:
            errors += 1
            print('  ✗', msg)

    print('\nSummary:')
    print('  Total:', total)
    print('  Success:', success)
    print('  Errors:', errors)
    print('TXTs saved under', OUTPUT_TXT_DIR)

if __name__ == "__main__":
    main()
