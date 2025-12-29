#!/bin/bash

#####################################################################
# Script Simplificado - Processamento em Massa de XMLs
#####################################################################

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

INPUT_DIR="${1:-/mnt/c/prd_debian/BinPacking/src/tests/samples/mapas_backtest}"
OUTPUT_BASE="/mnt/c/prd_debian/mapas/out/processamento_massa"
CONVERTER_URL="http://localhost:8002"

mkdir -p "$OUTPUT_BASE/sucesso"
mkdir -p "$OUTPUT_BASE/erro"
mkdir -p "$OUTPUT_BASE/logs"

LOG_FILE="$OUTPUT_BASE/logs/processamento_$(date +%Y%m%d_%H%M%S).log"
RESUMO_CSV="$OUTPUT_BASE/logs/resumo_boxing.csv"

# Criar cabeçalho do CSV
echo "Arquivo|Mapa|Usou_Boxing|Produtos_Marketplace" > "$RESUMO_CSV"

TOTAL=0
SUCESSO=0
ERRO=0
INICIO=$(date +%s)

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Processamento em Massa de XMLs - Paletização          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📁 Entrada:${NC} $INPUT_DIR"
echo -e "${GREEN}📂 Saída:${NC} $OUTPUT_BASE"
echo ""

# Verificar converter
if ! curl -s "$CONVERTER_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ ERRO: Converter não está rodando${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Converter: Online${NC}"

# Contar XMLs
TOTAL=$(find "$INPUT_DIR" -name "*.xml" -type f | wc -l)
echo -e "${BLUE}📊 Total de XMLs:${NC} $TOTAL"
echo ""
echo -e "${GREEN}🚀 Processando...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ativar ambiente virtual
cd /mnt/c/prd_debian/ocp_wms_core
source wms_venv/bin/activate
export PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH

current=0
while IFS= read -r xml_file; do
    current=$((current + 1))
    filename=$(basename "$xml_file" .xml)
    mapa_num=$(echo "$filename" | grep -oP 'mapa_\K\d+' || echo "unknown")
    
    echo -e "${BLUE}[$current/$TOTAL]${NC} ${YELLOW}$filename${NC}" | tee -a "$LOG_FILE"
    
    # Converter XML → JSON
    response=$(curl -s -X POST -F "file=@$xml_file" "$CONVERTER_URL/convert")
    
    # Variável para tracking de boxing
    USOU_BOXING="NAO"
    MARKETPLACE_COUNT=0
    
    if echo "$response" | grep -q '"Number"'; then
        # Salvar JSON diretamente
        echo "$response" > /mnt/c/prd_debian/mapas/in/inputcompleto.json
        
        if [ -f "/mnt/c/prd_debian/mapas/in/inputcompleto.json" ]; then
            # Sempre tentar boxing (apply_boxing.py já faz a detecção)
            MARKETPLACE_COUNT=1  # Flag para sempre tentar boxing
            
            # Processar boxing (apply_boxing.py detecta marketplace automaticamente)
            if [ "$MARKETPLACE_COUNT" -gt 0 ]; then
                echo "  📦 Verificando boxing..." | tee -a "$LOG_FILE"
                
                # Chamar helper Python usando ambiente virtual correto
                boxing_response=$(source /mnt/c/prd_debian/wms_converter/venv/bin/activate && \
                    python /mnt/c/prd_debian/apply_boxing.py /mnt/c/prd_debian/mapas/in/inputcompleto.json 2>&1)
                
                if echo "$boxing_response" | grep -q '"success": true'; then
                    # Salvar resultado do boxing
                    echo "$boxing_response" > /mnt/c/prd_debian/mapas/in/boxing_result.json
                    
                    # Extrair e contar itens empacotados
                    BOXES_COUNT=$(echo "$boxing_response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('result', [{}])[0].get('result', {}).get('boxes', [])))" 2>/dev/null || echo "0")
                    PACKAGES_COUNT=$(echo "$boxing_response" | python3 -c "import sys, json; d=json.load(sys.stdin); r=d.get('result', [{}])[0].get('result', {}).get('packages', []); print(sum(p.get('quantity', 0) for p in r))" 2>/dev/null || echo "0")
                    
                    echo "  ✓ Boxing aplicado: $BOXES_COUNT caixas, $PACKAGES_COUNT itens em pacotes" | tee -a "$LOG_FILE"
                    USOU_BOXING="SIM"
                else
                    echo "  ⚠️  Boxing falhou, continuando sem boxing" | tee -a "$LOG_FILE"
                    if [ "$DEBUG" = "1" ]; then
                        echo "  Debug: $boxing_response" >> "$LOG_FILE"
                    fi
                fi
            else
                echo "  ℹ️  Sem produtos marketplace" | tee -a "$LOG_FILE"
            fi
            
            # Gerar config usando config_generator.py
            cd /mnt/c/prd_debian/ocp_wms_core/ocp_score-main
            source ../wms_venv/bin/activate
            export PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
            python3 service/config_generator.py /mnt/c/prd_debian/mapas/in/inputcompleto.json /mnt/c/prd_debian/mapas/in/config_completo.json >> "$LOG_FILE" 2>&1
            cd /mnt/c/prd_debian
            
            if [ -f "/mnt/c/prd_debian/mapas/in/config_completo.json" ]; then
                # Gerar TXT
                bash /mnt/c/prd_debian/ocp_wms_core/GERAR_TXT_COMPLETO.sh >> "$LOG_FILE" 2>&1
                
                # Verificar TXT gerado
                txt_file="/mnt/c/prd_debian/mapas/out/palletize_result_map_${mapa_num}.txt"
                if [ -f "$txt_file" ]; then
                    cp "$txt_file" "$OUTPUT_BASE/sucesso/${filename}.txt"
                    echo -e "${GREEN}  ✓ Sucesso${NC} (Boxing: $USOU_BOXING, Marketplace: $MARKETPLACE_COUNT)" | tee -a "$LOG_FILE"
                    
                    # Salvar resumo em arquivo separado
                    echo "$filename|$mapa_num|$USOU_BOXING|$MARKETPLACE_COUNT" >> "$RESUMO_CSV"
                    
                    SUCESSO=$((SUCESSO + 1))
                else
                    echo -e "${RED}  ✗ TXT não gerado${NC}" | tee -a "$LOG_FILE"
                    cp "$xml_file" "$OUTPUT_BASE/erro/"
                    ERRO=$((ERRO + 1))
                fi
            else
                echo -e "${RED}  ✗ Config não gerado${NC}" | tee -a "$LOG_FILE"
                cp "$xml_file" "$OUTPUT_BASE/erro/"
                ERRO=$((ERRO + 1))
            fi
        else
            echo -e "${RED}  ✗ JSON não encontrado${NC}" | tee -a "$LOG_FILE"
            cp "$xml_file" "$OUTPUT_BASE/erro/"
            ERRO=$((ERRO + 1))
        fi
    else
        echo -e "${RED}  ✗ Erro na conversão${NC}" | tee -a "$LOG_FILE"
        cp "$xml_file" "$OUTPUT_BASE/erro/"
        ERRO=$((ERRO + 1))
    fi
    
    echo "" | tee -a "$LOG_FILE"
