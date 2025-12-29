#!/bin/bash

# Script de validação em massa: XML ORTEC vs TXT gerado
# Compara todos os XMLs ORTEC com os TXTs gerados

PASTA_XML="${1:-/mnt/c/prd_debian/mapas_xml_saidas}"
PASTA_TXT="${2:-/mnt/c/prd_debian/mapas/out/processamento_massa/sucesso}"
RELATORIO_DIR="/mnt/c/prd_debian/mapas/out/relatorios_validacao"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RELATORIO_CONSOLIDADO="$RELATORIO_DIR/validacao_consolidada_$TIMESTAMP.md"

# Criar diretório de relatórios
mkdir -p "$RELATORIO_DIR"

# Contadores
TOTAL_XMLS=0
PROCESSADOS=0
SUCESSOS=0
FALHAS=0
NAO_ENCONTRADOS=0

# Arrays para rastreamento
declare -a MAPAS_OK
declare -a MAPAS_DIFF
declare -a MAPAS_NAO_ENCONTRADOS

# Banner
clear
cat << EOF
╔═══════════════════════════════════════════════════════════════╗
║     VALIDAÇÃO EM MASSA: XML ORTEC vs TXT GERADO              ║
╚═══════════════════════════════════════════════════════════════╝

📁 Pasta XMLs: $PASTA_XML
📁 Pasta TXTs: $PASTA_TXT
📄 Relatório: $RELATORIO_CONSOLIDADO

EOF

# Contar XMLs
TOTAL_XMLS=$(find "$PASTA_XML" -name "*.xml" | wc -l)
echo "📊 Total de XMLs encontrados: $TOTAL_XMLS"
echo ""
echo "🚀 Iniciando validação..."
echo ""

# Iniciar relatório consolidado em Markdown
cat > "$RELATORIO_CONSOLIDADO" << 'EOF'
# 📊 RELATÓRIO DE VALIDAÇÃO - XML ORTEC vs TXT GERADO

EOF

echo "**Data:** $(date '+%Y-%m-%d %H:%M:%S')  " >> "$RELATORIO_CONSOLIDADO"
echo "**Pasta XMLs:** \`$PASTA_XML\`  " >> "$RELATORIO_CONSOLIDADO"
echo "**Pasta TXTs:** \`$PASTA_TXT\`  " >> "$RELATORIO_CONSOLIDADO"
echo "**Total XMLs:** $TOTAL_XMLS" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"
echo "---" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"
echo "## 📋 Resultados por Mapa" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"

