import json
from typing import Dict

class TReadFakeInput:

    """Represents a mock class to test the algorithm.
    """

    def __init__(
        self,
        name: str,
        input_file:str,
        map_number: str,
        number_of_boxes: int,
        max_weight: float
    ) -> None:
        """
        Args:
            name: input name 
            orders: orders object - skus and respective quantity groupes by invoice number.
            skus_info: information about skus (dimensions, quantity by closed package).
            boxes_info: information about boxes (dimensions, box type).
            number_of_boxes: max number of available boxes
            max_weight: max weight for each box
        """

        self._input_file = input_file
        self._name = name
        with open(input_file) as json_file:
            data = json.load(json_file)
        self._map = data[map_number]
        self._skus = data['skus']
        self._boxes = data['boxes']
        self._number_of_boxes = number_of_boxes
        self._max_weight = max_weight

    @property
    def boxes(self) -> Dict:
        """Gets boxes info
        """
        return self._boxes 

    @property
    def number_of_boxes(self) -> Dict:
        """Gets number of boxes info
        """
        return self._number_of_boxes 

    @property
    def input_file(self) -> str:
        """Gets the input file name
        """
        return self._input_file

    @property
    def name(self) -> str:
        """Gets the customer code
        """
        return self._name            

    @property
    def map(self) -> Dict:
        """Gets the input map
        """
        return self._map

    @property
    def skus(self) -> Dict:
        """Gets the skus' info
        """
        return self._skus

    @property
    def max_weight(self) -> float:
        """Gets max weight
        """
        return self._max_weight
