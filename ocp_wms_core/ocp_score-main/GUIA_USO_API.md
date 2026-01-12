# Guia Rápido: Como Usar a API de Paletização

Guia prático para enviar um XML e receber o TXT processado.

---

## Pré-requisitos

1. APIs rodando (executar uma vez):
```bash
cd /home/wms_core/wsm_ocp_mvp/ocp_wms_core/ocp_score-main
bash start_apis.sh
```

2. Ter um arquivo XML do mapa para processar

---

## Opção 1: Usando cURL (Linha de Comando)

### Passo 1: Enviar XML e Processar

```bash
# Flask API (porta 5001)
curl -X POST http://localhost:5001/process-xml \
  -F "file=@/caminho/do/seu/arquivo.xml" \
  -o resultado.json

# OU FastAPI (porta 8000)
curl -X POST http://localhost:8000/process-xml \
  -F "file=@/caminho/do/seu/arquivo.xml" \
  -o resultado.json
```

**Exemplo real:**
```bash
curl -X POST http://localhost:5001/process-xml \
  -F "file=@/home/wms_core/wms_xml_in/023c4f1b660f49cf86900cc0022df5d1_m_mapa_448111_0970_20260105234547.xml" \
  -o resultado.json
```

### Passo 2: Ver o Resultado

```bash
cat resultado.json | python -m json.tool
```

Você verá algo como:
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
  "download_urls": {
    "txt": "/result/448111",
    "json": "/json/448111"
  }
}
```

### Passo 3: Baixar o TXT Resultado

```bash
# Use o map_number da resposta anterior
curl http://localhost:5001/result/448111 -o mapa_448111_resultado.txt

# Ver o conteúdo
cat mapa_448111_resultado.txt
```

---

## Opção 2: Usando Python

### Script Completo:

```python
#!/usr/bin/env python3
"""
Exemplo: Enviar XML e baixar TXT resultado
"""
import requests
import json

# Configuração
API_URL = "http://localhost:5001"  # Ou 8000 para FastAPI
XML_FILE = "/home/wms_core/wms_xml_in/mapa_448111.xml"

# Passo 1: Upload e processamento do XML
print("Enviando XML para processamento...")

with open(XML_FILE, 'rb') as f:
    files = {'file': (XML_FILE.split('/')[-1], f, 'application/xml')}
    response = requests.post(f'{API_URL}/process-xml', files=files)

# Verifica resposta
if response.status_code == 200:
    result = response.json()
    print("Processamento concluído!")
    print(json.dumps(result, indent=2))
    
    # Passo 2: Baixar o TXT resultado
    map_number = result['map_number']
    print(f"\nBaixando resultado do mapa {map_number}...")
    
    txt_response = requests.get(f'{API_URL}/result/{map_number}')
    
    if txt_response.status_code == 200:
        # Salva o TXT
        output_file = f'mapa_{map_number}_resultado.txt'
        with open(output_file, 'wb') as f:
            f.write(txt_response.content)
        
        print(f"Arquivo salvo: {output_file}")
        
        # Mostra estatísticas
        stats = result['statistics']
        print(f"\nEstatísticas:")
        print(f"   Paletes: {stats['pallets_count']}")
        print(f"   Unidades: {stats['units_palletized']}")
        print(f"   Peso: {stats['total_weight']:.2f} kg")
        print(f"   Tempo: {stats['processing_time']:.2f}s")
    else:
        print(f"Erro ao baixar TXT: {txt_response.status_code}")
else:
    print(f"Erro no processamento: {response.status_code}")
    print(response.text)
```

### Executar:

```bash
chmod +x processar_xml.py
python processar_xml.py
```

---

## Opção 3: Usando JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_URL = 'http://localhost:5001';
const XML_FILE = '/home/wms_core/wms_xml_in/mapa_448111.xml';

async function processarXML() {
    try {
        // Passo 1: Upload e processamento
        console.log('Enviando XML...');
        
        const form = new FormData();
        form.append('file', fs.createReadStream(XML_FILE));
        
        const response = await axios.post(`${API_URL}/process-xml`, form, {
            headers: form.getHeaders()
        });
        
        const result = response.data;
        console.log('Processamento concluído!');
        console.log(JSON.stringify(result, null, 2));
        
        // Passo 2: Baixar TXT
        const mapNumber = result.map_number;
        console.log(`\nBaixando resultado do mapa ${mapNumber}...`);
        
        const txtResponse = await axios.get(`${API_URL}/result/${mapNumber}`, {
            responseType: 'stream'
        });
        
        const outputFile = `mapa_${mapNumber}_resultado.txt`;
        const writer = fs.createWriteStream(outputFile);
        txtResponse.data.pipe(writer);
        
        writer.on('finish', () => {
            console.log(`Arquivo salvo: ${outputFile}`);
            
            // Estatísticas
            const stats = result.statistics;
            console.log('\nEstatísticas:');
            console.log(`   Paletes: ${stats.pallets_count}`);
            console.log(`   Unidades: ${stats.units_palletized}`);
            console.log(`   Peso: ${stats.total_weight.toFixed(2)} kg`);
            console.log(`   Tempo: ${stats.processing_time.toFixed(2)}s`);
        });
        
    } catch (error) {
        console.error('Erro:', error.message);
    }
}

processarXML();
```

