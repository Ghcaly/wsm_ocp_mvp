from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from typing import List, Dict, Tuple, Set, Optional
import logging
from boxing.orders import Orders 
from boxing.boxes import Boxes
from boxing.items import Items
from boxing.utils import Utils

import numpy as np
import logging

from boxing.logger import BoxingLogger


class Input(ABC):
    
    def __init__(
        self,
        name: str,
        orders: Orders,
        skus_info: Dict[str, Items],
        boxes_info: Dict[str, Boxes],
        number_of_boxes: int,
        max_weight: float
    ) -> None:

        """ Represent a generic object which contains all inputs to algorithm.
        Args:
            name: input name 
            orders: orders object - skus and respective quantity groupes by invoice number.
            skus_info: information about skus (dimensions, quantity by closed package).
            boxes_info: information about boxes (dimensions, box type).
            number_of_boxes: max number of available boxes
            max_weight: max weight for each box
        """
        self._name = name
        self._orders = orders
        self._skus = skus_info
        self._boxes = boxes_info
        self._number_of_boxes = number_of_boxes
        self._max_weight = max_weight
        
    

   
    @property
    def name(self) -> str:
        """Gets step name
        """
        return self._name

    @property
    def orders(self) -> Orders:
        """Gets orders
        """
        return self._orders 
    @property
    def skus(self) -> Items:
        """Gets skus info
        """
        return self._skus
    @property
    def boxes(self) -> Boxes:
        """Gets boxes info
        """
        return self._boxes

    @property
    def number_of_boxes(self) -> int:
        """Gets number of boxes info
        """
        return self._number_of_boxes

    @property
    def max_weight(self) -> float:
        """Gets max weight
        """
        return self._max_weight

  