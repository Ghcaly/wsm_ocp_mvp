from typing import List, Dict, Tuple, Set, Optional
import numpy as np
import pandas as pd
import copy
import logging
from boxing.utils import Utils
from boxing.logger import BoxingLogger


class Boxes:

    
    """
    Gets boxes' part from the original input and keeps the information
    in order to insert it into the algorithm
    Args:
        input_data: Dict
        box_name: str
    """ 


    def __init__(
        self, 
        box_name: str,
        input_data: Dict,
        map_id: str,
        verbose: bool
    ) -> None:
        
        self._verbose = verbose
        self._box = str(box_name) 
        self._map_id = map_id
        self._box_slots = int(input_data['box_slots'])
        self._height = float(input_data['height'])
        self._width = float(input_data['width'])
        self._length = float(input_data['length'])
        self._box_slot_diameter = float(input_data['box_slot_diameter'])
        self._box_log_utils = BoxingLogger(map_id = map_id, name =  'box_log', verbose = self.verbose)
        self._logger = self.box_log_utils.logger
        self._box_type = self.get_box_type()
        
        
    @property
    def verbose(self) -> bool:
        """Gets the verbose option.
        """
        return self._verbose

    @property
    def box(self) -> str:
        """Gets box code/name from original input
        """
        return self._box

    @property
    def box_type(self) -> str:
        """Gets box from original input
        """
        return self._box_type

    @property
    def box_slots(self) -> int:
        """Gets number of box_slots from original input
        """
        return self._box_slots

    @property
    def height(self) -> float:
        """Gets box height from original input
        """
        return self._height

    @property
    def width(self) -> float:
        """Gets box width from original input
        """
        return self._width

    @property
    def length(self) -> float:
        """Gets box length from original input
        """
        return self._length

    @property
    def box_slot_diameter(self) -> float:
        """Gets box slot diameter from original input
        """
        return self._box_slot_diameter

    @property
    def map_id(self) -> str:
        """Gets the map identifier.
        """
        return self._map_id

    
    @property
    def box_log_utils(self) -> BoxingLogger:
        """Gets the BoxingLogger object .
        """
        return self._box_log_utils

    @property
    def logger(self) -> logging:
        """Gets the logger object.
        """
        return self._logger


    def get_box_type(
        self        
    ) -> str:
        
        if self.box_slots == 0:
            self.logger.debug("Getting box type -> result = CAIXA")
            return 'caixa'
        elif self.box_slots > 0:
            self.logger.debug("Getting box type -> result = GARRAFEIRA")
            return 'garrafeira'

    





