#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/c/prd_debian/ocp_wms_core/ocp_score-main')

try:
    from service.calculator_palletizing_service import CalculatorPalletizingService
    print("✓ Import OK")
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
