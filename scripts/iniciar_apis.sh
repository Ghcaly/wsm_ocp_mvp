#!/bin/bash
# Script para iniciar todas as APIs

echo "🚀 Iniciando APIs..."

# Criar diretórios necessários
mkdir -p /mnt/c/prd_debian/mapas/in
mkdir -p /mnt/c/prd_debian/mapas/out

# Iniciar WMS Converter (porta 8000)
echo "📦 Iniciando WMS Converter..."
cd /mnt/c/prd_debian/wms_converter
source venv/bin/activate
nohup python api.py > /tmp/wms_converter.log 2>&1 &
sleep 3

# Iniciar WMS Boxing (porta 8001)
echo "📦 Iniciando WMS Boxing..."
cd /mnt/c/prd_debian/wms-itemsboxing
source venv/bin/activate
nohup python src/app.py > /tmp/wms_boxing.log 2>&1 &
sleep 3

# Iniciar OCP Core e Orchestrator
echo "📦 Iniciando OCP Core..."
cd /mnt/c/prd_debian/ocp_wms_core
source wms_venv/bin/activate
cd ocp_score-main
export PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
nohup python master_orchestrator.py > /tmp/orchestrator.log 2>&1 &

echo ""
echo "⏳ Aguardando APIs iniciarem..."
sleep 10

echo ""
echo "🔍 Verificando APIs..."
curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "✅ WMS Converter: Online" || echo "❌ WMS Converter: Offline"
curl -s http://localhost:8001/health > /dev/null 2>&1 && echo "✅ WMS Boxing: Online" || echo "❌ WMS Boxing: Offline"

echo ""
echo "✅ APIs iniciadas!"
echo ""
