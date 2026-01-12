# 🚀 APIs de Paletização OCP

Sistema completo com **FastAPI** e **Flask** para processamento de mapas XML.

## 📋 Arquivos Criados

### APIs
- **`api_fastapi.py`** - API moderna com FastAPI (async, Swagger docs)
- **`api_flask_complete.py`** - API Flask completa com todos os endpoints
- **`start_apis.sh`** - Script para iniciar todas as APIs
- **`test_apis.sh`** - Script para testar as APIs

## 🌐 Endpoints Disponíveis

### FastAPI (porta 8000)

```bash
# Documentação interativa
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
http://localhost:8000/           # JSON API info
```

#### Endpoints:
- **`GET /`** - Informações da API
- **`GET /health`** - Health check
- **`POST /process-xml`** - Upload e processa XML completo
- **`POST /process-json`** - Processa JSON já convertido
- **`GET /result/{map_number}`** - Download TXT resultado
- **`GET /json/{map_number}`** - Download JSON resultado

### Flask API (porta 5001)

```bash
# API info
http://localhost:5001/
```

#### Endpoints (idênticos ao FastAPI):
- **`GET /`** - Informações da API
- **`GET /health`** - Health check
- **`POST /process-xml`** - Upload e processa XML completo
- **`POST /process-json`** - Processa JSON já convertido
- **`GET /result/<map_number>`** - Download TXT resultado
- **`GET /json/<map_number>`** - Download JSON resultado

### WMS Converter (porta 8002)

- **`POST /convert`** - Converte XML → JSON (usado internamente)

## 🎯 Fluxo Completo

Quando você faz upload de um XML via **`POST /process-xml`**:

```
1. 📤 Upload XML
   ↓
2. 🔄 Converte XML → JSON (WMS Converter)
   ↓
3. ⚙️  Gera configuração automaticamente (ConfigGenerator)
   ↓
4. 🎯 Executa paletização (51 regras)
   ↓
5. 📄 Gera saída TXT profissional (PalletizeTextReport)
   ↓
6. ✅ Retorna resultado com estatísticas
```

## 🚀 Como Usar

### 1. Iniciar as APIs

```bash
cd /home/wms_core/wsm_ocp_mvp/ocp_wms_core/ocp_score-main
bash start_apis.sh
```

Isso inicia:
- ✅ WMS Converter (porta 8002)
- ✅ Flask API (porta 5001)
- ✅ FastAPI (porta 8000)

### 2. Testar o Sistema

```bash
bash test_apis.sh
```

### 3. Processar um XML (Flask)

```bash
curl -X POST http://localhost:5001/process-xml \
  -F "file=@/home/wms_core/wms_xml_in/mapa_448111.xml" \
  | python -m json.tool
```

### 4. Processar um XML (FastAPI)

```bash
curl -X POST http://localhost:8000/process-xml \
  -F "file=@/home/wms_core/wms_xml_in/mapa_448111.xml" \
  | python -m json.tool
```

### 5. Download do Resultado

```bash
# Download TXT
curl http://localhost:5001/result/448111 -o resultado.txt

# Download JSON
curl http://localhost:5001/json/448111 -o resultado.json
```

## 📊 Resposta da API

Exemplo de resposta do **`POST /process-xml`**:

```json
{
  "success": true,
  "map_number": 448111,
  "message": "Processamento concluído com sucesso",
  "statistics": {
    "pallets_count": 10,
    "units_palletized": 302,
    "total_weight": 4209.13,
    "processing_time": 2.45
  },
  "files": {
    "txt": "/tmp/ocp_results/448111-ocp-map.txt",
    "json": "/tmp/ocp_results/448111-ocp-map.json",
    "config": "/tmp/ocp_results/config_448111.json"
  },
  "download_urls": {
    "txt": "/result/448111",
    "json": "/json/448111"
  }
}
```

## 🐍 Usar via Python

### Exemplo FastAPI:

