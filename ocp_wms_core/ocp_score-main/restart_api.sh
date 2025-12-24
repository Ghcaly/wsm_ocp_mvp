#!/bin/bash
# Script para reiniciar a API de paletização

echo "🔄 Reiniciando API de Paletização..."
echo ""

# Para processos existentes
echo "Parando processos existentes..."
pkill -f "simple_api.py" 2>/dev/null
sleep 2

# Inicia novo processo
echo "Iniciando nova instância..."
cd /home/prd_debian/ocp_wms_core/ocp_score-main
source ../wms_venv/bin/activate
export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
nohup python simple_api.py > /tmp/api.log 2>&1 &
PID=$!

echo "✓ API iniciada com PID: $PID"
echo ""

# Aguarda e testa
echo "Aguardando servidor inicializar..."
sleep 3

echo ""
echo "Testando conexão..."
RESPONSE=$(curl -s http://localhost:5000/health)

if [ $? -eq 0 ]; then
    echo "✓ API está respondendo!"
    echo ""
    echo "Status: $RESPONSE"
    echo ""
    echo "📋 Endpoints disponíveis:"
    echo "  http://localhost:5000/              - Documentação"
    echo "  http://localhost:5000/health        - Health check"
    echo "  http://localhost:5000/mapas/list    - Listar arquivos"
    echo ""
    echo "Ver logs: tail -f /tmp/api.log"
else
    echo "✗ API não está respondendo"
    echo "Ver logs: cat /tmp/api.log"
    exit 1
fi
