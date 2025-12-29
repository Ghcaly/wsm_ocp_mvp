#!/bin/bash
set -x  # Debug mode

echo "=== Teste de Processamento de 1 XML ==="

cd /mnt/c/prd_debian

# Pegar primeiro XML
XML=$(ls meus_xmls/*.xml | head -1)
echo "XML: $XML"

# 1. Converter
echo ""
echo "1. CONVERSÃO XML -> JSON"
python3 wms_converter/convert.py -i "$XML" -o mapas/in/test.json 2>&1
echo "Status conversão: $?"

# 2. Ver JSON gerado
echo ""
echo "2. JSON GERADO:"
head -50 mapas/in/test.json

# 3. Tentar paletizar
echo ""
echo "3. TENTANDO PALETIZAR"
cd ocp_wms_core
source wms_venv/bin/activate

# Copiar para local esperado
cp /mnt/c/prd_debian/mapas/in/test.json /mnt/c/prd_debian/mapas/in/inputcompleto.json

# Criar config simples
echo '{"warehouse":"916","delivery_date":"2025-12-23"}' > /mnt/c/prd_debian/mapas/in/config_completo.json

# Tentar rodar script de geração de TXT
cd /mnt/c/prd_debian/ocp_wms_core
bash GERAR_TXT_COMPLETO.sh 2>&1 | tail -100

echo ""
echo "=== FIM ==="
