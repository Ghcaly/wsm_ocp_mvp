#!/bin/bash
cd /mnt/c/prd_debian

echo "=== TESTE MARKETPLACE DETECTION ==="
echo ""

# Converter XML
echo "1. Convertendo XML..."
python3 wms_converter/convert.py -i test_mapa_985625.xml -o mapas/in/test_input.json 2>&1 | tail -2

# Criar config simples
echo ""
echo "2. Criando config.json..."
cat > mapas/in/config.json <<'ENDCONFIG'
{
  "warehouse": "CDD-Sul SP",
  "delivery_date": "2025-12-23",
  "Settings": {
    "UseBaySmallerThan35": false,
    "KegExclusivePallet": true,
    "IncludeTopOfPallet": true,
    "TwoOrMoreLayers": false,
    "IsobaricTankPallet": false,
    "PureWaterPallet": false,
    "IsobaricWaterPallet": false,
    "DisposablePallet": true,
    "MixedPallet": true,
    "MixedLayerPallet": true,
    "MixedExceptIsobaricTank": true,
    "ChoppPackagePallet": false,
    "ReturShopKeeper600Pallet": false,
    "KeepWaterMixPallet": false,
    "HighPriorityDisposable": false,
    "BulkPriority": false,
    "KeepGroupInDifferentPallet": false,
    "KeepMixedGroup": false,
    "QuantityAssemblyPallet": 1,
    "MaximumShortPalletQuantity": 1,
    "CrossDockingStopPoint": 0,
    "AS": 0,
    "DisposableFirstLayer": false,
    "ReturnableFirstLayer": false,
    "NonReturnableFirstLayer": false,
    "DisposableMixedPallet": true,
    "ReturnableMixedPallet": true,
    "NonReturnableMixedPallet": true,
    "SeparateReturnableNonReturnable": false,
    "MapPriorityForFirstPallet": false,
    "AllowIncompleteMap": false,
    "RoutePriority": [],
    "ExcludeProducts": [],
    "IncludeProducts": [],
    "CombinedGroups": ""
  }
}
ENDCONFIG

echo "Config OK"

# Processar
echo ""
echo "3. Processando paletização (filtrando logs marketplace)..."
cd ocp_wms_core
MAPA_NUM='985625' python3 -m ocp_score-main.service.palletizing_processor 2>&1 | tee /tmp/test_marketplace.log | grep -i "marketplace\|carregados"

echo ""
echo "4. Verificando JSON gerado..."
JSON_FILE=$(find data/route/985625/output -name "palletize_result*.json" 2>/dev/null | head -1)
if [ -f "$JSON_FILE" ]; then
    echo "JSON encontrado: $JSON_FILE"
    echo ""
    echo "Contando Marketplace=true:"
    grep -o '"Marketplace": true' "$JSON_FILE" | wc -l
    echo ""
    echo "Contando Marketplace=false:"
    grep -o '"Marketplace": false' "$JSON_FILE" | wc -l
else
    echo "JSON não encontrado!"
fi

echo ""
echo "5. Verificando TXT gerado..."
TXT_FILE=$(find data/route/985625/output -name "palletize_result*.txt" 2>/dev/null | head -1)
if [ -f "$TXT_FILE" ]; then
    echo "TXT encontrado: $TXT_FILE"
    echo ""
    echo "Procurando 'BinPack' no TXT:"
    grep -c "BinPack" "$TXT_FILE" || echo "0 ocorrências"
else
    echo "TXT não encontrado!"
fi

echo ""
echo "=== TESTE CONCLUÍDO ==="
