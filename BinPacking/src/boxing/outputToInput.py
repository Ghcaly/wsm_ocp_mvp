
from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from typing import List, Dict, Tuple, Set, Optional
import logging
from boxing.input import Input
from boxing.output import Output


import numpy as np

class OutputToInput(ABC):
  
    def __init__(
        self,
        name: str,
        output: Output,
        original_input: Input,
        step_name: str,
        number_of_boxes: int
    ) -> None:

        """
        Represents a generic object that processes the output of
        a previous step and transforms it in an input for the next step.
        Args:
            name: object name,
            output: output of the previous step,
            original_input: algorithm input,
            step_name: next step's name,
            number_of_boxes: number of available boxes
        """
        self._name = name
        self._output = output
        self._original_input = original_input
        self._step_name = step_name
        self._number_of_boxes = number_of_boxes
    
    @property
    def step_name(self) -> str:
        """Gets next step's name
        """
        return self._step_name
    
    @property
    def original_input(self) -> Input:
        """Gets algorithm's original input
        """
        return self._original_input
   
    @property
    def name(self) -> str:
        """Gets object name
        """
        return self._name

    @property
    def output(self) -> Output:
        """Gets previous step's output
        """
        return self._output

    @property
    def number_of_boxes(self) -> int:
        """Gets number of boxes
        """
        return self._number_of_boxes

    def get_best_box_garrafeira(self, 
                                boxes_info: Dict) -> Tuple:
        box_diameter = 0 
        box_key = ''
        for b in boxes_info.keys():
            if boxes_info[b].box_slot_diameter > box_diameter:
                box_key = b
                box_diameter = boxes_info[b].box_slot_diameter

        return boxes_info[box_key], box_key

    def get_best_box_caixa(self, 
                           boxes_info: Dict) -> Tuple:
        box_volume = 0 
        box_key = ''
        for b in boxes_info.keys():
            box_vol = boxes_info[b].length*boxes_info[b].width*boxes_info[b].height
            if box_vol > box_volume:
                box_key = b
                box_volume = box_vol

        return boxes_info[box_key], box_key



    def apply(
        self
    ) -> Input:

        """This method processes an output object into an input object
        """
        boxes_inf= {}
        for bi in self.original_input.boxes.keys():
            
            if self.original_input.boxes[bi].box_type.lower() == self.step_name.lower():
                boxes_inf[str(bi)] = self.original_input.boxes[bi]

        if self.step_name.lower() == 'garrafeira':
            box_step, box_step_key = self.get_best_box_garrafeira(boxes_inf)
        elif self.step_name.lower() == 'caixa':
            box_step, box_step_key = self.get_best_box_caixa(boxes_inf)


        box_dict = {}
        box_dict[box_step_key] = box_step
        input_result = Input(self.name, 
                  orders = self.output.new_orders, 
                  skus_info = self.original_input.skus, 
                  boxes_info = box_dict,
                  number_of_boxes = self.number_of_boxes,
                  max_weight = self.original_input.max_weight)

        return input_result
    
        