done < <(find "$INPUT_DIR" -name "*.xml" -type f)

# Relatório
FIM=$(date +%s)
DURACAO=$((FIM - INICIO))
MIN=$((DURACAO / 60))
SEG=$((DURACAO % 60))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    RELATÓRIO FINAL                            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Estatísticas:${NC}"
echo "   Total: $TOTAL"
echo -e "   ${GREEN}✓ Sucesso: $SUCESSO${NC}"
echo -e "   ${RED}✗ Erro: $ERRO${NC}"
echo ""
echo -e "${BLUE}⏱️  Tempo:${NC} ${MIN}m ${SEG}s"
echo ""
echo -e "${GREEN}📁 Resultados:${NC}"
echo "   Sucessos: $OUTPUT_BASE/sucesso/"
echo "   Erros: $OUTPUT_BASE/erro/"
echo ""

# Estatísticas de Boxing
TOTAL_COM_BOXING=$(grep -c "|SIM|" "$RESUMO_CSV" 2>/dev/null || echo "0")
TOTAL_SEM_BOXING=$(grep -c "|NAO|" "$RESUMO_CSV" 2>/dev/null || echo "0")

if [ -f "$RESUMO_CSV" ] && [ $SUCESSO -gt 0 ]; then
    echo -e "${YELLOW}📦 Estatísticas de Boxing:${NC}"
    echo "   Com Boxing (Marketplace): $TOTAL_COM_BOXING"
    echo "   Sem Boxing (Não-Marketplace): $TOTAL_SEM_BOXING"
    echo "   📋 Resumo detalhado: $RESUMO_CSV"
    echo ""
fi

if [ $SUCESSO -gt 0 ]; then
    echo -e "${GREEN}📄 TXTs gerados:${NC}"
    ls -lh "$OUTPUT_BASE/sucesso/"*.txt | head -5 | awk '{print "   " $5 "  " $9}'
    [ $SUCESSO -gt 5 ] && echo "   ... e mais $((SUCESSO - 5)) arquivo(s)"
    echo ""
fi

echo -e "${BLUE}✨ Concluído!${NC}"