---

## Opção 4: Script Bash Completo

Crie um arquivo `processar_mapa.sh`:

```bash
#!/bin/bash

# Configurações
API_URL="http://localhost:5001"
XML_FILE="$1"

if [ -z "$XML_FILE" ]; then
    echo "Uso: $0 <arquivo.xml>"
    exit 1
fi

if [ ! -f "$XML_FILE" ]; then
    echo "Arquivo não encontrado: $XML_FILE"
    exit 1
fi

echo "Enviando XML: $XML_FILE"
echo ""

# Passo 1: Processar XML
RESULT=$(curl -s -X POST "$API_URL/process-xml" \
    -F "file=@$XML_FILE")

# Verifica sucesso
SUCCESS=$(echo "$RESULT" | grep -o '"success": true' | head -1)

if [ -z "$SUCCESS" ]; then
    echo "Erro no processamento:"
    echo "$RESULT" | python -m json.tool
    exit 1
fi

echo "Processamento concluído!"
echo ""

# Extrai informações
MAP_NUMBER=$(echo "$RESULT" | grep -o '"map_number": [0-9]*' | grep -o '[0-9]*')
PALLETS=$(echo "$RESULT" | grep -o '"pallets_count": [0-9]*' | grep -o '[0-9]*')
UNITS=$(echo "$RESULT" | grep -o '"units_palletized": [0-9]*' | grep -o '[0-9]*')

echo "Estatísticas:"
echo "   Mapa: $MAP_NUMBER"
echo "   Paletes: $PALLETS"
echo "   Unidades: $UNITS"
echo ""

# Passo 2: Baixar TXT
OUTPUT_FILE="mapa_${MAP_NUMBER}_resultado.txt"
echo "Baixando resultado..."

curl -s "$API_URL/result/$MAP_NUMBER" -o "$OUTPUT_FILE"

if [ -f "$OUTPUT_FILE" ]; then
    echo "Arquivo salvo: $OUTPUT_FILE"
    echo ""
    echo "Primeiras linhas:"
    head -20 "$OUTPUT_FILE"
else
    echo "Erro ao baixar resultado"
    exit 1
fi
```

### Usar:

```bash
chmod +x processar_mapa.sh
./processar_mapa.sh /home/wms_core/wms_xml_in/mapa_448111.xml
```

---

## Verificar se APIs estão Rodando

```bash
# Flask
curl http://localhost:5001/health

# FastAPI
curl http://localhost:8000/health

# Resposta esperada:
# {"status": "healthy", "services": {"api": "ok", "wms_converter": "ok"}}
```

---

## Exemplo de Resposta Completa

### Resposta JSON do processamento:

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

### Conteúdo do TXT resultado:

```
================================================================
                       PALETIZAÇÃO - MAPA 448111
================================================================

Quantidade de Espaços Montados: 10

----------------------------------------------------------------
                    MOTORISTA (51,29%)
----------------------------------------------------------------
Quantidade: 5 - Peso Total: 2158,66 Kg

----------------------------------------------------------------
P_M_01_1/35 - 14,99 - 27  Peso: 367,19
----------------------------------------------------------------
| 0  972  Skol 300ML GFA  27  1002  10/1002  367,20  Retornavel  14,99 |

----------------------------------------------------------------
P_M_02_1/35 - 14,99 - 32  Peso: 435,20
----------------------------------------------------------------
| 0  972  Skol 300ML GFA  32  1002  10/1002  435,20  Retornavel  14,99 |

...
```

---

## Fluxo Resumido

```
1. Enviar XML via POST /process-xml
   ↓
2. Receber JSON com estatísticas e map_number
   ↓
3. Usar map_number para baixar resultado
   ↓
4. GET /result/{map_number} → baixa o TXT
```

---

## Troubleshooting

### Erro: Connection refused

```bash
# Verificar se APIs estão rodando
ps aux | grep -E "(api_flask|api_fastapi|uvicorn)"

# Reiniciar
bash start_apis.sh
```

### Erro: File not found

```bash
# Verificar caminho do XML
ls -la /caminho/do/arquivo.xml

# Usar caminho absoluto no curl
curl -X POST http://localhost:5001/process-xml \
  -F "file=@$(pwd)/arquivo.xml"
```

### Ver logs em tempo real

```bash
# Flask
tail -f /tmp/flask_api.log

# FastAPI
tail -f /tmp/fastapi.log
```

---

## Documentação Completa

- **Swagger UI (FastAPI)**: http://localhost:8000/docs
- **ReDoc (FastAPI)**: http://localhost:8000/redoc
- **README APIs**: `README_APIS.md`

---

## Exemplo Prático Rápido

```bash
# Tudo em um comando!
curl -X POST http://localhost:5001/process-xml \
  -F "file=@mapa.xml" | \
  python -c "import sys, json; r=json.load(sys.stdin); print(f\"Mapa: {r['map_number']}\"); exit(0)" && \
  curl http://localhost:5001/result/$(cat resultado.json | grep -o '"map_number": [0-9]*' | grep -o '[0-9]*') \
  -o resultado.txt && \
  echo "Pronto! Ver: resultado.txt"
```

---

**Desenvolvido para o Sistema OCP de Paletização**
