#!/bin/bash

#####################################################################
# Script de Processamento em Massa de XMLs
# Processa múltiplos XMLs através do Master Orchestrator
#####################################################################

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
ORCHESTRATOR_URL="http://localhost:9000"
INPUT_DIR="${1:-/mnt/c/prd_debian/BinPacking/src/tests/samples/mapas_backtest}"
OUTPUT_BASE="/mnt/c/prd_debian/mapas/out/processamento_massa"
LOG_FILE="$OUTPUT_BASE/processamento_$(date +%Y%m%d_%H%M%S).log"
MAX_PARALLEL="${2:-1}"  # Número de processos paralelos (padrão: 1)

# Criar diretórios de saída
mkdir -p "$OUTPUT_BASE/sucesso"
mkdir -p "$OUTPUT_BASE/erro"
mkdir -p "$OUTPUT_BASE/logs"

# Mover LOG_FILE para pasta logs
LOG_FILE="$OUTPUT_BASE/logs/processamento_$(date +%Y%m%d_%H%M%S).log"

# Contadores
TOTAL=0
SUCESSO=0
ERRO=0
INICIO=$(date +%s)

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Processamento em Massa de XMLs - Paletização          ║${NC}"
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${GREEN}📁 Diretório de entrada:${NC} $INPUT_DIR"
echo -e "${GREEN}📂 Diretório de saída:${NC} $OUTPUT_BASE"
echo -e "${GREEN}📋 Arquivo de log:${NC} $LOG_FILE"
echo -e "${GREEN}⚙️  Processos paralelos:${NC} $MAX_PARALLEL"
echo ""

# Verificar se orchestrator está rodando
if ! curl -s "$ORCHESTRATOR_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ ERRO: Master Orchestrator não está rodando em $ORCHESTRATOR_URL${NC}"
    echo -e "${YELLOW}💡 Inicie o orchestrator primeiro:${NC}"
    echo "   cd /mnt/c/prd_debian/ocp_wms_core/ocp_score-main"
    echo "   source ../wms_venv/bin/activate"
    echo "   nohup python master_orchestrator.py > /tmp/orchestrator.log 2>&1 &"
    exit 1
fi

echo -e "${GREEN}✅ Master Orchestrator: Online${NC}"
echo ""

