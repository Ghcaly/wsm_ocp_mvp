#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   PROCESSAMENTO EM MASSA - Versão Simplificada              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /mnt/c/prd_debian

# Criar diretórios
mkdir -p mapas/out/processamento_massa/sucesso
mkdir -p mapas/out/processamento_massa/erro

TOTAL=$(find meus_xmls -name "*.xml" -type f | wc -l)
echo "📊 Total de XMLs: $TOTAL"
echo ""

count=0
success=0
erro=0

# Processar cada XML
for xml in meus_xmls/*.xml; do
    count=$((count + 1))
    filename=$(basename "$xml" .xml)
    mapa_num=$(echo "$filename" | grep -oP 'mapa_\K\d+' || echo "unknown")
    
    echo "[$count/$TOTAL] $filename"
    
    # 1. Converter XML para JSON
    if python3 wms_converter/convert.py -i "$xml" -o "mapas/in/input.json" > /dev/null 2>&1; then
        
        # 2. Ler JSON para pegar warehouse
        warehouse=$(python3 -c "import json; f=open('mapas/in/input.json'); d=json.load(f); print(d['Warehouse']['UnbCode'])" 2>/dev/null || echo "916")
        
        # 3. Criar config
        echo "{\"warehouse\":\"$warehouse\"}" > mapas/in/config.json
        
        # 4. Criar diretório de trabalho
        WORK_DIR="ocp_wms_core/ocp_score-main/data/route/$mapa_num"
        mkdir -p "$WORK_DIR"
        
        # 5. Copiar arquivos
        cp mapas/in/config.json "$WORK_DIR/config.json"
        cp mapas/in/input.json "$WORK_DIR/input.json"
        
        # 6. Tentar processar com Python direto
        cd ocp_wms_core/ocp_score-main
        
        # Executar via PYTHONPATH
        if PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core python3 -c "
import sys
sys.path.insert(0, '/mnt/c/prd_debian/ocp_wms_core/ocp_score-main')
from service.palletizing_processor import PalletizingProcessor
processor = PalletizingProcessor(debug_enabled=False)
context = processor.load_configuration_and_data('data/route/$mapa_num/config.json', 'data/route/$mapa_num/input.json')
result = processor.palletize(context)
print('OK')
" 2>&1 | grep -q "OK"; then
            echo "  ✓ Paletizado"
            
            # Procurar TXT gerado
            txt_file=$(find "data/route/$mapa_num" -name "*.txt" -type f 2>/dev/null | head -1)
            if [ -f "$txt_file" ]; then
                cp "$txt_file" "/mnt/c/prd_debian/mapas/out/processamento_massa/sucesso/${filename}.txt"
                echo "  ✓ TXT copiado"
                success=$((success + 1))
            else
                echo "  ✗ TXT não encontrado"
                erro=$((erro + 1))
            fi
        else
            echo "  ✗ Erro na paletização"
            erro=$((erro + 1))
        fi
        
        cd /mnt/c/prd_debian
        
    else
        echo "  ✗ Erro na conversão"
        erro=$((erro + 1))
    fi
    
    echo ""
done

echo "══════════════════════════════════════════════════════════════"
echo "📊 RESULTADOS FINAIS:"
echo "   Total: $TOTAL"
echo "   ✓ Sucesso: $success"
echo "   ✗ Erro: $erro"
echo "══════════════════════════════════════════════════════════════"