# Processar cada XML
for XML_FILE in "$PASTA_XML"/*.xml; do
    [ ! -f "$XML_FILE" ] && continue
    
    BASENAME=$(basename "$XML_FILE")
    HASH=$(echo "$BASENAME" | cut -d'_' -f1)
    MAPA_NUM=$(echo "$BASENAME" | grep -oP 'ocp_\K\d+' || echo "UNKNOWN")
    
    # Encontrar TXT correspondente
    TXT_FILE=$(find "$PASTA_TXT" -name "${HASH}_*.txt" | head -1)
    
    if [ ! -f "$TXT_FILE" ]; then
        NAO_ENCONTRADOS=$((NAO_ENCONTRADOS + 1))
        MAPAS_NAO_ENCONTRADOS+=("$MAPA_NUM")
        
        echo "" >> "$RELATORIO_CONSOLIDADO"
        echo "### ❌ Mapa $MAPA_NUM - TXT NÃO ENCONTRADO" >> "$RELATORIO_CONSOLIDADO"
        echo "" >> "$RELATORIO_CONSOLIDADO"
        echo "- **XML:** \`$BASENAME\`" >> "$RELATORIO_CONSOLIDADO"
        echo "- **Status:** TXT correspondente não encontrado" >> "$RELATORIO_CONSOLIDADO"
        echo "" >> "$RELATORIO_CONSOLIDADO"
        continue
    fi
    
    PROCESSADOS=$((PROCESSADOS + 1))
    
    echo "[$PROCESSADOS/$TOTAL_XMLS] Validando Mapa $MAPA_NUM..."
    
    # Executar comparação
    TEMP_RESULT="/tmp/comparacao_$MAPA_NUM.txt"
    python3 /mnt/c/prd_debian/comparar_xml_txt.py "$XML_FILE" "$TXT_FILE" > "$TEMP_RESULT" 2>&1
    
    # Extrair métricas do resultado
    SKU_ACC=$(grep "SKUs Idênticos:" "$TEMP_RESULT" | grep -oP '\d+\.\d+%' || echo "0.0%")
    DIFF_UN=$(grep "Diferença de Unidades:" "$TEMP_RESULT" | grep -oP '[+-]\d+' || echo "0")
    DIFF_PCT=$(grep "Diferença de Unidades:" "$TEMP_RESULT" | grep -oP '[+-]\d+\.\d+%' | tail -1 || echo "0.0%")
    TOTAL_XML=$(grep "Unidades Total" "$TEMP_RESULT" | awk '{print $3}' | head -1 || echo "0")
    TOTAL_TXT=$(grep "Unidades Total" "$TEMP_RESULT" | awk '{print $4}' | head -1 || echo "0")
    
    # Extrair SKUs com problemas
    SKUS_PROBLEMA=$(grep -A 20 "SKUs com Diferenças:" "$TEMP_RESULT" | grep "⚠️\|❌" | head -5 || echo "")
    
    # Verificar se é sucesso (>= 80% de precisão)
    SKU_NUM=$(echo "$SKU_ACC" | sed 's/%//')
    
    if (( $(echo "$SKU_NUM >= 80" | bc -l) )); then
        SUCESSOS=$((SUCESSOS + 1))
        MAPAS_OK+=("$MAPA_NUM:$SKU_ACC")
        STATUS="✅"
        STATUS_TEXT="APROVADO"
    else
        FALHAS=$((FALHAS + 1))
        MAPAS_DIFF+=("$MAPA_NUM:$SKU_ACC")
        STATUS="❌"
        STATUS_TEXT="DIVERGENTE"
    fi
    
    # Adicionar ao relatório consolidado com mais detalhes
    echo "" >> "$RELATORIO_CONSOLIDADO"
    echo "### $STATUS Mapa $MAPA_NUM - $STATUS_TEXT" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    echo "| Métrica | Valor |" >> "$RELATORIO_CONSOLIDADO"
    echo "|---------|-------|" >> "$RELATORIO_CONSOLIDADO"
    echo "| **Precisão SKUs** | $SKU_ACC |" >> "$RELATORIO_CONSOLIDADO"
    echo "| **Unidades XML** | $TOTAL_XML |" >> "$RELATORIO_CONSOLIDADO"
    echo "| **Unidades TXT** | $TOTAL_TXT |" >> "$RELATORIO_CONSOLIDADO"
    echo "| **Diferença** | $DIFF_UN ($DIFF_PCT) |" >> "$RELATORIO_CONSOLIDADO"
    
    if [ "$STATUS" = "❌" ] && [ -n "$SKUS_PROBLEMA" ]; then
        echo "" >> "$RELATORIO_CONSOLIDADO"
        echo "**🔍 Diagnóstico - Principais Divergências:**" >> "$RELATORIO_CONSOLIDADO"
        echo "\`\`\`" >> "$RELATORIO_CONSOLIDADO"
        echo "$SKUS_PROBLEMA" >> "$RELATORIO_CONSOLIDADO"
        echo "\`\`\`" >> "$RELATORIO_CONSOLIDADO"
    fi
    echo "" >> "$RELATORIO_CONSOLIDADO"
    
    # Salvar relatório individual
    RELATORIO_IND="$RELATORIO_DIR/mapa_${MAPA_NUM}_validacao.txt"
    cp "$TEMP_RESULT" "$RELATORIO_IND"
    rm -f "$TEMP_RESULT"
done

# Adicionar resumo ao relatório consolidado
if [ $PROCESSADOS -gt 0 ]; then
    if [ $SUCESSOS -gt 0 ]; then
        PERC_SUCESSO=$(echo "scale=1; $SUCESSOS * 100 / $PROCESSADOS" | bc)
    else
        PERC_SUCESSO="0.0"
    fi
    PERC_FALHAS=$(echo "scale=1; $FALHAS * 100 / $PROCESSADOS" | bc)
    PERC_NAO_ENC=$(echo "scale=1; $NAO_ENCONTRADOS * 100 / $TOTAL_XMLS" | bc)
else
    PERC_SUCESSO="0.0"
    PERC_FALHAS="0.0"
    PERC_NAO_ENC="0.0"
fi

cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## 📈 RESUMO GERAL

EOF

echo "| Métrica | Quantidade | Percentual |" >> "$RELATORIO_CONSOLIDADO"
echo "|---------|------------|------------|" >> "$RELATORIO_CONSOLIDADO"
echo "| **Total Processados** | $PROCESSADOS | 100% |" >> "$RELATORIO_CONSOLIDADO"
echo "| ✅ **Aprovados (≥80%)** | $SUCESSOS | ${PERC_SUCESSO}% |" >> "$RELATORIO_CONSOLIDADO"
echo "| ❌ **Com Divergências** | $FALHAS | ${PERC_FALHAS}% |" >> "$RELATORIO_CONSOLIDADO"
echo "| ⚠️  **TXT Não Encontrado** | $NAO_ENCONTRADOS | ${PERC_NAO_ENC}% |" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"
echo "### 🎯 Taxa de Aprovação: **${PERC_SUCESSO}%**" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"
echo "---" >> "$RELATORIO_CONSOLIDADO"
echo "" >> "$RELATORIO_CONSOLIDADO"

# Listar mapas OK
if [ ${#MAPAS_OK[@]} -gt 0 ]; then
    cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'
## ✅ MAPAS APROVADOS (Precisão ≥80%)

EOF
    echo "Total: ${#MAPAS_OK[@]} mapas" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    for mapa in "${MAPAS_OK[@]}"; do
        MAPA_NUM=$(echo "$mapa" | cut -d':' -f1)
        PRECISAO=$(echo "$mapa" | cut -d':' -f2)
        echo "- **Mapa $MAPA_NUM**: $PRECISAO" >> "$RELATORIO_CONSOLIDADO"
    done
    echo "" >> "$RELATORIO_CONSOLIDADO"
fi

# Listar mapas com divergências
if [ ${#MAPAS_DIFF[@]} -gt 0 ]; then
    cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## ❌ MAPAS COM DIVERGÊNCIAS (Precisão menor que 80%)

EOF
    echo "Total: ${#MAPAS_DIFF[@]} mapas" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    echo "**⚠️  Estes mapas requerem atenção e revisão!**" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    for mapa in "${MAPAS_DIFF[@]}"; do
        MAPA_NUM=$(echo "$mapa" | cut -d':' -f1)
        PRECISAO=$(echo "$mapa" | cut -d':' -f2)
        echo "- **Mapa $MAPA_NUM**: $PRECISAO ⚠️" >> "$RELATORIO_CONSOLIDADO"
    done
    echo "" >> "$RELATORIO_CONSOLIDADO"
fi

# Listar mapas não encontrados
if [ ${#MAPAS_NAO_ENCONTRADOS[@]} -gt 0 ]; then
    cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## ⚠️  MAPAS SEM TXT CORRESPONDENTE

EOF
    echo "Total: ${#MAPAS_NAO_ENCONTRADOS[@]} mapas" >> "$RELATORIO_CONSOLIDADO"
    echo "" >> "$RELATORIO_CONSOLIDADO"
    for mapa in "${MAPAS_NAO_ENCONTRADOS[@]}"; do
        echo "- Mapa $mapa" >> "$RELATORIO_CONSOLIDADO"
    done
    echo "" >> "$RELATORIO_CONSOLIDADO"
fi

cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## 📂 Arquivos Gerados

EOF
echo "- **Relatório consolidado**: \`$RELATORIO_CONSOLIDADO\`" >> "$RELATORIO_CONSOLIDADO"
echo "- **Relatórios individuais**: \`$RELATORIO_DIR/mapa_*_validacao.txt\`" >> "$RELATORIO_CONSOLIDADO"

cat >> "$RELATORIO_CONSOLIDADO" << 'EOF'

---

## 🔍 Diagnóstico Geral

### Tipos de Divergências Comuns:

1. **SKUs Faltando no TXT** - Produtos que aparecem no XML mas não no TXT gerado
   - Geralmente são produtos TopoPallet (chicletes, balas, pequenos itens)
   
2. **Diferenças de Quantidade** - Quantidades divergentes entre XML e TXT
   - Podem indicar problemas no processamento ou arredondamento

3. **Produtos Fora do Caminhão** - Itens que não couberam na paletização
   - Verificar se estão corretamente identificados na seção "fora do caminhão"

### Recomendações:

- ✅ Mapas com **≥95%** de precisão: Excelente, sem ação necessária
- ⚠️  Mapas com **80-94%** de precisão: Revisar diferenças específicas
- ❌ Mapas com **menos de 80%** de precisão: Investigar causa raiz e reprocessar

---

EOF
echo "**Gerado em:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$RELATORIO_CONSOLIDADO"

echo ""
echo "📄 Relatório consolidado: $RELATORIO_CONSOLIDADO"
echo "📂 Relatórios individuais: $RELATORIO_DIR/mapa_*_validacao.txt"
echo ""
echo "✅ Validação concluída!"
