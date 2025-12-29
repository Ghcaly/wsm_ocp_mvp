import traceback
from typing import Dict, Tuple, Set
import copy

from boxing.step import Step
from boxing.input import Input
from boxing.output import Output
from boxing.garrafeira_step_weight_checker import GarrafeiraStepWeightChecker

class GarrafeiraStep(Step):

    """Middle phase of the boxing algorithm: put SKUs into bottle cases. 
       Inherits class Step.
    """
   
    def __init__(
        self,
        verbose: bool,
        map_id: str
    ) -> None:
        super().__init__('Garrafeira', map_id = map_id, verbose = verbose)

    def sub_skus_to_step(
        self,
        step_input: Input,
        skus_bottles: Dict,
        skus: Dict,
        new_orders: Dict,
        order: Dict,
        not_bottle: Set,
        final_orders: Dict,
        box: Dict,
        od: str
        ) -> Tuple:

        for sku in order.keys():
            [fib, qt_fib] = step_input.skus[sku].fit_in_box(box)
            if skus_bottles[sku] == 1 and fib:
                qt_sku_order = order[sku]
                skus[sku] = skus[sku] + int(qt_sku_order)
                new_orders.pop(sku)
            else:
                not_bottle.add(sku)                        
        if new_orders != {}:
            final_orders[od] = new_orders  
        return (final_orders, skus, not_bottle, skus_bottles)


    def skus_to_step(
        self, 
        original_orders: Dict,
        step_input: Input,
        box: Dict
        ) -> Dict:
            self.logger.debug('Getting SKUs that will be processed in garrafeiraStep...')
            orders = copy.deepcopy(original_orders)
            skus = {s:0 for s in step_input.skus.keys()}
            skus_bottles = {s:step_input.skus[s].is_bottle for s in step_input.skus.keys()}
            final_orders = {}
            skus_final = {}
            new_orders = {}
            not_bottle = set()
            for od in orders.keys():
                order = orders[od]
        
                new_orders = copy.deepcopy(order)
                (final_orders, skus, not_bottle, skus_bottles) =  self.sub_skus_to_step(step_input,
                                                                                        skus_bottles,
                                                                                        skus,
                                                                                        new_orders,
                                                                                        order,
                                                                                        not_bottle,
                                                                                        final_orders,
                                                                                        box,
                                                                                        od)
            for s in skus.keys():
                if skus[s] > 0:
                    skus_final[s] = skus[s]
            self.logger.debug(f'Skus that are not bottle: {not_bottle}. New orders: {new_orders}. Grouped bottle SKUs = {skus_final}')
        
            return {'new_orders':final_orders, 'skus_final':skus_final}
    
    def homogeneous_boxes_configuration(
        self,
        homogeneous_sku_boxes_number: int,
        homogeneous_boxes: Dict,
        space_box: int,
        homogeneous_box: int,
        sku
    ) -> Dict:
        
        if homogeneous_sku_boxes_number > 0:
                
                for i in range(homogeneous_sku_boxes_number):
                    homogeneous_boxes[i+homogeneous_box] = {sku:space_box}
                homogeneous_box = homogeneous_box + homogeneous_sku_boxes_number
        return {'homogeneous_boxes':homogeneous_boxes, 'homogeneous_box':homogeneous_box}

    def heterogeneous_boxes_configuration(
        self,
        heterogeneous_boxes: Dict,
        space_box: int,
        heterogeneous_box: int,
        part_boxes_qt: int,
        box_capacity: int,
        current_heterogeneous_box: Dict,
        sku: int,
        skus_that_exceed_max_weight: Dict,
        step_input: Input,
        weight_checker: GarrafeiraStepWeightChecker
    ) -> Dict:
       
        flag = 0
        box_weight = weight_checker.calculate_heterogeneous_box_weight(current_heterogeneous_box, step_input)

        max_weight_maintained = weight_checker.max_weight_is_maintained(current_heterogeneous_box,
                                                                              step_input,
                                                                              sku,
                                                                              box_weight,
                                                                              part_boxes_qt)
        if weight_checker.sku_quantity_does_not_fill_current_heterogeneous_box_and_max_weight_is_mantained(part_boxes_qt, 
                                                                                                     box_capacity,
                                                                                                     max_weight_maintained
                                                                                                     ):
                current_heterogeneous_box[sku] = part_boxes_qt
                flag = 1
        if weight_checker.sku_quantity_does_not_fill_current_heterogeneous_box_and_max_weight_is_not_mantained(part_boxes_qt, 
                                                                                                    box_capacity,
                                                                                                    max_weight_maintained
                                                                                                    ):
            skus_that_exceed_max_weight = weight_checker.add_to_skus_that_exceed_max_weight(skus_that_exceed_max_weight,
                                                                                        sku,
                                                                                        part_boxes_qt)
            return {'heterogeneous_boxes':heterogeneous_boxes, 'heterogeneous_box':heterogeneous_box, 'current_heterogeneous_box': current_heterogeneous_box, 'flag':flag, 'skus_that_exceed_max_weight': skus_that_exceed_max_weight}


            
            
        if weight_checker.sku_quantity_fills_current_heterogeneous_box_and_max_weight_is_mantained(part_boxes_qt, 
                                                                                                    box_capacity,
                                                                                                    max_weight_maintained
                                                                                                    ):
            current_heterogeneous_box[sku] = part_boxes_qt
            
            heterogeneous_boxes[heterogeneous_box] = copy.deepcopy(current_heterogeneous_box)
            heterogeneous_box = heterogeneous_box+1
            current_heterogeneous_box = {}
            flag = 1

        if weight_checker.sku_quantity_fills_current_heterogeneous_box_and_max_weight_is_not_mantained(part_boxes_qt, 
                                                                                                    box_capacity,
                                                                                                    max_weight_maintained
                                                                                                    ):

            skus_that_exceed_max_weight = weight_checker.add_to_skus_that_exceed_max_weight(skus_that_exceed_max_weight,
                                                                                        sku,
                                                                                        part_boxes_qt)
            return {'heterogeneous_boxes':heterogeneous_boxes, 'heterogeneous_box':heterogeneous_box, 'current_heterogeneous_box': current_heterogeneous_box, 'flag':flag, 'skus_that_exceed_max_weight': skus_that_exceed_max_weight}


        if weight_checker.sku_quantity_exceeds_current_heterogeneous_box(part_boxes_qt, 
                                                               box_capacity,
                                                               max_weight_maintained
                                                               ):

            
            leftover = part_boxes_qt - box_capacity
            max_weight_maintained = weight_checker.max_weight_is_maintained(current_heterogeneous_box,
                                                                            step_input,
                                                                            sku,
                                                                            box_weight,
                                                                            box_capacity)
                


            max_weight_new_box_maintained = weight_checker.max_weight_is_maintained(current_heterogeneous_box,
                                                                            step_input,
                                                                            sku,
                                                                            0.0,
                                                                            part_boxes_qt)
            if max_weight_maintained and max_weight_new_box_maintained:
                current_heterogeneous_box[sku] = box_capacity
                
                heterogeneous_boxes[heterogeneous_box] = copy.deepcopy(current_heterogeneous_box)
                heterogeneous_box = heterogeneous_box+1
                current_heterogeneous_box = {}
                current_heterogeneous_box[sku] = leftover
                flag = 1
            if max_weight_maintained == False or max_weight_new_box_maintained == False:
                skus_that_exceed_max_weight = weight_checker.add_to_skus_that_exceed_max_weight(skus_that_exceed_max_weight,
                                                                                        sku,
                                                                                        part_boxes_qt)
                return {'heterogeneous_boxes':heterogeneous_boxes, 'heterogeneous_box':heterogeneous_box, 'current_heterogeneous_box': current_heterogeneous_box, 'flag':flag, 'skus_that_exceed_max_weight': skus_that_exceed_max_weight}



        return {'heterogeneous_boxes':heterogeneous_boxes, 'heterogeneous_box':heterogeneous_box, 'current_heterogeneous_box': current_heterogeneous_box, 'flag':flag, 'skus_that_exceed_max_weight': skus_that_exceed_max_weight}

    def general_result_join_boxes_subtype(
        self,
        boxes: Dict, 
        new_boxes: Dict
        ) -> Dict:
        result = copy.deepcopy(boxes)
        if boxes == {}:
            return new_boxes
        elif new_boxes == {}:
            return boxes 
        else:
            number_of_boxes = len(boxes)
            number_of_new_boxes = len(new_boxes)
            for i in range(number_of_new_boxes):
                result[number_of_boxes+i] = new_boxes[i]
            return result

    def general_result(
        self,
        homogeneous_boxes: Dict,
        heterogeneous_boxes: Dict, 
        new_homogeneous_boxes: Dict, 
        new_heterogeneous_boxes: Dict
        ) -> Dict:
        
        final_new_homogeneous_boxes = self.general_result_join_boxes_subtype(homogeneous_boxes, new_homogeneous_boxes)
        final_new_heterogeneous_boxes = self.general_result_join_boxes_subtype(heterogeneous_boxes, new_heterogeneous_boxes)

        if final_new_homogeneous_boxes == {}:
            return final_new_heterogeneous_boxes
        elif final_new_heterogeneous_boxes == {}:
            return final_new_homogeneous_boxes 
        else:
            result = copy.deepcopy(final_new_homogeneous_boxes)
            number_of_homogeneous_boxes = len(final_new_homogeneous_boxes)
            number_of_heterogeneous_boxes = len(final_new_heterogeneous_boxes)
            for i in range(number_of_heterogeneous_boxes):
                result[number_of_homogeneous_boxes+i] = final_new_heterogeneous_boxes[i]
            return result

    def get_current_box_capacity(
        self,
        current_heterogeneous_box: Dict,
        space_box: int      
    ) -> int:
        
        if current_heterogeneous_box != {}:
            box_capacity = space_box - sum(current_heterogeneous_box.values())
        else:
            box_capacity = space_box
        return box_capacity

    def get_boxes_configuration(
        self,
        box_info: Dict,
        space_box: int,
        skus_final: Dict,
        step_input: Input
        ) -> Dict:

        heterogeneous_box = 0
        heterogeneous_boxes = {}
        homogeneous_box = 0
        homogeneous_boxes = {}
        new_heterogeneous_boxes = {}
        new_homogeneous_boxes = {}
        
        self.logger.debug('Getting boxes configuration for garrafeiraStep...')
        current_heterogeneous_box = {}
        flag = 0
        skus_that_exceed_max_weight = {}
        weight_checker = GarrafeiraStepWeightChecker(name = 'garrafeiraWeightChecker', map_id = self.map_id, verbose = self.verbose)

        for s in skus_final.keys():
            
            total_quantity = skus_final[s]            
            part_boxes_qt = total_quantity%space_box
            skus_to_homogeneous_boxes = total_quantity - part_boxes_qt
            
            homogeneous_sku_boxes_number = int((skus_to_homogeneous_boxes)/space_box)
            sku_will_not_be_processed_now = 0
            if homogeneous_sku_boxes_number > 0:
                homogeneous_box_weight = weight_checker.calculate_box_weight({s:space_box}, step_input)
                if homogeneous_box_weight <= step_input.max_weight:
                    homogeneous_box_result = self.homogeneous_boxes_configuration(
                                                                             homogeneous_sku_boxes_number = homogeneous_sku_boxes_number,
                                                                             homogeneous_boxes = homogeneous_boxes,
                                                                             space_box = space_box,
                                                                             homogeneous_box = homogeneous_box,
                                                                             sku = s
                                                                             )
                    homogeneous_boxes = homogeneous_box_result['homogeneous_boxes']
                    homogeneous_box = homogeneous_box_result['homogeneous_box']
                else:
                    sku_will_not_be_processed_now = 1
                    self.logger.warning(f'Weight violation - SKU {s} cannot be placed in a homogeneous bottle case due to excess weight - will be processed afterwards')
                    skus_that_exceed_max_weight = weight_checker.add_to_skus_that_exceed_max_weight(skus_that_exceed_max_weight,
                                                                                          s,
                                                                                          total_quantity)            
            if sku_will_not_be_processed_now == 0:

                box_capacity = self.get_current_box_capacity(
                                                       current_heterogeneous_box = current_heterogeneous_box,
                                                       space_box = space_box 
                                                       )
            
        
                heterogeneous_box_result = self.heterogeneous_boxes_configuration(
                                                                                 heterogeneous_boxes = heterogeneous_boxes,
                                                                                 space_box = space_box,
                                                                                 heterogeneous_box = heterogeneous_box,
                                                                                 part_boxes_qt = part_boxes_qt,
                                                                                 box_capacity = box_capacity,
                                                                                 current_heterogeneous_box = current_heterogeneous_box,
                                                                                 sku = s,
                                                                                 skus_that_exceed_max_weight = skus_that_exceed_max_weight,
                                                                                 step_input = step_input,
                                                                                 weight_checker = weight_checker
                                                                                 ) 
                heterogeneous_boxes = heterogeneous_box_result['heterogeneous_boxes']
                heterogeneous_box = heterogeneous_box_result['heterogeneous_box']
                current_heterogeneous_box = heterogeneous_box_result['current_heterogeneous_box']
                flag = heterogeneous_box_result['flag']
                skus_that_exceed_max_weight = heterogeneous_box_result['skus_that_exceed_max_weight']

        if ((heterogeneous_box >0 or flag == 1) or homogeneous_box >0) and current_heterogeneous_box != {}:
            
            heterogeneous_boxes[len(list(heterogeneous_boxes.keys()))] = copy.deepcopy(current_heterogeneous_box)
        
        if skus_that_exceed_max_weight != {}:
            new_heterogeneous_boxes, new_homogeneous_boxes = weight_checker.add_skus_that_exceed_max_weight(skus_that_exceed_max_weight,  homogeneous_boxes, heterogeneous_boxes, step_input, space_box)
        self.logger.debug(f'garrafeiraStep - Heterogeneous boxes: {heterogeneous_boxes}. Homogeneous boxes: {homogeneous_boxes}.')


        return {'heterogeneous_boxes': heterogeneous_boxes, 'homogeneous_boxes': homogeneous_boxes, 'new_heterogeneous_boxes': new_heterogeneous_boxes, 'new_homogeneous_boxes': new_homogeneous_boxes}

    
    def apply(
        self,
        step_input: Input
    ) -> Tuple:
                
        """ Applies procedures

        Args:
            step_input: Input object.
        """

        new_orders = {} 
        final_result = {}
        try:

            input_garrafeiras = step_input
            self.box_log_utils.logging_input(input = input_garrafeiras,
                                        logger = self.logger,
                                        name = 'garrafeira_step')
        
            initial_orders = input_garrafeiras.orders.orders_by_invoice
            boxes_step = input_garrafeiras.boxes
            

        
            
            if boxes_step != {}:
                for b in boxes_step.keys():
                    box_info = boxes_step[b]
                    space_box = box_info.box_slots

                    res_to_step = self.skus_to_step(initial_orders, input_garrafeiras, box_info)
                    if res_to_step != {}:

                        new_orders = res_to_step['new_orders']
                        skus_final = res_to_step['skus_final']
        
     
                        self.box_log_utils.logging_box_un(logger = self.logger,
                                                          box = box_info,
                                                          name = 'garrafeira_step',
                                                          mode = 'debug')
                
                        self.logger.debug('Calculating box configurations for garrafeiraStep...')
                
                        partial_result = self.get_boxes_configuration(box_info = box_info,
                                                                      space_box = space_box,
                                                                      skus_final = skus_final,
                                                                      step_input = step_input)

                        homogeneous_boxes = partial_result['homogeneous_boxes']
                        heterogeneous_boxes = partial_result['heterogeneous_boxes']
                        new_homogeneous_boxes = partial_result['new_homogeneous_boxes']
                        new_heterogeneous_boxes = partial_result['new_heterogeneous_boxes']


                        final_result = self.general_result(homogeneous_boxes, heterogeneous_boxes, new_homogeneous_boxes, new_heterogeneous_boxes)
            else:
                self.logger.warning('No boxes for this step.')        
            output = Output(name = 'GarrafeiraOutput', new_orders = new_orders, step_result = final_result, map_number = input_garrafeiras.orders.map, skus_not_processed = {}, verbose = self.verbose)
            return output
        except Exception as e:
        #    self.logger.error(f"Applying GarafeiraStep: fatal error in execution. - message: {e}, stack trace: {str(traceback.print_exception(etype=type(e), value=e, tb=e.__traceback__))}")
            err_stck = ''.join(map(lambda x: str(x).replace('\n', ' -- '), traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            self.logger.error(f"Applying GarafeiraStep: fatal error in execution. - message: {e}, stack trace: {err_stck}")
            raise        
            