import sys
sys.path.append(r'c:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia')

from adapters.comparar_relatorios import extrair_produtos_do_relatorio

# Carregar ambos os arquivos
with open(r'c:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\relatorio_wms.txt', 'r', encoding='utf-8') as f:
    wms_data = extrair_produtos_do_relatorio(f.read())

with open(r'c:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score_ia\data\relatorio_api.txt', 'r', encoding='utf-8') as f:
    api_data = extrair_produtos_do_relatorio(f.read())

print(f'Total WMS: {len(wms_data)}')
print(f'Total API: {len(api_data)}')
print()

# Criar set de API para busca rápida (number_mapa, pallet_code, product_code, quantity)
api_set = set()
for item in api_data:
    key = (item['number_mapa'], item['pallet_code'], item['product_code'], item['quantity'])
    api_set.add(key)

print(f'Chaves únicas no API: {len(api_set)}')

# Contar matches
matches = 0
nao_encontrados = []
for item in wms_data:
    key = (item['number_mapa'], item['pallet_code'], item['product_code'], item['quantity'])
    if key in api_set:
        matches += 1
    else:
        nao_encontrados.append(item)

print(f'\nLinhas idênticas: {matches}')
print(f'Percentual: {matches/len(wms_data)*100:.1f}%')
print()

# Mostrar exemplos que não bateram
print('Primeiras 10 linhas WMS sem match no API:')
for i, item in enumerate(nao_encontrados[:10]):
    print(f"{i+1}. WMS: mapa={item['number_mapa']}, pallet={item['pallet_code']}, produto={item['product_code']}, qty={item['quantity']}")
    
    # Verificar se existe com outros valores
    encontrou_similar = False
    for api_item in api_data:
        if (api_item['pallet_code'] == item['pallet_code'] and 
            api_item['product_code'] == item['product_code']):
            print(f"   API: mapa={api_item['number_mapa']}, pallet={api_item['pallet_code']}, produto={api_item['product_code']}, qty={api_item['quantity']}")
            encontrou_similar = True
            break
    if not encontrou_similar:
        print(f"   Não encontrado produto {item['product_code']} no pallet {item['pallet_code']} no API")
    print()
