from typing import List, Dict, Set, Tuple
import csv
import os
import logging
from pathlib import Path

from boxing.logger import BoxingLogger

class MarketplaceItems:
    """
    Classe para gerenciar a tabela de itens marketplace.
    Carrega e mantém uma lista de SKUs que são considerados marketplace.
    """

    def __init__(
        self,
        csv_path: str = None,
        map_id: str = "marketplace",
        verbose: bool = False
    ) -> None:
        """
        Inicializa a classe de itens marketplace
        Args:
            csv_path: Caminho para o arquivo CSV com itens marketplace (opcional)
            map_id: ID do mapa para logging
            verbose: Se deve mostrar logs detalhados
        """
        self._verbose = verbose
        self._box_log_utils = BoxingLogger(map_id=map_id, name='marketplace_items_log', verbose=self.verbose)
        self._logger = self._box_log_utils.logger
        self._marketplace_skus = set()
        self._item_data = {}  # Armazena dados adicionais por SKU (UnitsPerBox, BoxType)
        
        # Tenta carregar de um caminho padrão se não for especificado
        if csv_path is None:
            self._load_default_marketplace_skus()
        else:
            self._load_marketplace_skus(csv_path)
            
    @property
    def verbose(self) -> bool:
        """Retorna o modo verbose"""
        return self._verbose
        
    @property
    def logger(self) -> logging:
        """Retorna o objeto logger"""
        return self._logger
        
    @property
    def marketplace_skus(self) -> Set[str]:
        """Retorna o conjunto de SKUs marketplace"""
        return self._marketplace_skus
        
    @property
    def item_data(self) -> Dict[str, Dict[str, str]]:
        """Retorna os dados adicionais para cada SKU"""
        return self._item_data
        
    def _load_default_marketplace_skus(self) -> None:
        """Tenta carregar o arquivo CSV de caminhos padrão"""
        candidates = [
            Path("c:/prd_debian/ocp_wms_core/ocp_score-main/database/ItemMarketPlace.csv"),  # Caminho específico
            Path("/mnt/c/prd_debian/ocp_wms_core/ocp_score-main/database/ItemMarketPlace.csv"),  # path no WSL
            Path("/home/prd_debian/ocp_wms_core/ocp_score-main/database/ItemMarketPlace.csv"),  # fallback Linux
        ]

        for csv_file in candidates:
            if not csv_file.exists():
                continue
                
            self.logger.info(f"Carregando arquivo de marketplace: {csv_file}")
            self._load_marketplace_skus(str(csv_file))
            return
        
        self.logger.warning("Não foi possível encontrar o arquivo de marketplace em nenhum dos caminhos padrão")
            
    def _load_marketplace_skus(self, csv_path: str) -> None:
        """
        Carrega os SKUs marketplace de um arquivo CSV
        Args:
            csv_path: Caminho para o arquivo CSV
        """
        try:
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(csv_path, 'r', encoding=encoding, newline='') as f:
                        # Identifica o formato do CSV
                        first_line = f.readline().strip()
                        f.seek(0)  # Volta para o início do arquivo
                        
                        if "Id,UnitsPerBox,BoxType" in first_line:
                            # Formato novo: Id,UnitsPerBox,BoxType
                            self._load_marketplace_from_specific_csv(f, encoding)
                        else:
                            # Formato antigo: Cod_Produto,Desc_Embalagem,...,Cluster_Premium
                            self._load_marketplace_from_generic_csv(f)
                    break
                except UnicodeDecodeError:
                    continue
                    
            self.logger.info(f"Carregados {len(self._marketplace_skus)} SKUs marketplace")
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo CSV de marketplace: {e}")
            
    def _load_marketplace_from_specific_csv(self, file_handle, encoding: str) -> None:
        """
        Carrega dados do CSV específico com formato Id,UnitsPerBox,BoxType
        """
        try:
            # Pular as duas primeiras linhas (cabeçalho e linha de separação)
            next(file_handle)  # Id,UnitsPerBox,BoxType
            next(file_handle)  # --,-----------,-------
            
            csv_reader = csv.reader(file_handle)
            for row in csv_reader:
                if len(row) >= 1 and row[0].strip():
                    sku = row[0].strip()
                    self._marketplace_skus.add(sku)
                    
                    # Armazena dados adicionais
                    units_per_box = None if len(row) < 2 or row[1] == "NULL" else row[1]
                    box_type = None if len(row) < 3 or row[2] == "NULL" else row[2]
                    
                    self._item_data[sku] = {
                        "units_per_box": units_per_box,
                        "box_type": box_type
                    }
                    
                    # Normaliza o SKU sem zeros à esquerda e adiciona também
                    try:
                        normalized_sku = str(int(sku))
                        if normalized_sku != sku:
                            self._marketplace_skus.add(normalized_sku)
                            self._item_data[normalized_sku] = self._item_data[sku]
                    except ValueError:
                        pass
                        
        except Exception as e:
            self.logger.error(f"Erro ao processar CSV específico: {e}")
            
    def _load_marketplace_from_generic_csv(self, file_handle) -> None:
        """
        Carrega dados do CSV genérico antigo
        """
        try:
            next(file_handle)  # pula o header
            for line in file_handle:
                parts = line.strip().replace('\r', '').split(',')
                # Formato: Cod_Produto,Desc_Embalagem,...,Cluster_Premium
                if len(parts) >= 6 and parts[-1].strip() == 'MKTP':
                    sku = parts[0].strip()
                    self._marketplace_skus.add(sku)
                    try:
                        normalized_sku = str(int(sku))
                        self._marketplace_skus.add(normalized_sku)
                    except ValueError:
                        pass
        except Exception as e:
            self.logger.error(f"Erro ao processar CSV genérico: {e}")
            
    def is_marketplace_sku(self, sku: str) -> bool:
        """
        Verifica se um SKU está na lista de marketplace
        Args:
            sku: Código do SKU a verificar
        Returns:
            bool: True se for um SKU marketplace, False caso contrário
        """
        normalized_sku = sku
        
        # Tenta normalizar o SKU removendo zeros à esquerda
        try:
            normalized_sku = str(int(sku))
        except (ValueError, TypeError):
            pass
            
        return (sku in self._marketplace_skus) or (normalized_sku in self._marketplace_skus)
        
    def add_sku(self, sku: str) -> None:
        """
        Adiciona um SKU à lista de marketplace
        Args:
            sku: Código do SKU a adicionar
        """
        self._marketplace_skus.add(sku)
        try:
            self._marketplace_skus.add(str(int(sku)))  # normaliza
        except (ValueError, TypeError):
            pass