#!/usr/bin/env python3
"""
Detector de Produtos Marketplace

Identifica se produtos do input são marketplace baseado no CSV.
"""

import pandas as pd
import logging
from typing import Set, List, Dict, Any
from pathlib import Path

log = logging.getLogger(__name__)


class MarketplaceDetector:
    """Detecta produtos marketplace no input"""
    
    def __init__(self, csv_path: str = None):
        """
        Inicializa o detector
        
        Args:
            csv_path: Caminho do CSV de produtos marketplace
        """
        if csv_path is None:
            # Caminho padrão
            csv_path = "/home/prd_debian/data 2(Export).csv"
        
        self.csv_path = csv_path
        self.marketplace_skus: Set[str] = set()
        self.product_details: Dict[str, Dict] = {}
        self._load_marketplace_products()
    
    def _load_marketplace_products(self):
        """Carrega lista de produtos marketplace do CSV"""
        try:
            # Tenta diferentes encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(self.csv_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise Exception("Não foi possível decodificar o CSV com nenhum encoding testado")
            
            # Filtra apenas produtos com Cluster_Premium = MKTP
            mktp_df = df[df['Cluster_Premium'] == 'MKTP']
            
            # Armazena SKUs como strings
            self.marketplace_skus = set(mktp_df['Cod_Produto'].astype(str))
            
            # Armazena detalhes dos produtos
            for _, row in mktp_df.iterrows():
                sku = str(row['Cod_Produto'])
                self.product_details[sku] = {
                    'descricao_embalagem': row.get('Descricao_Embalagem', ''),
                    'descricao_familia': row.get('Descricao_Familia_EG', ''),
                    'descricao_produto': row.get('Descricao_Produto', ''),
                    'cluster_embalagem': row.get('Cluster_Embalgem', 'DES'),
                }
            
            log.info(f"✓ Carregados {len(self.marketplace_skus)} produtos marketplace")
            
        except Exception as e:
            log.error(f"Erro ao carregar CSV marketplace: {e}")
            raise
    
    def is_marketplace(self, sku: str) -> bool:
        """
        Verifica se um SKU é marketplace
        
        Args:
            sku: Código do produto
            
        Returns:
            True se for marketplace
        """
        return str(sku) in self.marketplace_skus
    
    def get_product_info(self, sku: str) -> Dict[str, Any]:
        """
        Retorna informações de um produto marketplace
        
        Args:
            sku: Código do produto
            
        Returns:
            Dict com informações do produto ou None
        """
        return self.product_details.get(str(sku))
    
    def filter_marketplace_items(self, items: List[Dict]) -> tuple:
        """
        Separa itens entre marketplace e não-marketplace
        
        Args:
            items: Lista de itens com campo 'Code' ou 'ProductCode'
            
        Returns:
            Tupla (marketplace_items, non_marketplace_items)
        """
        marketplace = []
        non_marketplace = []
        
        for item in items:
            # Tenta pegar o código do produto de diferentes campos
            code = item.get('Code') or item.get('ProductCode') or item.get('SKU')
            
            if code and self.is_marketplace(code):
                marketplace.append(item)
            else:
                non_marketplace.append(item)
        
        return marketplace, non_marketplace
    
    def analyze_input(self, input_data: Dict) -> Dict[str, Any]:
        """
        Analisa o input e identifica produtos marketplace
        
        Args:
            input_data: Dados do input.json
            
        Returns:
            Dict com análise: {
                'has_marketplace': bool,
                'total_items': int,
                'marketplace_count': int,
                'marketplace_skus': List[str],
                'non_marketplace_count': int
            }
        """
        all_items = []
        
        # Extrai itens de diferentes estruturas possíveis
        if 'Orders' in input_data:
            for order in input_data['Orders']:
                if 'Items' in order:
                    all_items.extend(order['Items'])
        elif 'Items' in input_data:
            all_items = input_data['Items']
        
        marketplace_items, non_marketplace_items = self.filter_marketplace_items(all_items)
        
        marketplace_skus = []
        for item in marketplace_items:
            code = item.get('Code') or item.get('ProductCode') or item.get('SKU')
            if code:
                marketplace_skus.append(str(code))
        
        analysis = {
            'has_marketplace': len(marketplace_items) > 0,
            'total_items': len(all_items),
            'marketplace_count': len(marketplace_items),
            'marketplace_skus': list(set(marketplace_skus)),
            'non_marketplace_count': len(non_marketplace_items),
            'marketplace_percentage': (len(marketplace_items) / len(all_items) * 100) if all_items else 0
        }
        
        log.info(f"Análise: {analysis['marketplace_count']}/{analysis['total_items']} itens são marketplace ({analysis['marketplace_percentage']:.1f}%)")
        
        return analysis


# Singleton global
_detector_instance = None

def get_detector() -> MarketplaceDetector:
    """Retorna instância singleton do detector"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = MarketplaceDetector()
    return _detector_instance


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)
    
    detector = MarketplaceDetector()
    
    print(f"\n✓ Total produtos marketplace: {len(detector.marketplace_skus)}")
    print(f"\nExemplos de SKUs marketplace:")
    for sku in list(detector.marketplace_skus)[:10]:
        info = detector.get_product_info(sku)
        print(f"  - {sku}: {info['descricao_produto'][:50]}")
    
    # Teste de detecção
    print(f"\nTestes de detecção:")
    print(f"  1706 é marketplace? {detector.is_marketplace('1706')}")
    print(f"  99999 é marketplace? {detector.is_marketplace('99999')}")
