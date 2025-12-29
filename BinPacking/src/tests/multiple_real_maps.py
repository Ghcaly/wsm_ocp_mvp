import os
import pandas as pd
import xml.etree.ElementTree as Xet
import gc

from boxing.unitBoxing import UnitBoxing

def get_itens_df_old(filename):
    return pd.read_csv(filename).drop(columns = 'Unnamed: 0')

def get_itens_mktp_old(itens_df):
    return list(itens_df['CdProdutoPromax'])

def get_filenames_old(filepath):
    return os.listdir(filepath)

def get_maps_new(mapa_promax):
    sku_col = 'Cód. Produto'
    nr_nf_col = 'Desc. Pallet'
    qt_col = 'Qt. Caixas Pallet'
    map_col = 'mapa'    
    mapa_promax_df_init = pd.read_csv(mapa_promax+'.csv')
    mapa_promax_df_init[map_col] = mapa_promax_df_init[map_col].astype('int')
    map_numbers = get_map_numbers_new(mapa_promax_df_init, map_col)
    maps = {}
    for mn in range(len(map_numbers)):
        maps[map_numbers[mn]] = get_map_configuration_new(df = mapa_promax_df_init,
                                         map_col = map_col,
                                         sku_col = sku_col,
                                         nr_nf_col = nr_nf_col,
                                         map_number = map_numbers[mn],
                                         qt_col = qt_col)
    return maps

def get_map_numbers_new(df, map_col):
    return df[map_col].unique()

def get_map_configuration_new(df, map_col, sku_col, nr_nf_col, map_number, qt_col):
    df_sub = df[df[map_col] == map_number]
    nr_nf = get_map_nf_new(df_sub, nr_nf_col)
    dict_res = {}
    for nf in nr_nf:
        nf_dict = {}
        df_rows = df_sub[df_sub[nr_nf_col] == nf]
        pallet_skus = df_rows[sku_col].unique()
        for sk in pallet_skus:
            df_sub_row = df_rows[df_rows[sku_col] == sk]
            nf_dict[str(sk)] = df_sub_row[qt_col].values.sum() 
        dict_res[nf] = nf_dict
    return dict_res

def get_maps_new_items(mapa_promax):
    maps_new = get_maps_new(mapa_promax)
    maps_new_items = []
    for m in maps_new.keys():
        mapa = maps_new[m]
        for p in mapa.keys():
            pallet = mapa[p]
            for item in pallet.keys():
                if item not in maps_new_items:
                    maps_new_items.append(item)
    return maps_new_items

def get_map_nf_new(df, nr_nf_col):
    return list(df[nr_nf_col].unique())

def get_itens_nf(itens, skus_mktp):
    itens_nf = {}
    for it in itens:
        item = it
        cd_item = item.find("cdItem").text
        if cd_item in skus_mktp:
            qt_un_venda = int(item.find("qtUnVenda").text)
            itens_nf[cd_item] = qt_un_venda
    return itens_nf
    
def get_unique_map_old(root, skus_mktp):
    orders = {}
    for i in root:
        notas_fiscais = i.find("notas_fiscais")
        if notas_fiscais != None:
            for nf in notas_fiscais:
                nota_fiscal = nf
                nr_nota_fiscal = nota_fiscal.find("nrNotaFiscal").text
                itens = nota_fiscal.find("itens")
                itens_nf = get_itens_nf(itens, skus_mktp)
                if itens_nf != {}:
                    orders[nr_nota_fiscal] = itens_nf
        return orders

def get_maps_promax_old(filepath, mapa_promax):    
    files = get_filenames_old(filepath)
    skus_mktp = get_maps_new_items(mapa_promax)
    maps_promax = {}
    for f in files:
        xmlparse = Xet.parse(filepath+ "/" + f )
        root = xmlparse.getroot()
        map_number = root.find("mapa").find("nrMapa").text
        maps_promax[map_number] = get_unique_map_old(root, skus_mktp)
    return maps_promax

def get_items_info_old(gross_weight, itens_df, sku_colname, len_col, wid_col, hei_col, tipo_garrafa_col, units_in_boxes_col, items_new, subcategory):
    items = get_itens_mktp_old(itens_df)
    items_dict = {}
    for i in items:
        if str(i) in items_new:
            items_sub_dict = {}
            sub_itens_df = itens_df[itens_df[sku_colname] == i]
            items_sub_dict['height'] = float(sub_itens_df[hei_col].values[0])
            items_sub_dict['width'] = float(sub_itens_df[wid_col].values[0])
            items_sub_dict['length'] = float(sub_itens_df[len_col].values[0])
            items_sub_dict['tipo_garrafa'] = int(sub_itens_df[tipo_garrafa_col].values[0])
            items_sub_dict['units_in_boxes'] = int(sub_itens_df[units_in_boxes_col].values[0])
            items_sub_dict['gross_weight'] = float(sub_itens_df[gross_weight].values[0])
            items_sub_dict['subcategory'] = int(sub_itens_df[subcategory].values[0])
            items_dict[str(i)] = items_sub_dict
    return items_dict

def get_boxes_old():
    box_dict = {
    "1": {
      "length": 0,
      "width": 0,
      "height": 0,
      "box_slots": 9,
      "box_slot_diameter": 10.392304
    },
    "2": {
      "length": 40,
      "width": 58,
      "height": 34,
      "box_slots": 0,
      "box_slot_diameter": 0
        }
      }
    return box_dict

def get_families():
    fam_dict = [
    {
      "subcategory": "1",
      "cant_go_with": [
      ]
    }
    ]
    return fam_dict

def get_items_old(items_new, itens_df):
    sku_colname = 'CdProdutoPromax'
    len_col = 'Largura'
    wid_col = 'Comprimento'
    hei_col = 'Altura'
    tipo_garrafa_col = 'Tipo Garrafa'
    units_in_boxes_col = 'Unidades por Caixa'
    gross_weight = 'gross_weight'
    subcategory = 'subcategory'
    df = get_itens_df_old(itens_df)
    items = get_items_info_old(gross_weight, df, sku_colname, len_col, wid_col, hei_col, tipo_garrafa_col, units_in_boxes_col, items_new, subcategory)
    return items

def run_tests_old(maps, itens_df, mapa_promax):
    result = {}
    items_new = get_maps_new_items(mapa_promax)
    items = get_items_old(items_new, itens_df)
    boxes = get_boxes_old()
    families = get_families()
    for m in maps.keys():
        data = {str(m):maps[m], 'skus': items, 'boxes': boxes, "family_groups":families}
        algo_box = UnitBoxing(json_input = data, verbose = False)
        gc.collect()
        result[m] = algo_box.apply()
    return result

def get_res():
    current_path = os.path.dirname(os.path.abspath(__file__))
    filepath_promax = current_path + '/samples/mapas_backtest'
    mapa_promax = current_path + '/samples/mapas_sc'
    itens_df = current_path + '/samples/itens_df4.csv'
    maps_promax = get_maps_promax_old(filepath_promax, mapa_promax)
    return run_tests_old(maps_promax, itens_df, mapa_promax)

    

