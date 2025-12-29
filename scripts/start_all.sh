#!/bin/bash

echo "========================================="
echo "🚀 Iniciando todas as APIs"
echo "========================================="

# Criar diretórios
mkdir -p /mnt/c/prd_debian/mapas/in
mkdir -p /mnt/c/prd_debian/mapas/out

# 1. WMS Converter (porta 8000)
echo ""
echo "📦 [1/3] Iniciando WMS Converter..."
cd /mnt/c/prd_debian/wms_converter
source venv/bin/activate
nohup python api.py > /tmp/wms_converter.log 2>&1 &
echo "    PID: $!"
sleep 4

# 2. WMS Boxing (porta 8001)
echo "📦 [2/3] Iniciando WMS Boxing..."
cd /mnt/c/prd_debian/wms-itemsboxing
source venv/bin/activate
nohup python src/app.py > /tmp/wms_boxing.log 2>&1 &
echo "    PID: $!"
sleep 4

# 3. OCP Core + Orchestrator (porta 5000 e 9000)
echo "📦 [3/3] Iniciando OCP Core..."
cd /mnt/c/prd_debian/ocp_wms_core
source wms_venv/bin/activate
export PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
cd ocp_score-main
nohup python master_orchestrator.py > /tmp/orchestrator.log 2>&1 &
echo "    PID: $!"

echo ""
echo "⏳ Aguardando APIs estabilizarem (15s)..."
sleep 15

echo ""
echo "========================================="
echo "🔍 Verificando status das APIs"
echo "========================================="

# Verificar cada API
check_api() {
    local name=$1
    local url=$2
    
    if curl -s --max-time 3 "$url" > /dev/null 2>&1; then
        echo "✅ $name: ONLINE"
        return 0
    else
        echo "❌ $name: OFFLINE"
        return 1
    fi
}

check_api "WMS Converter (8000)" "http://localhost:8000/health"
check_api "WMS Boxing (8001)" "http://localhost:8001/health"

echo ""
echo "========================================="
echo "✅ Pronto para processar!"
echo "========================================="
