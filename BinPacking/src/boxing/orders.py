from typing import List, Dict, Tuple, Set, Optional
import numpy as np
import pandas as pd
import copy


class Orders:

    
    """
    Gets orders' part from the original input and keeps the information
    in order to insert it into the algorithm
    Args:
        input_data: Dict
    """ 


    def __init__(
        self, 
        input_data: Dict,
        map_number: str
    ) -> None:
  

        self._orders_by_invoice = {nf:self.refactor_dict_orders(input_data[nf]) for nf in input_data.keys()}
        self._map = map_number

    @property
    def orders_by_invoice(self) -> Dict:
        """Gets orders from original input
        """
        return self._orders_by_invoice

    @property
    def map(self) -> str:
        """Gets orders from original input
        """
        return self._map

    def refactor_dict_orders(self, orders_nf) -> Dict:
        return {sku:int(orders_nf[sku]) for sku in orders_nf.keys()}

    


