#!/bin/bash

cd /mnt/c/prd_debian

xml_file="meus_xmls/005fe6185a3841c8a1830dc8151ceeb0_m_mapa_622178_0764_20251210223427.xml"
mapa_num="622178"

echo "=== TESTANDO MARCAÇÃO BINPACK ==="
echo ""
echo "Mapa: $mapa_num"
echo ""

echo "1. Convertendo XML para JSON..."
python3 wms_converter/convert.py -i "$xml_file" -o mapas/in/input.json
echo "✓ JSON gerado"
echo ""

echo "2. Criando config.json..."
cd_num=$(grep -oP '"Company":\s*"\K[0-9]+' mapas/in/input.json | head -1)
cat > mapas/in/config.json << EOF
{
    "warehouse": "${cd_num}",
    "calculation_mode": "route"
}
EOF
echo "✓ Config criado (warehouse: $cd_num)"
echo ""

echo "3. Copiando para diretório de trabalho..."
mkdir -p ocp_wms_core/ocp_score-main/data/route/${mapa_num}
cp mapas/in/input.json ocp_wms_core/ocp_score-main/data/route/${mapa_num}/
cp mapas/in/config.json ocp_wms_core/ocp_score-main/data/route/${mapa_num}/
echo "✓ Arquivos copiados"
echo ""

echo "4. Executando paletização..."
cd ocp_wms_core
MAPA_NUM="${mapa_num}" python3 -m ocp_score-main.service.palletizing_processor > /tmp/palletize_${mapa_num}.log 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Paletização concluída com sucesso!"
    echo ""
    
    # Copiar TXT gerado
    cd /mnt/c/prd_debian
    txt_file=$(find ocp_wms_core/ocp_score-main/data/route/${mapa_num}/output -name "*.txt" 2>/dev/null | head -1)
    
    if [ -n "$txt_file" ]; then
        output_name="005fe6185a3841c8a1830dc8151ceeb0_m_mapa_622178_0764_20251210223427.txt"
        mkdir -p mapas/out/processamento_massa/teste_binpack
        cp "$txt_file" "mapas/out/processamento_massa/teste_binpack/$output_name"
        echo "✓ TXT copiado para: mapas/out/processamento_massa/teste_binpack/$output_name"
        echo ""
        
        echo "5. Procurando marcação 'BinPack' no TXT..."
        echo ""
        grep -n "BinPack" "mapas/out/processamento_massa/teste_binpack/$output_name" | head -10
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓✓✓ MARCAÇÃO BINPACK ENCONTRADA! ✓✓✓"
        else
            echo ""
            echo "⚠ Nenhuma marcação BinPack encontrada (talvez não haja produtos marketplace neste mapa)"
        fi
        echo ""
        echo "Veja produtos 21968 e 21973:"
        grep -E "21968|21973" "mapas/out/processamento_massa/teste_binpack/$output_name"
    else
        echo "⚠ TXT não encontrado"
    fi
else
    echo "❌ Erro na paletização"
    echo ""
    echo "Últimas linhas do log:"
    tail -20 /tmp/palletize_${mapa_num}.log
fi
