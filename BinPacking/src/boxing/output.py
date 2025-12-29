from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from typing import List, Dict, Tuple, Set, Optional
from boxing.orders import Orders 

import numpy as np
import logging

from boxing.logger import BoxingLogger


class Output(ABC):
    
    def __init__(
        self,
        name: str,
        new_orders: Dict,
        step_result: Dict,
        map_number: str,
        skus_not_processed: Dict,
        verbose: bool
    ) -> None:

        """
        Object with result informations for each step. 
        Args:
            name: output step name,
            new_orders: skus grouped by invoice numbers that weren't
            put into boxes up to this step of the algorithm
            step_result: skus grouped by boxes (results for the step
            of the algorithm)
            map_number: map number 
            skus_not_processed: skus that could not be processed by the algorithm
            verbose: if True, prints logger output (default False)
        """

        self._verbose = verbose
        self._name = name
        self._map_id = map_number
        self._new_orders = Orders(input_data = new_orders, map_number = map_number)
        self._step_result = step_result
        self._skus_not_processed = skus_not_processed
        self._box_log_utils = BoxingLogger(name =  name+'_log', map_id = map_number, verbose = self.verbose)
        self._logger = self._box_log_utils.logger
        
        self.logger.debug(f"Generating output object - step result = {self.step_result} - new orders = {self.new_orders.orders_by_invoice} - skus_not_processed = {self.skus_not_processed}")

    

    @property
    def verbose(self) -> bool:
        """Gets the verbose option.
        """
        return self._verbose
    
    @property
    def name(self) -> str:
        """Gets name
        """
        return self._name

    @property
    def new_orders(self) -> Dict:
        """Gets new orders
        """
        return self._new_orders
    @property
    def step_result(self) -> Dict:
        """Gets step result
        """
        return self._step_result

    @property
    def box_log_utils(self) -> BoxingLogger:
        """Gets the BoxingLogger object .
        """
        return self._box_log_utils

    @property
    def map_id(self) -> str:
        """Gets the map identifier.
        """
        return self._map_id

    @property
    def logger(self) -> logging:
        """Gets the logger object.
        """
        return self._logger

    @property
    def skus_not_processed(self) -> Dict:
        """Gets skus_not_processed.
        """
        return self._skus_not_processed
    


    
