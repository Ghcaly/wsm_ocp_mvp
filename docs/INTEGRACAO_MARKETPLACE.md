# Integração de Itens Marketplace

Este documento descreve a implementação da integração com a tabela de itens marketplace no projeto BinPacking.

## Visão Geral

A integração permite identificar SKUs que pertencem ao marketplace e obter informações adicionais sobre eles, como o número de unidades por caixa e o tipo de caixa a ser utilizado.

## Arquivos Modificados/Criados

- `BinPacking/src/boxing/marketplace_items.py`: Nova classe para gerenciar a tabela de itens marketplace
- `BinPacking/src/boxing/items.py`: Modificada para integrar com a classe MarketplaceItems
- `BinPacking/src/tests/tMarketplaceItems.py`: Testes para a funcionalidade marketplace

## Estrutura do Arquivo CSV

O arquivo CSV deve ter a seguinte estrutura:

```csv
Id,UnitsPerBox,BoxType
--,-----------,-------
123456,24,TIPO_A
234567,12,TIPO_B
...
```

O sistema também suporta o formato antigo com o seguinte layout:
```csv
Cod_Produto,Desc_Embalagem,Campo3,Campo4,Campo5,Cluster_Premium
12345,Desc1,c1,c2,c3,MKTP
...
```

## Localização do Arquivo

O arquivo é buscado automaticamente nas seguintes localizações:

1. `c:/prd_debian/ocp_wms_core/ocp_score-main/database/ItemMarketPlace.csv`
2. `/mnt/c/prd_debian/ocp_wms_core/ocp_score-main/database/ItemMarketPlace.csv` (para WSL)
3. `/home/prd_debian/ocp_wms_core/ocp_score-main/database/ItemMarketPlace.csv` (para Linux)

Alternativamente, é possível especificar o caminho do arquivo ao criar a instância da classe `MarketplaceItems`.

## Uso

### Criar uma instância da classe MarketplaceItems

```python
from boxing.marketplace_items import MarketplaceItems

# Usando o caminho padrão
marketplace_items = MarketplaceItems(verbose=True)

# OU especificando o caminho
marketplace_items = MarketplaceItems(
    csv_path="/caminho/para/marketplace.csv",
    map_id="mapa_123",
    verbose=True
)
```

### Verificar se um SKU é marketplace

```python
# Verifica se um SKU está na lista de marketplace
is_mktp = marketplace_items.is_marketplace_sku("123456")
```

### Integração com a classe Items

A classe `Items` já está integrada com a `MarketplaceItems`. Ao criar uma instância de `Items`, você pode fornecer uma instância de `MarketplaceItems`:

```python
from boxing.marketplace_items import MarketplaceItems
from boxing.items import Items

# Cria uma instância de MarketplaceItems
marketplace_items = MarketplaceItems()

# Cria um item com a instância de MarketplaceItems
item = Items(
    input_data=input_data,
    promax_code="123456",
    map_id="mapa_123",
    verbose=True,
    marketplace_items=marketplace_items
)

# Verifica se o item é marketplace
is_mktp = item.is_marketplace

# Obtém dados adicionais
units_per_box = item.units_per_box
box_type = item.box_type
```

## Sobrescrita de unidades por caixa

Se um SKU for identificado como marketplace e tiver a informação de `units_per_box` no CSV, este valor será automaticamente usado para substituir o valor original de `units_in_boxes` do item.

## Testes

Os testes para esta funcionalidade estão no arquivo `BinPacking/src/tests/tMarketplaceItems.py` e podem ser executados com:

```bash
cd BinPacking/src
python -m unittest tests/tMarketplaceItems.py
```