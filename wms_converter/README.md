# WMS Converter

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Conversor modular de XML (ocpEntrega/ocpOrtec) para JSON com CLI e API REST para sistemas WMS.

## Caracteristicas

- Conversao XML para JSON com estrutura customizada
- API REST com FastAPI
- CLI para processamento em lote
- Suporte a multiplos formatos de entrada
- Validacao e formatacao automatica
- Documentacao interativa Swagger/OpenAPI

## Instalacao

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

### CLI - Arquivo unico

```bash
python convert.py -i arquivo.xml -o saida.json
```

### CLI - Processamento em lote

```bash
python convert.py -i pasta_xml/ -o pasta_json/
```

### Scripts prontos

```bash
# Processar arquivo especifico
./convert_map.sh

# Processar todos XMLs da pasta
./process_all.sh
```

### API REST

#### Iniciar servidor

```bash
python api.py
```

ou com auto-reload:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

#### Endpoints disponiveis

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| GET | / | Info da API |
| GET | /health | Health check |
| POST | /convert | Upload de arquivo XML |
| POST | /convert/raw | XML como texto |

#### Exemplo com curl

```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@arquivo.xml" \
  -F "unbcode=916"
```

#### Exemplo com Python

```python
import requests

with open('arquivo.xml', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/convert',
        files={'file': f}
    )
    print(response.json())
```

## Documentacao interativa

Acesse a documentacao Swagger em: `http://localhost:8000/docs`

## Estrutura do projeto

```
wms_converter/
├── api.py                  # API REST FastAPI
├── convert.py              # CLI principal
├── convert_map.sh          # Script arquivo unico
├── process_all.sh          # Script lote
├── requirements.txt        # Dependencias
├── README.md              # Documentacao
└── modules/
    ├── converter.py       # Logica de conversao
    ├── cli.py             # Argumentos CLI
    ├── file_handler.py    # Gerenciamento arquivos
    ├── output.py          # Mensagens formatadas
    └── api_service.py     # Service API
```

## Opcoes CLI

| Opcao | Descricao |
|-------|-----------|
| --unique-key | Forcar valor UniqueKey |
| --unbcode | Forcar Warehouse.UnbCode |
| --delivery-date | Forcar DeliveryDate (ISO) |
| --plate | Forcar Vehicle.Plate |
| --support-point | Forcar Cross.SupportPoint |

## Formato de saida

```json
{
  "Type": 1,
  "Number": "621622",
  "DeliveryDate": "2025-12-03T00:00:00",
  "Warehouse": {
    "UnbCode": "916",
    "FileName": "arquivo.xml",
    "Company": "029",
    "Branch": "0916"
  },
  "Vehicle": {
    "Plate": "ABC1234",
    "Bays": []
  },
  "Orders": [],
  "UniqueKey": "hash"
}
```

## Tecnologias

- Python 3.13
- FastAPI 0.109.0
- Uvicorn 0.27.0
- ElementTree XML Parser

## Licenca

MIT
