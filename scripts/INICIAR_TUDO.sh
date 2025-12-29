#!/bin/bash
set -e

echo "================================================"
echo "🚀 INICIANDO PROJETO - Processamento de XMLs"
echo "================================================"
echo ""

# Criar diretórios
mkdir -p /mnt/c/prd_debian/mapas/in
mkdir -p /mnt/c/prd_debian/mapas/out

echo "📦 Iniciando WMS Converter (porta 8000)..."
cd /mnt/c/prd_debian/wms_converter
source venv/bin/activate
python3 api.py > /tmp/wms_converter.log 2>&1 &
WMS_PID=$!
echo "   ✓ PID: $WMS_PID"
sleep 3

echo "📦 Iniciando WMS Boxing (porta 8001)..."
cd /mnt/c/prd_debian/wms-itemsboxing
source venv/bin/activate
python3 src/app.py > /tmp/wms_boxing.log 2>&1 &
BOXING_PID=$!
echo "   ✓ PID: $BOXING_PID"
sleep 3

echo "📦 Iniciando OCP Core + Orchestrator..."
cd /mnt/c/prd_debian/ocp_wms_core
source wms_venv/bin/activate
export PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
cd ocp_score-main
python3 master_orchestrator.py > /tmp/orchestrator.log 2>&1 &
OCP_PID=$!
echo "   ✓ PID: $OCP_PID"

echo ""
echo "⏳ Aguardando APIs iniciarem (15 segundos)..."
sleep 15

echo ""
echo "🔍 Verificando APIs..."
if curl -s --max-time 2 http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ WMS Converter: ONLINE"
else
    echo "   ❌ WMS Converter: OFFLINE (verificar /tmp/wms_converter.log)"
fi

if curl -s --max-time 2 http://localhost:8001/health > /dev/null 2>&1; then
    echo "   ✅ WMS Boxing: ONLINE"
else
    echo "   ❌ WMS Boxing: OFFLINE (verificar /tmp/wms_boxing.log)"
fi

echo ""
echo "================================================"
echo "📊 Processando XMLs da pasta meus_xmls/"
echo "================================================"
echo ""

# Contar XMLs
TOTAL=$(find /mnt/c/prd_debian/meus_xmls -name "*.xml" -type f 2>/dev/null | wc -l)
echo "📁 Total de XMLs encontrados: $TOTAL"
echo ""

if [ $TOTAL -eq 0 ]; then
    echo "❌ Nenhum XML encontrado em c:/prd_debian/meus_xmls/"
    echo ""
    echo "💡 Coloque seus XMLs nesta pasta e execute novamente"
    exit 1
fi

echo "🚀 Iniciando processamento..."
echo ""

cd /mnt/c/prd_debian
./processar_massa_simples.sh /mnt/c/prd_debian/meus_xmls

echo ""
echo "================================================"
echo "✅ PROCESSAMENTO CONCLUÍDO!"
echo "================================================"
echo ""
echo "📂 Resultados:"
echo "   Sucesso: c:/prd_debian/mapas/out/processamento_massa/sucesso/"
echo "   Erros:   c:/prd_debian/mapas/out/processamento_massa/erro/"
echo "   Logs:    c:/prd_debian/mapas/out/processamento_massa/logs/"
echo ""
