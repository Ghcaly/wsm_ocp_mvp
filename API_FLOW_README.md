# 🚀 API de Fluxo Completo - OCP Core

API REST que executa todo o fluxo de paletização OCP Core em um único endpoint.

## 📋 Fluxo Executado

```
XML → JSON → Config → Paletização (51 regras) → TXT Completo
```

## 🔧 Componentes

### 1. **WMS Converter** (Porta 8002)
- Converte XML para JSON

### 2. **OCP Complete Flow API** (Porta 5001)
- Executa fluxo completo de paletização
- Gera TXT com todas as informações

## 🚀 Como Usar

### Iniciar API

```bash
cd /home/wms_core/wsm_ocp_mvp/ocp_wms_core/ocp_score-main
./start_complete_api.sh
```

Ou manualmente:

```bash
source /home/wms_core/wms_venv/bin/activate
python api_complete_flow.py
```

### Testar API

```bash
cd /home/wms_core/wsm_ocp_mvp
chmod +x test_api.sh
./test_api.sh
```

## 📡 Endpoints

### 1. Health Check

```bash
GET http://localhost:5001/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "OCP Complete Flow API",
  "version": "1.0.0"
}
```

### 2. Processar XML

```bash
POST http://localhost:5001/process
Content-Type: multipart/form-data
```

**Request:**
- `file`: Arquivo XML do mapa

**Response:**
```json
{
  "success": true,
  "mapa": "448111",
  "files": {
    "json": "/tmp/ocp_results/448111.json",
    "config": "/tmp/ocp_results/448111_config.json",
    "result_json": "/tmp/ocp_results/palletize_result_map_448111.json",
    "txt": "/tmp/ocp_results/448111-ocp-map.txt"
  },
  "statistics": {
    "mounted_spaces": 10,
    "pallets": 10,
    "products": 60,
    "peso_motorista": 4482.22,
    "peso_ajudante": 4408.15,
    "perc_motorista": 50.42,
    "perc_ajudante": 49.58
  }
}
```

### 3. Download TXT

```bash
GET http://localhost:5001/download/{mapa_number}
```

**Exemplo:**
```bash
curl -o resultado.txt http://localhost:5001/download/448111
```

## 📊 Informações no TXT Gerado

O TXT gerado contém:

✅ **Retornável:** GFA 300ML, 600ML, 1L  
✅ **Descartável:** Latas, Long Neck, PET  
✅ **BinPack (Marketplace):** Produtos especiais  
✅ **TopoPallet:** Produtos para topo  
✅ **Chopp:** KEG 30L, 50L  
✅ **Isotônico:** Gatorade, água  
✅ **Grupos/Subgrupos:** Completos  
✅ **Embalagens:** Códigos completos  

## 🎯 Regras Executadas

### Principal Route Chain (2 regras)
- ComplexGroupLoadRule
- FilteredRouteRule

### Route Chain (19 regras)
- BulkPalletRule
- LayerRule
- PalletGroupSubGroupRule
- NonPalletizedProductsRule
- ReturnableAndDisposableSplitRemountRule
- RemountRule
- IsotonicWaterWithoutMinimumOccupationRule
- RecalculatePalletOccupationRule
- E outras...

### Common Chain (13 regras)
- ReassignmentNonPalletizedItemsRule
- NewReorderRule
- SideBalanceRule
- VehicleCapacityOverflowRule
- CalculatorOccupationRule
- E outras...

**Total: 51+ regras executadas**

## 📁 Estrutura de Arquivos

```
/tmp/ocp_results/
├── {mapa}.json                           # JSON convertido do XML
├── {mapa}_config.json                    # Configurações geradas
├── palletize_result_map_{mapa}.json      # Resultado completo
└── {mapa}-ocp-map.txt                    # TXT final
```

## 🧪 Exemplo Completo

```bash
# 1. Processar XML
curl -X POST http://localhost:5001/process \
  -F "file=@/path/to/mapa_448111.xml"

# 2. Baixar resultado
curl -o resultado_448111.txt \
  http://localhost:5001/download/448111

# 3. Ver resultado
cat resultado_448111.txt
```

## ⚙️ Dependências

- Flask
- Flask-CORS
- WMS Converter API (porta 8002)
- Python 3.13+
- Ambiente virtual: `/home/wms_core/wms_venv`

## 📝 Logs

Ver logs da API:

```bash
tail -f /tmp/api_complete.log
```

## 🔄 Reiniciar API

```bash
pkill -f "api_complete_flow.py"
cd /home/wms_core/wsm_ocp_mvp/ocp_wms_core/ocp_score-main
./start_complete_api.sh
```

## ✅ Status

- ✅ API rodando na porta 5001
- ✅ Fluxo completo funcional
- ✅ TXT com todas as informações
- ✅ 51+ regras executadas
- ✅ Balanceamento Motorista/Ajudante