# Função para processar um XML
processar_xml() {
    local xml_file="$1"
    local filename=$(basename "$xml_file" .xml)
    local mapa_num=$(echo "$filename" | grep -oP 'mapa_\K\d+' || echo "$filename")
    
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} Processando: ${YELLOW}$filename${NC}" | tee -a "$LOG_FILE"
    
    # Fazer request ao orchestrator para converter XML
    local response=$(curl -s -X POST \
        -F "file=@$xml_file" \
        "$ORCHESTRATOR_URL/process-xml-file")
    
    # Verificar se houve sucesso na conversão
    if echo "$response" | grep -q '"success": true'; then
        # Extrair session_id da resposta
        local session_id=$(echo "$response" | grep -oP '"session_id": "\K[^"]+' || echo "")
        
        if [ -n "$session_id" ]; then
            # Processar com método direto (GERAR_TXT_COMPLETO.sh)
            local tmp_dir="/tmp/ocp_processing/$session_id"
            
            # Copiar arquivos para diretório de entrada
            if [ -f "$tmp_dir/config.json" ] && [ -f "$tmp_dir/input.json" ]; then
                cp "$tmp_dir/config.json" /mnt/c/prd_debian/mapas/in/config_completo.json
                cp "$tmp_dir/input.json" /mnt/c/prd_debian/mapas/in/inputcompleto.json
                
                # Executar geração de TXT
                cd /mnt/c/prd_debian/ocp_wms_core
                source wms_venv/bin/activate
                export PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
                bash GERAR_TXT_COMPLETO.sh >> "$LOG_FILE" 2>&1
                
                # Verificar se TXT foi gerado
                local txt_source="/mnt/c/prd_debian/mapas/out/palletize_result_map_${mapa_num}.txt"
                if [ -f "$txt_source" ]; then
                    cp "$txt_source" "$OUTPUT_BASE/sucesso/${filename}.txt"
                    echo -e "${GREEN}  ✓ Sucesso${NC}" | tee -a "$LOG_FILE"
                    echo "  📄 TXT salvo: sucesso/${filename}.txt" | tee -a "$LOG_FILE"
                    
                    # Copiar arquivos intermediários
                    mkdir -p "$OUTPUT_BASE/sucesso/${filename}_files"
                    cp -r "$tmp_dir"/* "$OUTPUT_BASE/sucesso/${filename}_files/" 2>/dev/null
                    
                    return 0
                else
                    echo -e "${RED}  ✗ Erro: TXT não gerado${NC}" | tee -a "$LOG_FILE"
                    cp "$xml_file" "$OUTPUT_BASE/erro/"
                    echo "TXT não gerado após processamento" > "$OUTPUT_BASE/erro/${filename}_error.log"
                    return 1
                fi
            else
                echo -e "${RED}  ✗ Erro: Arquivos intermediários não encontrados${NC}" | tee -a "$LOG_FILE"
                cp "$xml_file" "$OUTPUT_BASE/erro/"
                echo "config.json ou input.json não encontrado em $tmp_dir" > "$OUTPUT_BASE/erro/${filename}_error.log"
                return 1
            fi
        else
            echo -e "${RED}  ✗ Erro: session_id não encontrado${NC}" | tee -a "$LOG_FILE"
            echo "$response" > "$OUTPUT_BASE/erro/${filename}_error.log"
            cp "$xml_file" "$OUTPUT_BASE/erro/"
            return 1
        fi
    else
        echo -e "${RED}  ✗ Erro na conversão${NC}" | tee -a "$LOG_FILE"
        echo "$response" >> "$OUTPUT_BASE/erro/${filename}_error.log"
        cp "$xml_file" "$OUTPUT_BASE/erro/"
        return 1
    fi
}

export -f processar_xml
export ORCHESTRATOR_URL OUTPUT_BASE LOG_FILE GREEN RED YELLOW BLUE NC

# Contar total de XMLs
TOTAL=$(find "$INPUT_DIR" -name "*.xml" -type f | wc -l)
echo -e "${BLUE}📊 Total de XMLs encontrados:${NC} $TOTAL"
echo ""
echo -e "${GREEN}🚀 Iniciando processamento...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Processar XMLs
if [ "$MAX_PARALLEL" -gt 1 ]; then
    # Processamento paralelo
    echo -e "${YELLOW}⚡ Modo paralelo: $MAX_PARALLEL processos simultâneos${NC}"
    echo ""
    
    find "$INPUT_DIR" -name "*.xml" -type f | \
        xargs -P "$MAX_PARALLEL" -I {} bash -c 'processar_xml "$@"' _ {}
else
    # Processamento sequencial
    current=0
    while IFS= read -r xml_file; do
        current=$((current + 1))
        echo -e "${BLUE}[$current/$TOTAL]${NC}"
        
        if processar_xml "$xml_file"; then
            SUCESSO=$((SUCESSO + 1))
        else
            ERRO=$((ERRO + 1))
        fi
        
        echo ""
    done < <(find "$INPUT_DIR" -name "*.xml" -type f)
fi

# Calcular estatísticas finais
FIM=$(date +%s)
DURACAO=$((FIM - INICIO))
MINUTOS=$((DURACAO / 60))
SEGUNDOS=$((DURACAO % 60))

# Se processamento foi paralelo, contar sucessos/erros
if [ "$MAX_PARALLEL" -gt 1 ]; then
    SUCESSO=$(find "$OUTPUT_BASE/sucesso" -name "*.txt" -type f | wc -l)
    ERRO=$(find "$OUTPUT_BASE/erro" -name "*.xml" -type f | wc -l)
fi

# Relatório final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    RELATÓRIO FINAL                            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Estatísticas:${NC}"
echo "   Total processado: $TOTAL"
echo -e "   ${GREEN}✓ Sucesso: $SUCESSO${NC}"
echo -e "   ${RED}✗ Erro: $ERRO${NC}"
echo ""
echo -e "${BLUE}⏱️  Tempo de execução:${NC} ${MINUTOS}m ${SEGUNDOS}s"
echo -e "${BLUE}⚡ Taxa:${NC} $(echo "scale=2; $TOTAL / $DURACAO" | bc) XMLs/segundo"
echo ""
echo -e "${GREEN}📁 Arquivos gerados:${NC}"
echo "   Sucessos: $OUTPUT_BASE/sucesso/"
echo "   Erros: $OUTPUT_BASE/erro/"
echo "   Logs: $LOG_FILE"
echo ""

# Listar alguns exemplos
if [ $SUCESSO -gt 0 ]; then
    echo -e "${GREEN}📄 Exemplos de TXTs gerados:${NC}"
    find "$OUTPUT_BASE/sucesso" -name "*.txt" -type f | head -5 | while read txt; do
        size=$(du -h "$txt" | cut -f1)
        echo "   $size  $(basename "$txt")"
    done
    echo ""
fi

if [ $ERRO -gt 0 ]; then
    echo -e "${RED}⚠️  XMLs com erro:${NC}"
    find "$OUTPUT_BASE/erro" -name "*.xml" -type f | head -5 | while read xml; do
        echo "   $(basename "$xml")"
    done
    [ $ERRO -gt 5 ] && echo "   ... e mais $((ERRO - 5)) arquivo(s)"
    echo ""
fi

echo -e "${BLUE}✨ Processamento concluído!${NC}"
echo ""
