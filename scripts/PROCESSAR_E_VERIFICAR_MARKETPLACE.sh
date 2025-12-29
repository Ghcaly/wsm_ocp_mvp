#!/bin/bash
# Script completo: Limpar + Processar + Verificar Marketplace

cd /mnt/c/prd_debian

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     PROCESSAMENTO COMPLETO COM DETECÇÃO MARKETPLACE          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# PASSO 1: LIMPEZA
echo "🧹 [1/4] Limpando outputs antigos..."
rm -f mapas/out/processamento_massa/sucesso/*.txt 2>/dev/null
rm -f mapas/out/processamento_massa/erro/*.txt 2>/dev/null
rm -rf ocp_wms_core/ocp_score-main/data/route/*/output/*.txt 2>/dev/null
rm -rf ocp_wms_core/ocp_score-main/data/route/*/output/*.json 2>/dev/null
echo "   ✓ Outputs limpos"
echo ""

# PASSO 2: CONTAGEM
TOTAL_XMLS=$(ls mapas_xml_saidas_filtrados/*.xml 2>/dev/null | wc -l)
echo "📊 [2/4] XMLs para processar: $TOTAL_XMLS"
echo ""

# PASSO 3: PROCESSAMENTO
echo "⚙️  [3/4] Processando todos os XMLs..."
echo ""
bash ./PROCESSAR_TODOS_AGORA.sh 2>&1 | tee /tmp/processamento_completo.log
echo ""

# PASSO 4: VERIFICAÇÃO
echo "🔍 [4/4] Verificando detecção de produtos marketplace..."
echo ""

# Contar TXTs gerados
SUCESSO=$(ls mapas/out/processamento_massa/sucesso/*.txt 2>/dev/null | wc -l)
ERRO=$(ls mapas/out/processamento_massa/erro/*.txt 2>/dev/null | wc -l)

echo "📈 Resultados do processamento:"
echo "   ✓ Sucesso: $SUCESSO TXTs"
echo "   ✗ Erro: $ERRO TXTs"
echo ""

# Verificar marcação BinPack nos TXTs
echo "🏷️  Verificando marcação 'BinPack' nos TXTs..."
BINPACK_COUNT=$(grep -c "BinPack" mapas/out/processamento_massa/sucesso/*.txt 2>/dev/null | grep -v ':0' | wc -l)
echo "   Arquivos com BinPack: $BINPACK_COUNT"
echo ""

if [ $BINPACK_COUNT -gt 0 ]; then
    echo "✅ MARKETPLACE DETECTADO E MARCADO!"
    echo ""
    echo "Exemplos de produtos marketplace encontrados:"
    grep -h "BinPack" mapas/out/processamento_massa/sucesso/*.txt 2>/dev/null | head -5
else
    echo "⚠️  Nenhum produto marketplace marcado como BinPack"
    echo ""
    echo "Verificando produtos conhecidos (21968, 21973, 27177)..."
    grep -E "21968|21973|27177" mapas/out/processamento_massa/sucesso/*.txt 2>/dev/null | head -3
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    PROCESSAMENTO CONCLUÍDO                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 TXTs em: mapas/out/processamento_massa/sucesso/"
echo "📋 Log completo em: /tmp/processamento_completo.log"
echo ""
