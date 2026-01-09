#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   PROCESSAMENTO COM VARIÁVEL DE AMBIENTE MAPA_NUM            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd /mnt/c/prd_debian

mkdir -p mapas/out/processamento_massa/sucesso
mkdir -p mapas/out/processamento_massa/erro

TOTAL=$(find meus_xmls -name "*.xml" -type f | wc -l)
echo "📊 Total: $TOTAL XMLs"
echo ""

count=0
success=0
erro=0
INICIO=$(date +%s)

for xml in meus_xmls/*.xml; do
    count=$((count + 1))
    filename=$(basename "$xml" .xml)
    mapa_num=$(echo "$filename" | grep -oP 'mapa_\K\d+' || echo "unknown")
    
    printf "[%3d/%3d] %-60s " "$count" "$TOTAL" "$(basename $xml)"
    
    # 1. Converter XML -> JSON
    if ! python3 wms_converter/convert.py -i "$xml" -o "mapas/in/input.json" > /dev/null 2>&1; then
        echo "✗ Conv"
        erro=$((erro + 1))
        continue
    fi
    
    # 2. Extrair warehouse
    warehouse=$(python3 -c "import json; f=open('mapas/in/input.json'); d=json.load(f); print(d['Warehouse']['UnbCode'])" 2>/dev/null || echo "916")
    
    # 3. Criar config completo
    cat > mapas/in/config.json << 'EOF'
{
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
  "MapNumber": 0,
  "NotPalletizedItems": [],
  "Type": "Route"
}
EOF
    
    # 3.5. Detectar marketplace e aplicar Boxing se necessário
    BOXING_RESULT=$(python3 detect_and_box.py "mapas/in/input.json" 2>/dev/null)
    HAS_MARKETPLACE=$(echo "$BOXING_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('has_marketplace', False))" 2>/dev/null || echo "False")
    
    if [ "$HAS_MARKETPLACE" = "True" ]; then
        BOXING_APPLIED=$(echo "$BOXING_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('boxing_applied', False))" 2>/dev/null)
        if [ "$BOXING_APPLIED" = "True" ]; then
            # Salva resultado do boxing para integração futura
            echo "$BOXING_RESULT" > "mapas/in/boxing_result_${mapa_num}.json"
        fi
    fi
    
    # 4. Preparar diretório
    WORK_DIR="ocp_wms_core/ocp_score-main/data/route/$mapa_num"
    mkdir -p "$WORK_DIR/output"
    
    # 5. Copiar arquivos
    cp mapas/in/config.json "$WORK_DIR/config.json"
    cp mapas/in/input.json "$WORK_DIR/input.json"
    
    # 6. Executar com variável de ambiente MAPA_NUM
    cd ocp_wms_core
    if MAPA_NUM="$mapa_num" python3 -m ocp_score-main.service.palletizing_processor > /tmp/proc_${mapa_num}.log 2>&1; then
        
        # 7. Procurar TXT gerado
        txt_file=$(find "ocp_score-main/data/route/$mapa_num/output" -name "*palletize_result*.txt" -type f 2>/dev/null | head -1)
        
        if [ -f "$txt_file" ]; then
            cp "$txt_file" "/mnt/c/prd_debian/mapas/out/processamento_massa/sucesso/${filename}.txt"
            echo "✓"
            success=$((success + 1))
        else
            echo "✗ NoTXT"
            erro=$((erro + 1))
        fi
    else
        echo "✗ Fail"
        erro=$((erro + 1))
    fi
    
    cd /mnt/c/prd_debian
done

FIM=$(date +%s)
TEMPO=$((FIM - INICIO))
MINUTOS=$((TEMPO / 60))
SEGUNDOS=$((TEMPO % 60))

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    RESULTADOS FINAIS                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
printf "  📊 Total:    %3d\n" "$TOTAL"
printf "  ✅ Sucesso:  %3d (%.1f%%)\n" "$success" "$(echo "scale=1; $success * 100 / $TOTAL" | bc)"
printf "  ❌ Erro:     %3d (%.1f%%)\n" "$erro" "$(echo "scale=1; $erro * 100 / $TOTAL" | bc)"
printf "  ⏱️  Tempo:    %dm %ds\n" "$MINUTOS" "$SEGUNDOS"
echo ""
echo "📁 c:\\prd_debian\\mapas\\out\\processamento_massa\\sucesso\\"
echo ""
