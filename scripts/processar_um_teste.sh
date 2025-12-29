#!/bin/bash

cd /mnt/c/prd_debian

# XML para testar
xml_file="meus_xmls/005fe6185a3841c8a1830dc8151ceeb0_m_mapa_622178_0764_20251210223427.xml"

if [ ! -f "$xml_file" ]; then
    echo "❌ Arquivo não encontrado: $xml_file"
    exit 1
fi

basename=$(basename "$xml_file" .xml)
mapa_num=$(echo "$basename" | grep -oE 'mapa_[0-9]+' | grep -oE '[0-9]+')

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          TESTE DE MARCAÇÃO BINPACK - MAPA $mapa_num           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Converter XML para JSON
echo "▶ Convertendo XML para JSON..."
python3 wms_converter/convert.py -i "$xml_file" -o mapas/in/input.json > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Conversão OK"
else
    echo "  ❌ Erro na conversão"
    exit 1
fi

# 2. Extrair warehouse
cd_num=$(grep -oP '"Company":\s*"\K[0-9]+' mapas/in/input.json | head -1)

# 3. Criar config.json
cat > mapas/in/config.json << EOF
{
    "warehouse": "$cd_num",
    "calculation_mode": "route",
    "number_of_bays": 10,
    "max_weight_per_pallet": 1200.0,
    "pallet_height": 160.0
}
EOF

# 4. Copiar arquivos
mkdir -p ocp_wms_core/ocp_score-main/data/route/${mapa_num}
cp mapas/in/input.json ocp_wms_core/ocp_score-main/data/route/${mapa_num}/
cp mapas/in/config.json ocp_wms_core/ocp_score-main/data/route/${mapa_num}/

# 5. Executar paletização
echo "▶ Executando paletização (Mapa: $mapa_num)..."
cd ocp_wms_core
MAPA_NUM="$mapa_num" python3 -m ocp_score-main.service.palletizing_processor > /tmp/proc_${mapa_num}.log 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Paletização OK"
    
    # 6. Procurar TXT gerado
    cd /mnt/c/prd_debian
    txt_output=$(find ocp_wms_core/ocp_score-main/data/route/${mapa_num}/output -name "*.txt" 2>/dev/null | head -1)
    
    if [ -n "$txt_output" ]; then
        # Copiar para diretório de teste
        mkdir -p mapas/out/teste_binpack
        cp "$txt_output" "mapas/out/teste_binpack/${basename}.txt"
        echo "  ✓ TXT gerado: mapas/out/teste_binpack/${basename}.txt"
        echo ""
        
        # 7. Procurar marcação BinPack
        echo "▶ Procurando marcação 'BinPack'..."
        binpack_count=$(grep -c "BinPack" "mapas/out/teste_binpack/${basename}.txt")
        
        if [ $binpack_count -gt 0 ]; then
            echo ""
            echo "╔═══════════════════════════════════════════════════════════════╗"
            echo "║  ✓✓✓ MARCAÇÃO BINPACK ENCONTRADA ($binpack_count ocorrências)    ║"
            echo "╚═══════════════════════════════════════════════════════════════╝"
            echo ""
            echo "Exemplos de produtos com BinPack:"
            grep "BinPack" "mapas/out/teste_binpack/${basename}.txt" | head -5
        else
            echo "  ⚠ Nenhuma marcação BinPack encontrada"
            echo ""
            echo "Produtos marketplace (21968, 21973, 27177):"
            grep -E "21968|21973|27177" "mapas/out/teste_binpack/${basename}.txt" | head -5
        fi
    else
        echo "  ❌ TXT não foi gerado"
        echo ""
        echo "Últimas linhas do log:"
        tail -30 /tmp/proc_${mapa_num}.log
    fi
else
    echo "  ❌ Erro na paletização"
    echo ""
    echo "Últimas linhas do log:"
    tail -30 /tmp/proc_${mapa_num}.log
fi