```python
import requests

# Upload e processar
with open('mapa.xml', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/process-xml', files=files)
    
result = response.json()
print(f"Paletes: {result['statistics']['pallets_count']}")
print(f"Unidades: {result['statistics']['units_palletized']}")

# Download resultado
map_number = result['map_number']
txt_response = requests.get(f'http://localhost:8000/result/{map_number}')
with open('resultado.txt', 'wb') as f:
    f.write(txt_response.content)
```

### Exemplo Flask:

```python
import requests

# Upload e processar
with open('mapa.xml', 'rb') as f:
    files = {'file': ('mapa.xml', f, 'application/xml')}
    response = requests.post('http://localhost:5001/process-xml', files=files)
    
result = response.json()

if result['success']:
    print(f"✅ {result['message']}")
    print(f"📦 {result['statistics']['pallets_count']} paletes")
    print(f"📊 {result['statistics']['units_palletized']} unidades")
    print(f"⚖️  {result['statistics']['total_weight']} kg")
    print(f"⏱️  {result['statistics']['processing_time']}s")
else:
    print(f"❌ Erro: {result['error']}")
```

## 📝 Logs

Acompanhar logs em tempo real:

```bash
# Flask API
tail -f /tmp/flask_api.log

# FastAPI
tail -f /tmp/fastapi.log

# WMS Converter
tail -f /tmp/wms_converter.log
```

## 🔧 Parar as APIs

```bash
# Parar Flask
pkill -f "api_flask_complete.py"

# Parar FastAPI
pkill -f "uvicorn"
pkill -f "api_fastapi.py"

# Parar WMS Converter
pkill -f "wms_converter.*api.py"
```

## 📂 Arquivos de Saída

Todos os resultados são salvos em:

```
/tmp/ocp_results/
├── 448111_input.json          # JSON convertido do XML
├── config_448111.json          # Configuração gerada
├── 448111-ocp-map.json         # Resultado JSON
└── 448111-ocp-map.txt          # Resultado TXT (formato profissional)
```

## ✨ Vantagens

### FastAPI (Porta 8000)
- ✅ **Async/Await** - Performance superior
- ✅ **Swagger UI** - Documentação interativa automática
- ✅ **Validação automática** - Pydantic models
- ✅ **Typing** - Type hints nativos
- ✅ **ReDoc** - Documentação alternativa

### Flask (Porta 5001)
- ✅ **Simplicidade** - Código mais direto
- ✅ **Compatibilidade** - Amplamente usado
- ✅ **Flexibilidade** - Fácil customização
- ✅ **Maduro** - Ecossistema estabelecido

## 🎯 Melhorias Implementadas

Ambas as APIs implementam o **fluxo completo**:

1. ✅ Upload de arquivo XML
2. ✅ Conversão XML → JSON automática
3. ✅ Geração de configuração inteligente
4. ✅ Processamento com 51 regras de paletização
5. ✅ Saída TXT profissional com todos os atributos
6. ✅ Download de resultados
7. ✅ Estatísticas detalhadas
8. ✅ Health checks
9. ✅ Logs estruturados
10. ✅ Tratamento de erros robusto

## 🔍 Troubleshooting

### Porta já em uso

```bash
# Ver o que está usando a porta
lsof -i :8000
lsof -i :5001

# Matar processo
kill -9 <PID>
```

### API não responde

```bash
# Ver logs
tail -f /tmp/fastapi.log
tail -f /tmp/flask_api.log

# Reiniciar
bash start_apis.sh
```

### WMS Converter offline

```bash
# Verificar status
curl http://localhost:8002/

# Reiniciar manualmente
cd /home/wms_core/wsm_ocp_mvp/wms_converter
source /home/wms_core/wms_venv/bin/activate
python api.py
```

## 📖 Documentação Adicional

- **FastAPI Docs**: http://localhost:8000/docs
- **FastAPI ReDoc**: http://localhost:8000/redoc
- **Código fonte**: `api_fastapi.py`, `api_flask_complete.py`

---

**Desenvolvido com ❤️ para o sistema OCP de Paletização**
