#!/bin/bash

XML_DIR="/home/prd_debian/mapas/in/xml"
OUTPUT_DIR="/home/prd_debian/mapas/in/json"

echo "Processando todos os XMLs em $XML_DIR"
echo ""

mkdir -p $OUTPUT_DIR

SUCCESS=0
ERROR=0
TOTAL=0

for XML_FILE in $XML_DIR/*.xml; do
    if [ -f "$XML_FILE" ]; then
        TOTAL=$((TOTAL + 1))
        FILENAME=$(basename "$XML_FILE")
        
        echo "[$TOTAL] Processando: $FILENAME"
        
        RESPONSE=$(curl -s -X POST "http://localhost:8000/convert" -F "file=@$XML_FILE")
        
        MAP_NUMBER=$(echo $RESPONSE | grep -oP '"Number"\s*:\s*"\K[^"]+')
        
        if [ -z "$MAP_NUMBER" ]; then
            echo "    Erro: nao foi possivel extrair numero do mapa"
            ERROR=$((ERROR + 1))
        else
            OUTPUT_FILE="$OUTPUT_DIR/input_$MAP_NUMBER.json"
            echo $RESPONSE | python3 -m json.tool > $OUTPUT_FILE
            
            if [ $? -eq 0 ]; then
                echo "    Salvo: input_$MAP_NUMBER.json"
                SUCCESS=$((SUCCESS + 1))
            else
                echo "    Erro ao salvar JSON"
                ERROR=$((ERROR + 1))
            fi
        fi
        echo ""
    fi
done

echo "================================"
echo "RESUMO"
echo "================================"
echo "Total: $TOTAL"
echo "Sucesso: $SUCCESS"
echo "Erros: $ERROR"
echo "================================"
