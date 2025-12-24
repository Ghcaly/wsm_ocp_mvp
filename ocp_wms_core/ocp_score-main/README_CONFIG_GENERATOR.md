# Gerador de Configuração e Processo de Paletização

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Status](https://img.shields.io/badge/Status-Production-green)
![License](https://img.shields.io/badge/License-Internal-red)

Este documento descreve o fluxo completo de geração de configuração e processamento de mapas de paletização.

## Índice

1. [Visão Geral](#visão-geral)
2. [Módulo config_generator.py](#módulo-config_generatorpy)
3. [Fluxo Completo](#fluxo-completo)
4. [Estrutura de Arquivos](#estrutura-de-arquivos)
5. [Comandos e Exemplos](#comandos-e-exemplos)
6. [Detalhes Técnicos](#detalhes-técnicos)

---

## Visão Geral

O sistema agora automatiza completamente a geração de arquivos de configuração (`config.json`) a partir de:
- **Arquivo de entrada** (`input.json`)
- **Database CSVs** (`database/Warehouse.csv`, `database/WarehouseConfiguration.csv`, etc.)

### Antes vs Agora

| Antes | Agora |
|-------|-------|
| Config manual (copy/paste) | Config automático |
| Propenso a erros | Carrega do database |
| Sem DE/PARA de warehouses | Aplica DE/PARA (916→764) |
| Sem overrides por data | Overrides automáticos |

---

## Módulo config_generator.py

Localização: `service/config_generator.py`

### Funcionalidades Principais

#### 1. Carregamento de Configurações do Database
```python
load_warehouse_config_from_csv(unb_code, delivery_date)
```
- Busca warehouse no `database/Warehouse.csv`
- Carrega 44+ settings do `database/WarehouseConfiguration.csv`
- Aplica DE/PARA de códigos obsoletos
- Carrega `CombinedGroups` das tabelas relacionadas
- Aplica overrides baseados em data

#### 2. DE/PARA de Warehouse Codes
```python
apply_warehouse_depara(unb_code)
```

Conversões automáticas:
- `232` → `771`
- `916` → `764` (com override de data)
- `549` → `71`
- `550` → `538`
- `646` → `575`
- `910` → `724`

Códigos ignorados (não existem mais):
- `57059`, `PY1n`, `PY1l`, `PY14`, `BR6V`, `BRV3A`, `BR53`, `BRV1`, `015`

#### 3. Extração de Configuração do JSON
```python
extract_config_from_input(input_data)
```
Extrai do `input.json`:
- `Settings`: Configurações globais
- `MapNumber`: Número do mapa
- `NotPalletizedItems`: Itens não paletizados
- `Type`: Tipo do contexto (Route/AS/Mixed/CrossDocking/T4)

#### 4. Normalização de UnbCode
```python
_extract_unb_code(data)
```
Busca em múltiplos locais:
- `data.UnbCode`
- `data.SupportPoint` (formato: `-00916`)
- `data.Orders[0].Cross.SupportPoint`
- `data.Warehouse.UnbCode`

Remove zeros à esquerda: `00916` → `916`

#### 5. Geração de Config Completo
```python
generate_config_file(input_file, output_file=None, overwrite=False)
```
- Lê `input.json`
- Extrai/carrega configurações
- Salva `config_map_{MapNumber}.json` automaticamente

---

## Fluxo Completo

### PASSO 1: Preparar Estrutura de Pastas

```bash
ocp_score-main/data/route/
├── 620768/
│   └── input.json          # Arquivo de entrada (obrigatório)
└── mapas_in/
    └── input.json
```

### PASSO 2: Gerar Arquivos de Configuração

**Opção A: Um mapa específico**
```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

python -m ocp_score-main.service.config_generator \
  ocp_score-main/data/route/620768/input.json
```

**Opção B: Múltiplos mapas (loop)**
```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

for dir in ocp_score-main/data/route/*/; do
    if [ -f "${dir}input.json" ]; then
        python -m ocp_score-main.service.config_generator "${dir}input.json"
    fi
done
```

**Opção C: Via código Python**
```python
from service.config_generator import ConfigGenerator

generator = ConfigGenerator()

# Gera config para um mapa
generator.generate_config_file(
    "data/route/620768/input.json",
    overwrite=True
)
```

**O que acontece:**
1. Lê `input.json`
2. Extrai `UnbCode` (ex: `-00916` → `916`)
3. Aplica DE/PARA (`916` → `764`)
4. Busca no `database/Warehouse.csv` → `WarehouseId=184`
5. Carrega 44 Settings do `database/WarehouseConfiguration.csv`
6. Carrega `CombinedGroups` das tabelas relacionadas
7. Verifica data para overrides (warehouse 764 após 02/dez/2025)
8. Salva `config_map_620815.json` **na mesma pasta do input**

### PASSO 3: Processar Mapas de Paletização

**Opção A: Um mapa específico**
```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

python -m ocp_score-main.service.palletizing_processor \
  --config ocp_score-main/data/route/620768/config_map_620815.json \
  --input ocp_score-main/data/route/620768/input.json \
  --output ocp_score-main/data/route/620768/output
```

**Opção B: Processar TODOS os mapas de uma pasta**
```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

python -m ocp_score-main.service.run_all ocp_score-main/data/route
```

**O que acontece:**
1. Lê `config.json` + `input.json`
2. Cria o **Context** baseado no tipo (RouteRuleContext/ASRuleContext/etc)
3. Enriquece itens com dados do database (`csv-itens_17122025.csv`)
4. Aplica cadeia de regras específicas do tipo de mapa
5. Aplica regras comuns (common_chain)
6. Gera arquivos de saída

**Arquivos gerados:**
- `output/palletize_result_map_620815.json` - Resultado completo em JSON
- `output/palletize_result_map_620815.txt` - Resumo de paletes
- `output/620815-ocp-Rota.txt` - Relatório completo (formato TXT padrão)

---

## Estrutura de Arquivos

### Estrutura Final Completa

```
ocp_wms_core/
├── ocp_score-main/
│   ├── service/
│   │   ├── config_generator.py           - Módulo principal
│   │   ├── palletizing_processor.py      - Processador de mapas
│   │   └── run_all.py                    - Processamento em lote
│   │
│   ├── database/                         - Database CSVs
│   │   ├── Warehouse.csv                 (UnbCode → WarehouseId)
│   │   ├── WarehouseConfiguration.csv    (Settings por warehouse)
│   │   ├── GroupCombination.csv          (Combinações de grupos)
│   │   └── GroupCombinationGroup.csv     (Grupos por combinação)
│   │
│   └── data/
│       ├── csv-itens_17122025.csv        - Dados de produtos
│       │
│       └── route/                        - Mapas de rota
│           ├── 620768/
│           │   ├── input.json            [INPUT] Dados de entrada
│           │   ├── config_map_620815.json [GERADO] Configuração
│           │   └── output/               [SAÍDA] Resultados
│           │       ├── palletize_result_map_620815.json
│           │       ├── palletize_result_map_620815.txt
│           │       └── 620815-ocp-Rota.txt
│           │
│           └── mapas_in/
│               ├── input.json
│               ├── config_map_620815.json
│               └── output/
│                   └── ...
│
├── GERAR_TXT_COMPLETO.sh                 - Script auxiliar de TXT
├── README_GERACAO_TXT.md                 - Doc de geração de TXT
└── README_CONFIG_GENERATOR.md            - Este arquivo
```

### Fluxo de Dados

```
┌─────────────────┐
│   input.json   │ ──┐
└─────────────────┘   │
                      │
┌─────────────────┐   │    ┌──────────────────────┐
│  database/*.csv │ ──┼───→│ config_generator.py  │
└─────────────────┘   │    └──────────────────────┘
                      │              │
                      │              ▼
                      │    ┌─────────────────────┐
                      │    │ config_map_XXX.json │
                      │    └─────────────────────┘
                      │              │
                      ▼              ▼
              ┌────────────────────────────┐
              │ palletizing_processor.py   │
              └────────────────────────────┘
                        │
                        ▼
              ┌────────────────────────┐
              │  output/               │
              │  - JSON (resultado)    │
              │  - TXT (resumo)        │
              │  - TXT (completo)      │
              └────────────────────────┘
```

---

## Comandos e Exemplos

### Geração de Config

#### Exemplo 1: Gerar config para um mapa
```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

python -m ocp_score-main.service.config_generator \
  ocp_score-main/data/route/620768/input.json
```

**Output:**
```
2025-12-21 23:24:40,127 - INFO - Lendo arquivo de entrada: input.json
2025-12-21 23:24:40,127 - INFO - Settings vazia no JSON, tentando carregar do database...
2025-12-21 23:24:40,127 - INFO - UnbCode encontrado: 916
2025-12-21 23:24:40,127 - INFO - UnbCode 916 → 764 (DE/PARA aplicado)
2025-12-21 23:24:40,128 - INFO - WarehouseId=184 encontrado para UnbCode=764
2025-12-21 23:24:40,136 - INFO - ✓ Config carregada para UnbCode=764 (original=916)
2025-12-21 23:24:40,136 - INFO - ✓ Arquivo de configuração gerado: config_map_620815.json
✓ Sucesso! Arquivo gerado: ocp_score-main/data/route/620768/config_map_620815.json
```

#### Exemplo 2: Gerar configs para todos os mapas
```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

# Loop em todas as pastas de mapas
for dir in ocp_score-main/data/route/*/; do
    input_file="${dir}input.json"
    if [ -f "$input_file" ]; then
        echo "Gerando config para: $dir"
        python -m ocp_score-main.service.config_generator "$input_file"
    fi
done
```

#### Exemplo 3: Especificar arquivo de saída
```bash
python -m ocp_score-main.service.config_generator \
  ocp_score-main/data/route/620768/input.json \
  ocp_score-main/data/route/620768/custom_config.json
```

### Processamento de Mapas

#### Exemplo 1: Processar um mapa
```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

python -m ocp_score-main.service.palletizing_processor \
  --config ocp_score-main/data/route/620768/config_map_620815.json \
  --input ocp_score-main/data/route/620768/input.json \
  --output ocp_score-main/data/route/620768/output
```

#### Exemplo 2: Processar todos os mapas (batch)
```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

python -m ocp_score-main.service.run_all ocp_score-main/data/route
```

**O que o run_all faz:**
1. Busca todas as pastas em `data/route/`
2. Para cada pasta, verifica se existe `input.json` e `config.json`
3. Processa cada mapa válido
4. Gera outputs em `pasta/output/`
5. Gera log consolidado: `batch_processing_TIMESTAMP.log`

### Workflow Completo (do zero)

```bash
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

# 1. Gerar todos os configs
echo "=== GERANDO CONFIGS ==="
for dir in ocp_score-main/data/route/*/; do
    input_file="${dir}input.json"
    if [ -f "$input_file" ]; then
        python -m ocp_score-main.service.config_generator "$input_file"
    fi
done

# 2. Processar todos os mapas
echo "=== PROCESSANDO MAPAS ==="
python -m ocp_score-main.service.run_all ocp_score-main/data/route

echo "=== CONCLUÍDO ==="
```

---

## Detalhes Técnicos

### Settings Carregadas do Database

O `config_generator` carrega 44+ configurações do CSV:

```python
{
  "UseBaySmallerThan35": "False",
  "KegExclusivePallet": "False",
  "IncludeTopOfPallet": "True",
  "MinimumOccupationPercentage": "0",
  "AllowEmptySpaces": "False",
  "AllowVehicleWithoutBays": "False",
  "DistributeItemsOnEmptySpaces": "False",
  "MinimumQuantityOfSKUsToDistributeOnEmptySpaces": "0",
  "AdjustReassemblesAfterWater": "False",
  "JoinDisposableContainers": "False",
  "OccupationToJoinMountedSpaces": "0",
  "OrderByItemsSequence": "False",
  "OrderPalletByProductGroup": "False",
  "OrderProductsForAutoServiceMap": "False",
  "DistributeMixedRouteOnASCalculus": "False",
  "OrderPalletByPackageCodeOccupation": "True",
  "OrderPalletByCancha": "True",
  "GroupComplexLoads": "True",
  "LimitPackageGroups": "True",
  "CombinedGroups": "(10, 20, 50, 90, 100, 200); (30, 40, 60, 70, 80)",
  "MinimumVolumeInComplexLoads": "42",
  "QuantitySkuInComplexLoads": "30",
  "UseItemsExclusiveOfWarehouse": "False",
  "EnableSafeSideRule": "False",
  "BulkAllPallets": "False",
  "NotMountBulkPallets": "True",
  "ReturnableAndDisposableSplitRuleDisabled": "True",
  "IsotonicTopPalletCustomOrderRule": "True",
  "ReassignmentOfNonPalletizedItems": "True",
  "SideBalanceRule": "True",
  "ReduceVolumePallets": "False",
  "PercentageReductionInPalletOccupancy": "0",
  "QuantityOfPackagingOnSamePallet": "0",
  "LoadControlEnabled": "False",
  "DebugStackBuilderEnabled": "False",
  "PalletizeDetached": "True",
  "MaxPackageGroups": "6",
  "OrderPalletByGroupSubGroupAndPackagingItem": "True",
  "ShouldLimitPackageGroups": "True",
  "OccupationAdjustmentToPreventExcessHeight": "False",
  "PalletEqualizationRule": "False",
  "ProductGroupSpecific": "",
  "PercentOccupationMinByDivision": "0",
  "PercentOccupationMinBySelectionPalletDisassembly": "0"
}
```

### Mapeamento CSV para Settings (DE/PARA)

O módulo faz mapeamento de nomes de colunas do CSV para nomes de Settings:

| Coluna CSV | Setting |
|------------|---------|
| `UseBayLessThan35` | `UseBaySmallerThan35` |
| `AllowEmptyBays` | `AllowEmptySpaces` |
| `DistributeItemsOnEmptyPallets` | `DistributeItemsOnEmptySpaces` |
| `JoinDisposables` | `JoinDisposableContainers` |
| `JoinPalletsWithLessThanOccupancy` | `OccupationToJoinMountedSpaces` |
| `AllowGroupingComplexLoads` | `GroupComplexLoads` |
| ... | ... |

### Override por Data (Warehouse 764)

Para warehouse 764 (após DE/PARA de 916):
- Antes de 02/dez/2025: `OccupationToJoinMountedSpaces` = valor do CSV
- A partir de 02/dez/2025: `OccupationToJoinMountedSpaces` = `29`

Exemplo:
```python
# Data: 25/nov/2025 → mantém valor do CSV (0)
# Data: 05/dez/2025 → override para 29
```

### CombinedGroups

Carregado de duas tabelas relacionadas:
1. `database/GroupCombination.csv` - Define combinações por warehouse
2. `database/GroupCombinationGroup.csv` - Define grupos em cada combinação

Formato de saída:
```
"(10, 20, 50, 90, 100, 200); (30, 40, 60, 70, 80)"
```

Cada grupo entre parênteses, separados por ponto-e-vírgula.

### Conversão de Valores

O módulo converte automaticamente tipos de dados:

```python
# Booleanos
"true"  → True
"false" → False
"1"     → True (em campos boolean)
"0"     → False (em campos boolean)

# Números
"42"    → 42 (int)
"3.14"  → 3.14 (float)
"1,5"   → 1.5 (float, aceita vírgula como separador decimal)
```

---

## Validação

### Como validar que está funcionando

#### 1. Config gerado corretamente
```bash
cat ocp_score-main/data/route/620768/config_map_620815.json | grep -E "Settings|MapNumber|Type"
```

Deve mostrar:
```json
{
  "Settings": {
    "UseBaySmallerThan35": "False",
    ...
  },
  "MapNumber": 620815,
  "Type": "Route"
}
```

#### 2. Settings carregadas do database
```bash
cat ocp_score-main/data/route/620768/config_map_620815.json | grep -c "\".*\":" | head -1
```

Deve retornar **44+** (número de configurações).

#### 3. DE/PARA aplicado
Verificar no log:
```
INFO - UnbCode 916 → 764 (DE/PARA aplicado)
INFO - WarehouseId=184 encontrado para UnbCode=764
```

#### 4. Outputs gerados
```bash
ls -lh ocp_score-main/data/route/620768/output/
```

Deve conter:
- `palletize_result_map_*.json`
- `palletize_result_map_*.txt`
- `*-ocp-Rota.txt`

---

## Troubleshooting

### Problema: Config vazio (Settings = {})

**Causa:** UnbCode não encontrado no input.json

**Solução:**
```bash
# Verificar se input.json tem UnbCode/SupportPoint
cat input.json | grep -E "UnbCode|SupportPoint"
```

### Problema: Warehouse não encontrado no CSV

**Causa:** UnbCode não existe em `database/Warehouse.csv` após DE/PARA

**Solução:**
```bash
# Verificar warehouse no CSV
grep "916" ocp_score-main/database/Warehouse.csv
```

### Problema: Settings com valores incorretos

**Causa:** CSV com dados inconsistentes

**Solução:**
```bash
# Verificar WarehouseConfiguration.csv
grep "764" ocp_score-main/database/WarehouseConfiguration.csv
```

### Problema: Processamento falha

**Causa:** config.json ou input.json inválido

**Solução:**
```bash
# Validar JSON
python -m json.tool ocp_score-main/data/route/620768/config_map_620815.json
python -m json.tool ocp_score-main/data/route/620768/input.json
```

---

## Referências

- **Código fonte:** `service/config_generator.py`
- **Processador:** `service/palletizing_processor.py`
- **Batch:** `service/run_all.py`
- **Database:** `database/*.csv`
- **Documentação TXT:** `README_GERACAO_TXT.md`

---

## Notas

1. Sempre ative o ambiente virtual antes de executar os comandos:
   ```bash
   source wms_venv/bin/activate
   ```

2. Os configs devem ser regenerados quando:
   - Warehouse configuration mudar no database
   - Data de entrega ultrapassar thresholds de override
   - Novos mapas forem adicionados

3. O processamento é idempotente: Pode ser executado múltiplas vezes com os mesmos inputs.

4. Logs são salvos: Processamento em lote gera `batch_processing_TIMESTAMP.log` na pasta raiz.

---

## Resumo Rápido

```bash
# 1. Ativar ambiente
cd /home/prd_debian/ocp_wms_core
source wms_venv/bin/activate

# 2. Gerar configs
python -m ocp_score-main.service.config_generator data/route/620768/input.json

# 3. Processar mapas
python -m ocp_score-main.service.run_all data/route
```

**Pronto! Sistema totalmente automatizado.**
