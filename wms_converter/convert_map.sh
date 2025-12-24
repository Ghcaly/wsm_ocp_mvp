#!/bin/bash

XML_INPUT="/home/prd_debian/mapas/in/xml/04ed74c4f0144ec78ba5ce5e2cc97651_m_mapa_621622_0764_20251203125645.xml"
OUTPUT_DIR="/home/prd_debian/mapas/in/json"

echo "Processando XML..."

RESPONSE=$(curl -s -X POST "http://localhost:8000/convert" -F "file=@$XML_INPUT")

MAP_NUMBER=$(echo $RESPONSE | grep -oP '"Number"\s*:\s*"\K[^"]+')

if [ -z "$MAP_NUMBER" ]; then
    echo "Erro ao extrair numero do mapa"
    echo $RESPONSE
    exit 1
fi

mkdir -p $OUTPUT_DIR
OUTPUT_FILE="$OUTPUT_DIR/input_$MAP_NUMBER.json"

echo $RESPONSE | python3 -m json.tool > $OUTPUT_FILE

echo "Salvo: $OUTPUT_FILE"
echo "Mapa: $MAP_NUMBER"
