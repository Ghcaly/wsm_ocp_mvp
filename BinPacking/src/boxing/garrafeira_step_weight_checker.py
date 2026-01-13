import logging
import traceback
from typing import List, Dict, Tuple, Set, Optional
import numpy as np
import pandas as pd
import copy

from boxing.step import Step
from boxing.input import Input
from boxing.output import Output
from boxing.logger import BoxingLogger

from boxing.logger import BoxingLogger

class GarrafeiraStepWeightChecker:


    def __init__(
        self,
        name: str,
        map_id: str,
        verbose: bool
    ) -> None:
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
    

    def calculate_box_weight(
        self,
        box: Dict,
        step_input: Input) -> float:

        box_skus = list(box.keys())

        box_weight = 0

        for bs in box_skus:
            box_weight = box_weight + box[bs]*step_input.skus[bs].gross_weight

        return box_weight

    def max_weight_is_maintained(
        self,
        box: Dict,
        step_input: Input,
        sku: int,
        box_weight: float,
        sku_qt: int) -> bool:


        if box_weight + step_input.skus[sku].gross_weight*sku_qt <= step_input.max_weight:
            return True
        else:
            return False
    def get_lightest_type_box(
        self,
        boxes:Dict,
        step_input: Input,
        sku: int,
        space_box: int) -> Tuple:
        lightest_type_box = str()
        lightest_type_box_weight = 100.1
        candidate_box_found = 0
        if boxes == {}:
            return None, None
        
        for b in list(boxes.keys()):
            box_config = boxes[b]
            if np.array(list(box_config.values())).sum() < space_box:
                box_weight = self.calculate_box_weight(box = box_config, step_input = step_input)
                if self.max_weight_is_maintained(box = box_config,
                                                 step_input = step_input,
                                                 sku = sku,
                                                 box_weight = box_weight,
                                                 sku_qt = 1) == True and box_weight < lightest_type_box_weight:
                    candidate_box_found = 1
                    lightest_type_box = b 
                    lightest_type_box_weight = box_weight
        if candidate_box_found == 0:
            return None, None

        return lightest_type_box, lightest_type_box_weight


    def compare_box_types_weight(
        self,
        box1:str,
        box1_weight: float,
        box2:str,
        box2_weight: float,
        box1_type: str,
        box2_type:str) -> Tuple:


        if box1_weight < box2_weight:
            return box1, box1_type, box1_weight
        else:
            return box2, box2_type, box2_weight

    def sku_is_different_from_box(
        self,
        box_config: Dict,
        sku: int) -> bool:

        if list(box_config.keys())[0] != sku:
            return True
        else:
            return False

    def get_lightest_box(
        self,
        homogeneous_boxes: Dict,
        heterogeneous_boxes: Dict,
        sku: int,
        step_input: Input,
        space_box: int) -> Tuple:
       
        lightest_homogeneous_box, lightest_homogeneous_box_weight = self.get_lightest_type_box(boxes = homogeneous_boxes,
                                                                    step_input = step_input,
                                                                    sku = sku,
                                                                    space_box = space_box)

        lightest_heterogeneous_box, lightest_heterogeneous_box_weight = self.get_lightest_type_box(boxes = heterogeneous_boxes,
                                                                        step_input = step_input,
                                                                        sku = sku,
                                                                        space_box = space_box)
        
        if lightest_homogeneous_box == None and lightest_heterogeneous_box != None:
            return lightest_heterogeneous_box, "heterogeneous", lightest_heterogeneous_box_weight
        elif lightest_heterogeneous_box == None and lightest_homogeneous_box != None:
            return lightest_homogeneous_box, "homogeneous", lightest_homogeneous_box_weight
        elif lightest_heterogeneous_box == None and lightest_homogeneous_box == None:
            return None, None, None
        else:
            lightest_box, lightest_box_type, lightest_box_weight = self.compare_box_types_weight(box1 = lightest_homogeneous_box,
                                                                                            box1_weight = lightest_homogeneous_box_weight,
                                                                                            box2 = lightest_heterogeneous_box,
                                                                                            box2_weight = lightest_heterogeneous_box_weight,
                                                                                            box1_type = 'homogenneous',
                                                                                            box2_type = 'heterogeneous')
        if lightest_box == {}:
            return None, None, None

        else: 
            return lightest_box, lightest_box_type, lightest_box_weight

    def remove_homogeneous_box(
        self,
        homogeneous_boxes: Dict,
        box_to_remove: str) -> Dict: 

        new_homogeneous_boxes = {}

        homogeneous_boxes_copy = copy.deepcopy(homogeneous_boxes)

        homogeneous_boxes_copy.pop(box_to_remove)

        hom_boxes_keys = list(homogeneous_boxes_copy.keys())
        for i in range(len(homogeneous_boxes_copy)):
            new_homogeneous_boxes[i] = homogeneous_boxes_copy[hom_boxes_keys[i]]

        return new_homogeneous_boxes

    def add_new_box_to_list(
        self,
        boxes: Dict,
        box_to_add: Dict) -> Dict:

        new_boxes = {}
        boxes_copy = copy.deepcopy(boxes)

        boxes_keys = list(boxes_copy.keys())

        for i in range(len(boxes_copy)):
            new_boxes[i] = boxes_copy[boxes_keys[i]]

        new_boxes[len(boxes_keys)] = box_to_add

        return new_boxes

    
    def homogeneous_to_heterogeneous_box(
        self,
        homogeneous_boxes: Dict,
        heterogeneous_boxes: Dict,
        box_to_change: str,
        sku_to_add: int) -> Tuple:

        new_homogeneous_boxes = self.remove_homogeneous_box(homogeneous_boxes,
                                                            box_to_change)

        new_box = self.add_sku_to_chosen_box(homogeneous_boxes[box_to_change], sku_to_add)
        new_heterogeneous_boxes = self.add_new_box_to_list(heterogeneous_boxes,
                                                           new_box)
        return new_heterogeneous_boxes, new_homogeneous_boxes 

    def add_sku_to_chosen_box(
        self, 
        box_to_add: Dict,
        sku_to_add: int) -> Dict:

        box_to_add_skus = list(box_to_add.keys())
        if box_to_add_skus != [] and sku_to_add in box_to_add_skus:
            current_quantity = box_to_add[sku_to_add]
            box_to_add[sku_to_add] = current_quantity + 1 
            return box_to_add 
        else:
            box_to_add[sku_to_add] = 1 
            return box_to_add 
       

    def replace_new_box(
        self,
        heterogeneous_boxes: Dict,
        new_box: Dict,
        box_id: str) -> Dict:
        
        heterogeneous_boxes[box_id] = new_box 

        return heterogeneous_boxes



    def choose_new_box(
        self,
        homogeneous_boxes : Dict,
        heterogeneous_boxes: Dict,
        sku: int,
        step_input: Input,
        space_box: int) -> Tuple:

        new_box, new_box_type, new_box_weight = self.get_lightest_box(homogeneous_boxes, 
                                        heterogeneous_boxes,
                                        sku,
                                        step_input,
                                        space_box)
        
        if new_box == None:
            newest_box = self.add_sku_to_chosen_box({}, sku)
            new_homogeneous_boxes = self.add_new_box_to_list(homogeneous_boxes, newest_box)
            return heterogeneous_boxes, new_homogeneous_boxes 
        elif new_box_type == 'heterogeneous':
            newest_box = self.add_sku_to_chosen_box(heterogeneous_boxes[new_box], sku)
            new_heterogeneous_boxes = self.replace_new_box(heterogeneous_boxes, newest_box, new_box)
            return new_heterogeneous_boxes, homogeneous_boxes
        elif new_box_type == 'homogeneous' and self.sku_is_different_from_box(homogeneous_boxes[new_box], 
                                                                                 sku):
            new_heterogeneous_boxes, new_homogeneous_boxes = self.homogeneous_to_heterogeneous_box(homogeneous_boxes,
                                                                                                    heterogeneous_boxes,
                                                                                                    new_box,
                                                                                                    sku)
            return new_heterogeneous_boxes, new_homogeneous_boxes                                                                                        
        elif new_box_type == 'homogeneous':

            newest_box = self.add_sku_to_chosen_box(homogeneous_boxes[new_box], sku)
            new_homogeneous_boxes = self.replace_new_box(homogeneous_boxes, newest_box, new_box)
            return heterogeneous_boxes, new_homogeneous_boxes
            
            
    def calculate_heterogeneous_box_weight(
        self,
        current_heterogeneous_box: Dict,
        step_input: Input
        ) -> float:

        if current_heterogeneous_box == {}:
            box_weight = 0.0 
        else:
            box_weight = self.calculate_box_weight(current_heterogeneous_box,step_input)

        
        return box_weight
    def sku_quantity_does_not_fill_current_heterogeneous_box_and_max_weight_is_mantained(
        self,
        part_boxes_qt: int,
        box_capacity: int,
        max_weight_maintained: bool) -> bool:

        result = False
        if part_boxes_qt > 0 and part_boxes_qt < box_capacity and max_weight_maintained:
            result = True
        return result

    def sku_quantity_fills_current_heterogeneous_box_and_max_weight_is_mantained(
        self,
        part_boxes_qt: int,
        box_capacity: int,
        max_weight_maintained: bool) -> bool:

        result = False
        if part_boxes_qt > 0 and part_boxes_qt == box_capacity and max_weight_maintained:
            result = True
        return result

    def sku_quantity_does_not_fill_current_heterogeneous_box_and_max_weight_is_not_mantained(
        self,
        part_boxes_qt: int,
        box_capacity: int,
        max_weight_maintained: bool) -> bool:

        result = False
        if part_boxes_qt > 0 and part_boxes_qt < box_capacity and max_weight_maintained == False:
            result = True
        return result
    def sku_quantity_fills_current_heterogeneous_box_and_max_weight_is_not_mantained(
        self,
        part_boxes_qt: int,
        box_capacity: int,
        max_weight_maintained: bool) -> bool:

        result = False
        if part_boxes_qt > 0 and part_boxes_qt == box_capacity and max_weight_maintained == False:
            result = True
        return result

    def sku_quantity_exceeds_current_heterogeneous_box(
        self,
        part_boxes_qt: int,
        box_capacity: int,
        max_weight_maintained: bool) -> bool:

        result = False
        if part_boxes_qt > 0 and part_boxes_qt > box_capacity:
            result = True
        return result

    
    def add_to_skus_that_exceed_max_weight(
        self,
        skus_that_exceed_max_weight: Dict,
        sku: int,
        sku_qt: int) -> Dict:

        skus_keys = list(skus_that_exceed_max_weight.keys())

        if sku in skus_keys:
            new_quantity = skus_that_exceed_max_weight[sku] + sku_qt 
            skus_that_exceed_max_weight[sku] = new_quantity 
        else:
            skus_that_exceed_max_weight[sku] = sku_qt 

        return skus_that_exceed_max_weight

    
    def add_skus_that_exceed_max_weight(
        self,
        skus_that_exceed_max_weight: Dict,
        homogeneous_boxes: Dict,
        heterogeneous_boxes: Dict,
        step_input: Input,
        space_box: int):
        self.logger.warning(f'Entered "add_skus_that_exceed_max_weight"')
        self.logger.warning(f'"skus_that_exceed_max_weight": {skus_that_exceed_max_weight}')
        skus = list(skus_that_exceed_max_weight.keys())
        new_heterogeneous_boxes = {}
        new_homogeneous_boxes = {}
        for s in skus:
            for _ in range(skus_that_exceed_max_weight[s]):
                new_heterogeneous_boxes, new_homogeneous_boxes = self.choose_new_box(new_homogeneous_boxes, new_heterogeneous_boxes, s, step_input, space_box)
        return new_heterogeneous_boxes, new_homogeneous_boxes
    
    


