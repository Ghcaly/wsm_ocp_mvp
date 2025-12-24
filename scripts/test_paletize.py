#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/c/prd_debian/ocp_wms_core/ocp_score-main')

print("1. Testando import...")
try:
    from service.palletizing_processor import PalletizingProcessor
    print("✓ Import OK")
except Exception as e:
    print(f"✗ Erro: {e}")
    sys.exit(1)

print("\n2. Criando processor...")
processor = PalletizingProcessor(debug_enabled=False)
print("✓ Processor criado")

print("\n3. Tentando carregar dados...")
try:
    context = processor.load_configuration_and_data(
        '/mnt/c/prd_debian/mapas/in/config.json',
        '/mnt/c/prd_debian/mapas/in/input.json'
    )
    print(f"✓ Context carregado")
    print(f"   Mapa: {context.MapNumber}")
    print(f"   Orders: {len(context.orders)}")
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. Executando paletização...")
try:
    result = processor.palletize(context)
    print("✓ Paletização concluída")
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ SUCESSO!")
