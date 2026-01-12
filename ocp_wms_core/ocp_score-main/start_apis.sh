#!/bin/bash
# Script para iniciar todas as APIs

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🚀 Iniciando APIs de Paletização OCP                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

# Ativa venv
echo -e "\n${YELLOW}📦 Ativando ambiente virtual...${NC}"
source /home/wms_core/wms_venv/bin/activate

# Diretório base
cd /home/wms_core/wsm_ocp_mvp/ocp_wms_core/ocp_score-main

# Mata processos anteriores
echo -e "\n${YELLOW}🔄 Parando APIs antigas...${NC}"
pkill -f "api_flask_complete.py" 2>/dev/null
pkill -f "api_fastapi.py" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
sleep 2

# Cria diretório de saída
mkdir -p /tmp/ocp_results

# Verifica WMS Converter
echo -e "\n${YELLOW}🔍 Verificando WMS Converter (porta 8002)...${NC}"
if curl -s http://localhost:8002/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ WMS Converter está rodando${NC}"
else
    echo -e "${YELLOW}⚠️  WMS Converter não está rodando!${NC}"
    echo -e "${YELLOW}   Iniciando WMS Converter...${NC}"
    cd /home/wms_core/wsm_ocp_mvp/wms_converter
    nohup python api.py > /tmp/wms_converter.log 2>&1 &
    sleep 3
    cd /home/wms_core/wsm_ocp_mvp/ocp_wms_core/ocp_score-main
    echo -e "${GREEN}✅ WMS Converter iniciado${NC}"
fi

# Inicia Flask API (porta 5001)
echo -e "\n${YELLOW}🌶️  Iniciando Flask API (porta 5001)...${NC}"
nohup python api_flask_complete.py > /tmp/flask_api.log 2>&1 &
FLASK_PID=$!
sleep 2

if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Flask API rodando (PID: $FLASK_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Flask API não respondeu${NC}"
fi

# Inicia FastAPI (porta 8000)
echo -e "\n${YELLOW}⚡ Iniciando FastAPI (porta 8000)...${NC}"
nohup uvicorn api_fastapi:app --host 0.0.0.0 --port 8000 > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!
sleep 3

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ FastAPI rodando (PID: $FASTAPI_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  FastAPI não respondeu${NC}"
fi

# Resumo
echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   ✅ APIs Iniciadas                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🌐 WMS Converter:${NC}  http://localhost:8002"
echo -e "${GREEN}🌶️  Flask API:${NC}      http://localhost:5001"
echo -e "${GREEN}⚡ FastAPI:${NC}         http://localhost:8000"
echo -e "${GREEN}📖 FastAPI Docs:${NC}   http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}📂 Output:${NC} /tmp/ocp_results"
echo -e "${YELLOW}📝 Logs:${NC}"
echo "   - Flask: tail -f /tmp/flask_api.log"
echo "   - FastAPI: tail -f /tmp/fastapi.log"
echo "   - WMS Converter: tail -f /tmp/wms_converter.log"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Exemplo de uso:${NC}"
echo ""
echo "  # Upload via Flask"
echo "  curl -X POST http://localhost:5001/process-xml \\"
echo "    -F 'file=@/home/wms_core/wms_xml_in/mapa_448111.xml'"
echo ""
echo "  # Upload via FastAPI"
echo "  curl -X POST http://localhost:8000/process-xml \\"
echo "    -F 'file=@/home/wms_core/wms_xml_in/mapa_448111.xml'"
echo ""
echo "  # Download resultado"
echo "  curl http://localhost:5001/result/448111 -o resultado.txt"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
