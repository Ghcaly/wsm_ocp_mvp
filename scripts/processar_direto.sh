#!/bin/bash

echo "🚀 Processando XMLs diretamente (sem APIs)"
echo "=========================================="

cd /mnt/c/prd_debian

# Criar diretórios
mkdir -p mapas/in mapas/out/processamento_massa/sucesso mapas/out/processamento_massa/erro

TOTAL=$(find meus_xmls -name "*.xml" -type f | wc -l)
echo "📊 Total de XMLs: $TOTAL"
echo ""

count=0
success=0
erro=0

for xml in meus_xmls/*.xml; do
    count=$((count + 1))
    filename=$(basename "$xml" .xml)
    mapa_num=$(echo "$filename" | grep -oP 'mapa_\K\d+' || echo "unknown")
    
    echo "[$count/$TOTAL] $filename"
    
    # Converter XML para JSON
    if python3 wms_converter/convert.py -i "$xml" -o "mapas/in/input.json" > /dev/null 2>&1; then
        echo "  ✓ Convertido"
        
        # Processar com OCP Core
        cd ocp_wms_core
        source wms_venv/bin/activate > /dev/null 2>&1
        export PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
        
        # Copiar para processamento
        cp /mnt/c/prd_debian/mapas/in/input.json /mnt/c/prd_debian/mapas/in/inputcompleto.json
        
        # Executar paletização
        cd ocp_score-main
        if python3 run_palletization.py /mnt/c/prd_debian/mapas/in/inputcompleto.json 2>&1 | grep -q "Paletização finalizada"; then
            # Copiar output.json se existir
            if [ -f "output.json" ]; then
                cp "output.json" "/mnt/c/prd_debian/mapas/out/processamento_massa/sucesso/${filename}.json"
                echo "  ✓ JSON de paletização gerado"
                success=$((success + 1))
            else
                echo "  ✗ Output JSON não encontrado"
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

echo "=========================================="
echo "📊 RESULTADOS:"
echo "   Total: $TOTAL"
echo "   ✓ Sucesso: $success"
echo "   ✗ Erro: $erro"
echo "=========================================="
