import unittest
import os
import tempfile
import json
from pathlib import Path

from boxing.marketplace_items import MarketplaceItems
from boxing.items import Items

class TMarketplaceItems(unittest.TestCase):
    """Testes para a classe MarketplaceItems"""
    
    def test_marketplace_loading(self):
        """Testa o carregamento de itens marketplace a partir de um CSV genérico"""
        
        # Cria um CSV temporário para teste
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_csv:
            temp_csv.write("Cod_Produto,Desc_Embalagem,Campo3,Campo4,Campo5,Cluster_Premium\n")
            temp_csv.write("12345,Desc1,c1,c2,c3,MKTP\n")
            temp_csv.write("00678,Desc2,c1,c2,c3,MKTP\n")
            temp_csv.write("91011,Desc3,c1,c2,c3,NAO_MKTP\n")
            
        try:
            # Testa carregamento e verificação
            marketplace_items = MarketplaceItems(csv_path=temp_csv.name)
            
            # Deve ter 2 SKUs + 2 normalizados = 4 entradas
            self.assertEqual(len(marketplace_items.marketplace_skus), 4)
            
            # Testa verificação de SKUs
            self.assertTrue(marketplace_items.is_marketplace_sku("12345"))
            self.assertTrue(marketplace_items.is_marketplace_sku("00678"))
            self.assertTrue(marketplace_items.is_marketplace_sku("678"))  # normalizado
            self.assertFalse(marketplace_items.is_marketplace_sku("91011"))
            
            # Testa adição de SKU
            marketplace_items.add_sku("99999")
            self.assertTrue(marketplace_items.is_marketplace_sku("99999"))
            
        finally:
            # Limpa o arquivo temporário
            os.unlink(temp_csv.name)
            
    def test_specific_csv_format(self):
        """Testa o carregamento de itens marketplace com o formato específico Id,UnitsPerBox,BoxType"""
        
        # Cria um CSV temporário para teste com o formato específico
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_csv:
            temp_csv.write("Id,UnitsPerBox,BoxType\n")
            temp_csv.write("--,-----------,-------\n")
            temp_csv.write("123456,24,TIPO_A\n")
            temp_csv.write("234567,12,TIPO_B\n")
            temp_csv.write("0034567,6,TIPO_C\n")  # com zeros à esquerda
            temp_csv.write("789,NULL,NULL\n")  # sem valores para UnitsPerBox e BoxType
            
        try:
            # Testa carregamento e verificação
            marketplace_items = MarketplaceItems(csv_path=temp_csv.name)
            
            # Testa se os SKUs foram carregados
            self.assertTrue(marketplace_items.is_marketplace_sku("123456"))
            self.assertTrue(marketplace_items.is_marketplace_sku("234567"))
            self.assertTrue(marketplace_items.is_marketplace_sku("34567"))  # normalizado sem zeros
            self.assertTrue(marketplace_items.is_marketplace_sku("789"))
            self.assertFalse(marketplace_items.is_marketplace_sku("999999"))  # não existe
            
            # Testa se os dados adicionais foram carregados
            self.assertEqual(marketplace_items.item_data["123456"]["units_per_box"], "24")
            self.assertEqual(marketplace_items.item_data["123456"]["box_type"], "TIPO_A")
            self.assertEqual(marketplace_items.item_data["234567"]["units_per_box"], "12")
            self.assertEqual(marketplace_items.item_data["234567"]["box_type"], "TIPO_B")
            
            # Testa normalização de SKU com zeros à esquerda
            self.assertEqual(marketplace_items.item_data["34567"]["units_per_box"], "6")
            self.assertEqual(marketplace_items.item_data["34567"]["box_type"], "TIPO_C")
            
            # Testa valor NULL
            self.assertEqual(marketplace_items.item_data["789"]["units_per_box"], None)
            self.assertEqual(marketplace_items.item_data["789"]["box_type"], None)
            
        finally:
            # Limpa o arquivo temporário
            os.unlink(temp_csv.name)
            
    def test_items_integration(self):
        """Testa a integração da classe MarketplaceItems com a classe Items"""
        
        # Cria um CSV temporário para teste
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_csv:
            temp_csv.write("Id,UnitsPerBox,BoxType\n")
            temp_csv.write("--,-----------,-------\n")
            temp_csv.write("123456,24,TIPO_A\n")
            
        try:
            # Carrega os itens de marketplace
            marketplace_items = MarketplaceItems(csv_path=temp_csv.name)
            
            # Mock do input_data para a classe Items
            input_data = {
                "height": "10",
                "width": "10",
                "length": "10",
                "pacote_fechado": "6",  # deve ser sobrescrito com o valor do CSV
                "tipo_garrafa": "",
                "weight": "5",
                "subcategory": "test"
            }
            
            # Cria um item com SKU do marketplace
            item = Items(
                input_data=input_data,
                promax_code="123456",
                map_id="test",
                verbose=False,
                marketplace_items=marketplace_items
            )
            
            # Verifica se é marketplace e se as propriedades estão corretas
            self.assertTrue(item.is_marketplace)
            self.assertEqual(item.units_per_box, "24")
            self.assertEqual(item.box_type, "TIPO_A")
            
            # Verifica se o units_in_boxes foi sobrescrito com o valor do CSV
            self.assertEqual(item.units_in_boxes, 24)
            
            # Testa com SKU não marketplace
            item2 = Items(
                input_data=input_data,
                promax_code="999999",
                map_id="test",
                verbose=False,
                marketplace_items=marketplace_items
            )
            
            self.assertFalse(item2.is_marketplace)
            self.assertIsNone(item2.units_per_box)
            self.assertIsNone(item2.box_type)
            
            # O units_in_boxes deve manter o valor original do input_data
            self.assertEqual(item2.units_in_boxes, 6)
            
        finally:
            # Limpa o arquivo temporário
            os.unlink(temp_csv.name)
            
if __name__ == '__main__':
    unittest.main()