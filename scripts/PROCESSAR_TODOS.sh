#!/bin/bash
# Processar todos os 65 XMLs do diretório de testes

echo "🚀 Processando 65 XMLs..."
echo "⏱️  Tempo estimado: ~10-15 minutos"
echo ""

cd /mnt/c/prd_debian
./processar_massa_simples.sh /mnt/c/prd_debian/BinPacking/src/tests/samples/mapas_backtest

echo ""
echo "✅ Processamento concluído!"
echo "📁 Resultados em: /mnt/c/prd_debian/mapas/out/processamento_massa/"
