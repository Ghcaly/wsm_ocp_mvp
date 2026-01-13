from boxing.input import Input
from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from typing import List, Dict, Tuple, Set, Optional
import logging
import numpy as np
from boxing.utils import Utils
from boxing.logger import BoxingLogger


class Step(ABC):
    
    """First phase of the boxing algorithm: check for SKUs that can stay in their original packages
    Ex: if an order placed has 13 Red Label bottles and the supplier sends them in boxes of 12 bottles,
    the algorithm instructs to get a full closed box and the remaining bottle goes to the next part of the 
    algorithm
    """

    def __init__(
        self,
        name: str,
        map_id: str,
        verbose: bool
    ) -> None:
        """Initializes the algorithm.

        Args:
            name: step name,
            map_id: map identification number,
            verbose: if True, prints logger output (default False)
        """

        self._verbose = verbose
        self._name = name 
        self._map_id = map_id
        self._box_log_utils = BoxingLogger(map_id = map_id, name = name + '_log', verbose = self.verbose)
        self._logger = self._box_log_utils.logger        

    @property
    def verbose(self) -> bool:
        """Returns verbose
        """
        return self._verbose
    
    @property
    def name(self) -> str:
        """Gets the step name.
        """
        return self._name
    
    @property
    def logger(self) -> logging:
        """Gets the logger object.
        """
        return self._logger

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
    


    @abstractmethod
    def apply(
        self,
        input: Input
    ) -> None:

        """This method must implement the logic behind the step 
        over the variables. It must be overriden in the child class.

        Args:
            input: An input to step.
            
        """
        pass

    
    def general_result(
        self,
        homogeneous_boxes: Dict,
        heterogeneous_boxes: Dict,

        ) -> Dict:

        self.logger.debug(f"Initializing abstract step class.")
        self.logger.debug(f"Initializing abstract step class.")
        result = copy.deepcopy(homogeneous_boxes)
        self.logger.debug(f"Calling function general_result from Step class.")
        self.logger.debug(f"Calling function general_result from Step class.")
        if homogeneous_boxes == {}:
            self.logger.debug(f"No homogeneous boxes, returning heterogeneous boxes.")
            return heterogeneous_boxes
        elif heterogeneous_boxes == {}:
            self.logger.debug(f"No heterogeneous boxes, returning homogeneous boxes.")
            return homogeneous_boxes 
        else:
            self.logger.debug(f"Both homogeneous and heterogeneous boxes, returning updated boxes list.")
            number_of_homogeneous_boxes = max(result.keys())
            number_of_heterogeneous_boxes = len(heterogeneous_boxes)
    
            for i in range(1,number_of_heterogeneous_boxes+1):
                result[number_of_homogeneous_boxes+i] = heterogeneous_boxes[i]
        
            return result
