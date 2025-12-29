#!/bin/bash
# =============================================================================
# Script para gerar relatório TXT COMPLETO de paletização
# =============================================================================
#
# Este script utiliza o código existente em adapters/palletize_text_report.py
# para gerar o relatório TXT no formato correto.
#
# Uso:
#   ./GERAR_TXT_COMPLETO.sh
#
# Arquivos de entrada esperados:
#   /mnt/c/prd_debian/mapas/in/config_completo.json
#   /mnt/c/prd_debian/mapas/in/inputcompleto.json
#
# Arquivo de saída:
#   /mnt/c/prd_debian/mapas/out/palletize_result_map_*.txt
# =============================================================================

set -e  # Para se houver erro

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║           GERADOR DE RELATÓRIO TXT COMPLETO - PALETIZAÇÃO                 ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Diretórios
MAPAS_IN="/mnt/c/prd_debian/mapas/in"
MAPAS_OUT="/mnt/c/prd_debian/mapas/out"
OCP_DIR="/mnt/c/prd_debian/ocp_wms_core/ocp_score-main"
WORK_DIR="$OCP_DIR/data/route/620768"

# Ativa ambiente virtual
echo "📦 Ativando ambiente virtual..."
cd /mnt/c/prd_debian/ocp_wms_core
source wms_venv/bin/activate

# Verifica dependências
echo "🔍 Verificando dependências..."
python3 -c "import pandas, multipledispatch" 2>/dev/null || {
    echo "   📥 Instalando dependências faltantes..."
    pip install -q pandas multipledispatch
}
echo "   ✓ Dependências OK"
echo ""

# Verifica arquivos de entrada
echo "📁 Verificando arquivos de entrada..."
if [ ! -f "$MAPAS_IN/config_completo.json" ]; then
    echo "❌ Erro: Arquivo não encontrado: $MAPAS_IN/config_completo.json"
    exit 1
fi

if [ ! -f "$MAPAS_IN/inputcompleto.json" ]; then
    echo "❌ Erro: Arquivo não encontrado: $MAPAS_IN/inputcompleto.json"
    exit 1
fi
echo "   ✓ config_completo.json"
echo "   ✓ inputcompleto.json"
echo ""

# Prepara diretório de trabalho
echo "🔧 Preparando ambiente..."
mkdir -p "$WORK_DIR"
mkdir -p "$OCP_DIR/data"
mkdir -p "$MAPAS_OUT"

# Copia arquivos para onde o código espera
cp "$MAPAS_IN/config_completo.json" "$WORK_DIR/config.json"
cp "$MAPAS_IN/inputcompleto.json" "$WORK_DIR/input.json"

# Copia CSV de itens se necessário
if [ ! -f "$OCP_DIR/data/csv-itens_17122025.csv" ]; then
    cp "$OCP_DIR/database/itens.csv" "$OCP_DIR/data/csv-itens_17122025.csv"
fi
echo "   ✓ Ambiente preparado"
echo ""

# Executa processamento
echo "⚙️  Executando processamento de paletização..."
echo "   (Aguarde, isso pode levar alguns instantes...)"
echo ""

cd /mnt/c/prd_debian/ocp_wms_core

# Executa como módulo Python (única forma que funciona com imports relativos)
python3 -m ocp_score-main.service.palletizing_processor 2>&1 | grep -E "^(✓|❌|📊|📁|Mapa:|Produtos:|ERROR|WARNING)" || true

# Verifica se o TXT foi gerado
TXT_FILE=$(ls -t "$WORK_DIR/output/"*.txt 2>/dev/null | head -1)

if [ -z "$TXT_FILE" ]; then
    echo ""
    echo "❌ Erro: Arquivo TXT não foi gerado"
    echo "   Verifique os logs acima para mais detalhes"
    exit 1
fi

# Copia para mapas/out
OUTPUT_NAME=$(basename "$TXT_FILE")
cp "$TXT_FILE" "$MAPAS_OUT/$OUTPUT_NAME"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                          ✅ CONCLUÍDO COM SUCESSO!                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📄 Relatório TXT gerado:"
echo "   $MAPAS_OUT/$OUTPUT_NAME"
echo ""
echo "📊 Estatísticas do arquivo:"
ls -lh "$MAPAS_OUT/$OUTPUT_NAME"
echo ""
echo "📋 Primeiras linhas do relatório:"
head -10 "$MAPAS_OUT/$OUTPUT_NAME"
echo ""
echo "Para ver o arquivo completo:"
echo "   cat $MAPAS_OUT/$OUTPUT_NAME"
echo ""
