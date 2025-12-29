# 🚀 Como Executar o Projeto

## ✅ Paths Corrigidos
Todos os scripts foram atualizados para usar `/mnt/c/prd_debian` (WSL paths).

## 📋 Passo a Passo

### 1️⃣ Abrir WSL/Bash
```bash
# No PowerShell do VS Code, digite:
bash
```

### 2️⃣ Iniciar as APIs (em terminais separados)

#### Terminal 1 - WMS Converter (porta 8000)
```bash
cd /mnt/c/prd_debian/wms_converter
source venv/bin/activate
python api.py
```

#### Terminal 2 - WMS Boxing (porta 8001)
```bash
cd /mnt/c/prd_debian/wms-itemsboxing
source venv/bin/activate
python src/app.py
```

#### Terminal 3 - OCP Core (porta 5000 e 9000)
```bash
cd /mnt/c/prd_debian/ocp_wms_core
source wms_venv/bin/activate
export PYTHONPATH=/mnt/c/prd_debian/ocp_wms_core/ocp_score-main:$PYTHONPATH
cd ocp_score-main
python master_orchestrator.py
```

### 3️⃣ Processar seus XMLs (em um novo terminal)

Aguarde ~30 segundos para as APIs iniciarem, então:

```bash
cd /mnt/c/prd_debian
./PROCESSAR_MEUS_XMLS.sh
```

## 📊 Status Atual

- **XMLs encontrados**: 115 arquivos em `meus_xmls/`
- **Output**: Resultados em `mapas/out/processamento_massa/sucesso/`

## 🔍 Verificar se APIs estão rodando

```bash
curl http://localhost:8000/health  # WMS Converter
curl http://localhost:8001/health  # WMS Boxing
```

## ⚡ Alternativa: Script Automático

Se preferir iniciar tudo de uma vez (em background):

```bash
cd /mnt/c/prd_debian
./start_all.sh
# Aguarde 15 segundos
./PROCESSAR_MEUS_XMLS.sh
```

## 📁 Resultados

Após o processamento, os TXTs estarão em:
```
c:\prd_debian\mapas\out\processamento_massa\sucesso\
```
