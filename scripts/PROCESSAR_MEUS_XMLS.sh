#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
XML_DIR="$BASE_DIR/meus_xmls"
PROCESS_SCRIPT="$SCRIPT_DIR/processar_massa_simples.sh"

# Conta quantos XMLs voce tem
TOTAL=$(find "$XML_DIR" -name "*.xml" -type f | wc -l)

if [ $TOTAL -eq 0 ]; then
    echo "Nenhum XML encontrado em c:/prd_debian/meus_xmls/"
    echo ""
    echo "Coloque seus XMLs aqui:"
    echo "   c:/prd_debian/meus_xmls/"
    echo ""
    echo "Exemplo:"
    echo "   cp /caminho/seus/xmls/*.xml /mnt/c/prd_debian/meus_xmls/"
    exit 1
fi

echo "Encontrados $TOTAL XMLs para processar"
echo ""

# Processar
cd "$BASE_DIR"
bash "$PROCESS_SCRIPT" "$XML_DIR"

echo ""
echo "Pronto!"
echo "Resultados: c:/prd_debian/mapas/out/processamento_massa/sucesso/"
