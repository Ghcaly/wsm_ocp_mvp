# 📦 Processamento em Massa de XMLs

Script para processar múltiplos XMLs de paletização de uma só vez.

## 🚀 Uso Rápido

### Processamento Sequencial (1 por vez)
```bash
cd /home/prd_debian
./processar_xmls_massa.sh
```

### Processamento Paralelo (múltiplos simultâneos)
```bash
# Processar 5 XMLs ao mesmo tempo
./processar_xmls_massa.sh /caminho/dos/xmls 5

# Processar 10 XMLs ao mesmo tempo (mais rápido)
./processar_xmls_massa.sh /caminho/dos/xmls 10
```

## 📝 Parâmetros

```bash
./processar_xmls_massa.sh [DIRETÓRIO_ENTRADA] [PROCESSOS_PARALELOS]
```

- **DIRETÓRIO_ENTRADA** (opcional): Pasta com XMLs
  - Padrão: `/home/prd_debian/BinPacking/src/tests/samples/mapas_backtest`
  
- **PROCESSOS_PARALELOS** (opcional): Quantos XMLs processar ao mesmo tempo
  - Padrão: `1` (sequencial)
  - Recomendado: `5-10` para melhor performance

## 📂 Estrutura de Saída

```
/home/prd_debian/mapas/out/processamento_massa/
├── sucesso/                          # XMLs processados com sucesso
│   ├── m_mapa_965635.txt            # TXT de paletização
│   ├── m_mapa_965711.txt
│   ├── m_mapa_965635_files/         # Arquivos intermediários (JSON, config)
│   └── ...
├── erro/                             # XMLs que falharam
│   ├── m_mapa_XXXXX.xml             # XML original
│   └── m_mapa_XXXXX_error.log       # Log do erro
└── logs/
    └── processamento_YYYYMMDD_HHMMSS.log  # Log completo
```

## 📊 O que o Script Faz

1. **Verifica APIs** - Confirma que Master Orchestrator está rodando
2. **Processa XMLs** - Para cada XML:
   - Converte XML → JSON (via wms_converter)
   - Gera config do database
   - Detecta produtos marketplace
   - Aplica boxing se necessário
   - Executa paletização com 48 regras
   - Gera TXT formatado
3. **Organiza Resultados** - Separa sucessos e erros
4. **Gera Relatório** - Estatísticas e tempo de execução

## ✅ Pré-requisitos

Certifique-se que as APIs estão rodando:

```bash
# Verificar status
curl http://localhost:9000/health  # Master Orchestrator
curl http://localhost:8000/health  # Converter
curl http://localhost:8001/health  # Boxing
curl http://localhost:5000/health  # Paletization
```

### Subir APIs se necessário:

```bash
# Master Orchestrator (porta 9000)
cd /home/prd_debian/ocp_wms_core/ocp_score-main
source ../wms_venv/bin/activate
nohup python master_orchestrator.py > /tmp/orchestrator.log 2>&1 &

# Converter (porta 8000)
cd /home/prd_debian/wms_converter
source venv/bin/activate
nohup uvicorn api:app --host 0.0.0.0 --port 8000 > /tmp/converter.log 2>&1 &

# Boxing (porta 8001)
cd /home/prd_debian/wms-itemsboxing/src
source ../venv/bin/activate
nohup python app.py > /tmp/boxing.log 2>&1 &

# Paletization (porta 5000)
cd /home/prd_debian/ocp_wms_core/ocp_score-main
source ../wms_venv/bin/activate
export PYTHONPATH=/home/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
nohup python api_server.py > /tmp/paletization.log 2>&1 &
```

## 🎯 Exemplos

### Processar XMLs de teste (sequencial)
```bash
./processar_xmls_massa.sh
```

### Processar diretório específico (5 paralelos)
```bash
./processar_xmls_massa.sh /home/prd_debian/mapas/in/xml 5
```

### Processar com alta performance (10 paralelos)
```bash
./processar_xmls_massa.sh /caminho/xmls 10
```

## 📈 Performance

- **Sequencial (1)**: ~10-15 segundos por XML
- **Paralelo (5)**: ~3-4 segundos por XML (média)
- **Paralelo (10)**: ~2-3 segundos por XML (média)

Para 184 XMLs:
- Sequencial: ~30-45 minutos
- 5 paralelos: ~10-15 minutos
- 10 paralelos: ~5-10 minutos

## 🔍 Monitoramento

### Ver progresso em tempo real:
```bash
# Em outro terminal
tail -f /home/prd_debian/mapas/out/processamento_massa/logs/processamento_*.log
```

### Contar sucessos:
```bash
ls /home/prd_debian/mapas/out/processamento_massa/sucesso/*.txt | wc -l
```

### Ver erros:
```bash
ls /home/prd_debian/mapas/out/processamento_massa/erro/
```

## 🐛 Troubleshooting

### "Master Orchestrator não está rodando"
```bash
cd /home/prd_debian/ocp_wms_core/ocp_score-main
source ../wms_venv/bin/activate
python master_orchestrator.py
```

### Processos travados
```bash
# Ver processos Python
ps aux | grep python

# Matar processos se necessário
pkill -f master_orchestrator
```

### Limpar resultados anteriores
```bash
rm -rf /home/prd_debian/mapas/out/processamento_massa/*
```

## 📋 Checklist Rápido

- [ ] APIs rodando (verificar com curl)
- [ ] Diretório com XMLs existe
- [ ] Espaço em disco suficiente (~50MB por 100 XMLs)
- [ ] Script tem permissão de execução (`chmod +x`)

## 💡 Dicas

1. **Use processamento paralelo** para muitos XMLs (5-10 processos)
2. **Monitore o log** em tempo real com `tail -f`
3. **Verifique erros** na pasta `erro/` após processar
4. **Backup XMLs importantes** antes de processar em massa

## 🎨 Output do Script

```
╔═══════════════════════════════════════════════════════════════╗
║        Processamento em Massa de XMLs - Paletização          ║
╔═══════════════════════════════════════════════════════════════╗

📁 Diretório de entrada: /path/to/xmls
📂 Diretório de saída: /home/prd_debian/mapas/out/processamento_massa
📋 Arquivo de log: processamento_massa/logs/processamento_20251222_163045.log
⚙️  Processos paralelos: 5

✅ Master Orchestrator: Online

📊 Total de XMLs encontrados: 184

🚀 Iniciando processamento...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[16:30:45] Processando: m_mapa_965635
  ✓ Sucesso
  📄 TXT salvo: sucesso/m_mapa_965635.txt

[16:30:52] Processando: m_mapa_965711
  ✓ Sucesso
  📄 TXT salvo: sucesso/m_mapa_965711.txt

...

╔═══════════════════════════════════════════════════════════════╗
║                    RELATÓRIO FINAL                            ║
╚═══════════════════════════════════════════════════════════════╝

📊 Estatísticas:
   Total processado: 184
   ✓ Sucesso: 180
   ✗ Erro: 4

⏱️  Tempo de execução: 12m 34s
⚡ Taxa: 0.24 XMLs/segundo

📁 Arquivos gerados:
   Sucessos: processamento_massa/sucesso/
   Erros: processamento_massa/erro/
   Logs: processamento_massa/logs/processamento_20251222_163045.log

✨ Processamento concluído!
```
