#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   PROCESSADOR FINAL - 112 XMLs                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd /mnt/c/prd_debian

# Criar diretórios
mkdir -p mapas/out/processamento_massa/sucesso
mkdir -p mapas/out/processamento_massa/erro

TOTAL=$(find meus_xmls -name "*.xml" -type f | wc -l)
echo "📊 Total: $TOTAL XMLs"
echo ""

count=0
success=0
erro=0

for xml in meus_xmls/*.xml; do
    count=$((count + 1))
    filename=$(basename "$xml" .xml)
    mapa_num=$(echo "$filename" | grep -oP 'mapa_\K\d+' || echo "unknown")
    
    printf "[$count/$TOTAL] %-70s" "$filename"
    
    # 1. Converter XML -> JSON
    if ! python3 wms_converter/convert.py -i "$xml" -o "mapas/in/input.json" > /dev/null 2>&1; then
        echo "✗ Erro conversão"
        erro=$((erro + 1))
        continue
    fi
    
    # 2. Extrair warehouse do JSON
    warehouse=$(python3 -c "import json; f=open('mapas/in/input.json'); d=json.load(f); print(d['Warehouse']['UnbCode'])" 2>/dev/null || echo "916")
    
    # 3. Criar config
    echo "{\"warehouse\":\"$warehouse\",\"delivery_date\":\"2025-12-23\"}" > mapas/in/config.json
    
    # 4. Preparar diretório de trabalho
    WORK_DIR="ocp_wms_core/ocp_score-main/data/route/$mapa_num"
    mkdir -p "$WORK_DIR"
    mkdir -p "$WORK_DIR/output"
    
    # 5. Copiar arquivos
    cp mapas/in/config.json "$WORK_DIR/config.json"
    cp mapas/in/input.json "$WORK_DIR/input.json"
    
    # 6. Executar paletização como módulo Python
    cd ocp_wms_core
    if python3 -m ocp_score-main.service.palletizing_processor > /tmp/paletize_${mapa_num}.log 2>&1; then
        
        # 7. Procurar TXT gerado
        txt_file=$(find "ocp_score-main/data/route/$mapa_num" -name "*.txt" -type f 2>/dev/null | head -1)
        
        if [ -f "$txt_file" ]; then
            cp "$txt_file" "/mnt/c/prd_debian/mapas/out/processamento_massa/sucesso/${filename}.txt"
            echo "✓"
            success=$((success + 1))
        else
            echo "✗ TXT não gerado"
            erro=$((erro + 1))
        fi
    else
        echo "✗ Falha paletização"
        erro=$((erro + 1))
    fi
    
    cd /mnt/c/prd_debian
done

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    RESULTADOS FINAIS                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "  📊 Total:    $TOTAL"
echo "  ✅ Sucesso:  $success"
echo "  ❌ Erro:     $erro"
echo ""
echo "📁 Arquivos processados em:"
echo "   c:\\prd_debian\\mapas\\out\\processamento_massa\\sucesso\\"
echo ""
