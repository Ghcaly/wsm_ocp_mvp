from py3dbp import Packer, Bin, Item

from boxing.step import Step
from boxing.input import Input
from boxing.output import Output
from boxing.boxes import Boxes
from boxing.items import Items
import traceback

from typing import Dict, Tuple
import copy

from boxing.caixa_step_weight_checker import CaixaStepWeightChecker



class CaixaStep(Step):

    """Last phase of the boxing algorithm: put SKUs into boxes. 
       Inherits class Step.
    """

    def __init__(
        self,
        verbose: bool,
        map_id: str
    ) -> None:
        super().__init__('Caixa', map_id = map_id, verbose = verbose)

       
    def apply(
        self,
        step_input: Input
    ) -> Output:
        """Applies procedures

            Args:
                step_input: Input object.
        """
        try: 
            input_caixa = step_input
            initial_orders = input_caixa.orders.orders_by_invoice
            items = input_caixa.skus
            boxes = input_caixa.boxes
        
            self.box_log_utils.logging_input(input = input_caixa,
                                        logger = self.logger,
                                        name = 'caixa_step')
            skus_not_processed = {}
            if boxes != {}:
                result = {}
                for b in boxes.keys():
                    box_info = boxes[b]
                    orders_result = self.skus_to_step(original_orders = initial_orders, 
                                              step_input = step_input,
                                              box = box_info,
                                              skus_info = items)
                    if orders_result != {}:

                        next_orders = orders_result['new_orders']
                        orders = orders_result['skus_final']
                        skus_not_processed = orders_result['skus_not_processed_final']

                        homogeneous_boxes_result = self.homogeneous_boxes(orders, box_info, items)

                        homogeneous_boxes = homogeneous_boxes_result['hom_boxes']
                        new_orders_hom =  homogeneous_boxes_result['new_orders']

                        heterogeneous_boxes_result = self.heterogeneous_boxes(
                                                            orders = new_orders_hom, 
                                                            box = box_info, 
                                                            skus = items,
                                                            max_weight = step_input.max_weight)
                     
                        heterogeneous_boxes = heterogeneous_boxes_result['het_boxes']
                        new_orders_het =  heterogeneous_boxes_result['new_orders']
                
                        orders = new_orders_het
                        result = self.general_result(homogeneous_boxes, heterogeneous_boxes)
                    self.logger.debug(f'caixaStep - Heterogeneous boxes: {heterogeneous_boxes}. Homogeneous boxes: {homogeneous_boxes}.')
                    output = Output(name = 'CaixaOutput', new_orders = next_orders, step_result = result, map_number = input_caixa.orders.map, skus_not_processed = skus_not_processed, verbose = self.verbose)
                    return output
            else:
                self.logger.warning('No boxes for this step.')
                return {}

        except Exception as e:
            err_stck = ''.join(map(lambda x: str(x).replace('\n', ' -- '), traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            self.logger.error(f"Applying CaixaStep: fatal error in execution. - message: {e}, stack trace: {err_stck}")
            raise        
    
    def get_not_processed_items(self,
                                skus_not_processed: Dict) -> Dict:
        skus_not_processed_final = {}
        for s in skus_not_processed.keys():
                if skus_not_processed[s] > 0:
                    skus_not_processed_final[s] = skus_not_processed[s]

        return skus_not_processed_final
        
    def sub_skus_to_step(self,
                         order: Dict,
                         skus_info: Dict,
                         skus_boxes: Dict,
                         skus: Dict,
                         new_orders: Dict,
                         box: Dict,
                         skus_not_processed: Dict) -> Tuple:
        for ok in order.keys():
            [tad, qt_tad]  = skus_info[ok].test_all_dimensions('CAIXA STEP')
            [fib, qt_fib] = skus_info[ok].fit_in_box(box)
            if skus_boxes[ok] == 1 and tad and fib:
                        
                qt_sku_order = order[ok]
                skus[ok] = skus[ok] + int(qt_sku_order)
                new_orders.pop(ok)
            else:
                skus_not_processed[ok] = skus_not_processed[ok] + order[ok]
        return (skus_not_processed, new_orders, skus)
        

    def skus_to_step(
        self, 
        original_orders: Dict,
        step_input: Input,
        box: Dict,
        skus_info: Items
        ) -> Dict:

            
            """Group SKUs from order to promax code  

            Args:
                original_orders: orders from input - skus grouped by invoice number
            """
            self.logger.debug('Getting SKUs that will be processed in pacoteStep...')
            orders = copy.deepcopy(original_orders)
            skus = {s:0 for s in step_input.skus.keys()}
            skus_not_processed = {s:0 for s in step_input.skus.keys()}
            skus_boxes = {s:1 for s in step_input.skus.keys()}
            new_orders = {}
            skus_final = {}
            remaining_orders = {}
            for od in orders.keys():
                order = orders[od]
                new_orders = copy.deepcopy(order)
                (skus_not_processed, new_orders, skus) = self.sub_skus_to_step(order,
                                                                                skus_info,
                                                                                skus_boxes,
                                                                                skus,
                                                                                new_orders,
                                                                                box,
                                                                                skus_not_processed)
            if new_orders != {}:
                remaining_orders[od] = new_orders   
            for s in skus.keys():
                if skus[s] > 0:
                    skus_final[s] = skus[s]
            skus_not_processed_final = self.get_not_processed_items(skus_not_processed)
            self.logger.debug(f'New Orders: {new_orders}. Grouped SKUs = {skus_final}. Not processed SKUs/respective quantities: {skus_not_processed_final}')

            return {'new_orders':remaining_orders, 'skus_not_processed_final': skus_not_processed_final, 'skus_final':skus_final}

    def get_boxes_in_packer(
        self,
        box_limit: int,
        box: Dict[str, Boxes],
        packer_obj: Packer,
        max_weight: float
    ) -> Packer: 
        """Adds boxes as a parameter for the packer object  

        Args:
            box_limit: max number of boxes that can be used
            box: information about the box in which the SKUs will be placed
            packer_obj: packer object
        """
        self.logger.debug('Adding boxes as parameters...')
        for i in range(1,box_limit+1):
            packer_obj.add_bin(Bin(i, box.width, box.height, box.length, max_weight))
        return packer_obj
    
    def get_skus_in_packer(
        self,
        box_limit: int,
        box: Dict,
        orders: Dict,
        skus: Dict,
        packer_obj: Packer
    ) -> Packer: 
        """Adds items as a parameter for the packer object  

        Args:
            box_limit: max number of boxes that can be used
            box: information about the box in which the SKUs will be placed
            orders: orders to be packed (SKUs and respective quantity)
            skus: information about the SKUs to be placed into boxes
            packer_obj: packer object
        """

        self.logger.debug('Adding items as parameters...')
 
        for sk in orders.keys():
            
            sku_name = sk
            sku_width = skus[sk].width
            sku_height = skus[sk].height
            sku_length = skus[sk].length
            sku_weight = skus[sk].gross_weight
            for _ in range(orders[sk]):
                packer_obj.add_item(Item(sku_name, sku_width, sku_height, sku_length, sku_weight))
        return packer_obj

    def refactor_packer_result_het_boxes(
        self,
        packer_obj: Packer,
        orders: Dict
    ) -> Dict:
        """Refactors final result from the packer heuristic (heterogeneous boxes)  

        Args:
            orders: orders to be packed (SKUs and respective quantity)
            packer_obj: packer object
        """

        self.logger.debug('Refactoring heuristics results...')
        het_boxes = {}
        packed_skus = {}
        for b in packer_obj.bins:
            het_boxes_bins = {}
            for item in b.items:
                if item.name in het_boxes_bins.keys():
                    het_boxes_bins[item.name] = het_boxes_bins[item.name] + 1
                else:
                    het_boxes_bins[item.name] = 1
                if item.name in packed_skus.keys():
                    packed_skus[item.name] = packed_skus[item.name] + 1
                else:
                    packed_skus[item.name] = 1

            if het_boxes_bins != {}:
                het_boxes[b.name] = het_boxes_bins
        
        return {'het_boxes': het_boxes, 'packed_skus': packed_skus}

    def refactor_packer_result_new_orders(
        self,
        orders: Dict,
        het_boxes: Dict,
        packed_skus: Dict
    ) -> Dict:
        """Refactors new orders - orders configurations after the boxes' configurations
           are obtained  

        Args:
            orders: orders to be packed (SKUs and respective quantity)
            het_boxes: configurations of heterogeneous boxes
            packer_obj: packer object
        """
        new_orders = {}
        for sk in orders.keys():
            if sk in packed_skus.keys():
                new_orders[sk] = orders[sk] - packed_skus[sk]
            else:
                new_orders[sk] = orders[sk]
        return new_orders


    def heterogeneous_boxes(
        self,
        orders, 
        skus, 
        box,
        max_weight,
        box_limit = 50
    ) -> Dict:

        """Returns the configuration of heterogeneous boxes - that is, boxes that might have more
           than one type of SKU  

        Args:
            orders: orders with SKUs and respective quantity
            box: information about the box in which the SKUs will be placed
            skus: information about the skus (dimensions)
            box_limit: max number of boxes that can be used (setted as 50 as a default)
        """        
        self.logger.debug('Calculating heterogeneous boxes configurations using the py3dbp heuristics...')

        
        packer_obj = self.get_boxes_in_packer(
                                            box_limit = box_limit, 
                                            box  = box, 
                                            packer_obj = Packer(),
                                            max_weight = max_weight
                                            ) 
        

        packer_obj = self.get_skus_in_packer(
                                            box_limit = box_limit, 
                                            box = box, 
                                            orders = orders, 
                                            skus = skus, 
                                            packer_obj = packer_obj
                                            )

        

        packer_obj.pack(distribute_items=True)

        refactored_result = self.refactor_packer_result_het_boxes(packer_obj = packer_obj, orders = orders)
        
        het_boxes = refactored_result['het_boxes']
        packed_skus = refactored_result['packed_skus']

        new_orders = self.refactor_packer_result_new_orders(orders = orders, het_boxes = het_boxes, packed_skus = packed_skus) 
        
        
        self.logger.debug(f'Final result - heterogeneous boxes: {het_boxes} - new_orders: {new_orders}')

        for hb in het_boxes.keys():
            het_box_weight = CaixaStepWeightChecker().calculate_box_weight(het_boxes[hb], skus)
            het_box_occupied_vol = CaixaStepWeightChecker().calculate_box_occupation_volume(het_boxes[hb], skus, box)
            self.logger.debug(f'Heterogeneous box {hb}: weight = {het_box_weight} kg - occupied volume = {het_box_occupied_vol:.2f} % ')
 
        return {'het_boxes':het_boxes, 'new_orders':new_orders}

    def general_result(
        self,
        homogeneous_boxes: Dict,
        heterogeneous_boxes: Dict
        ) -> Dict:
        """Refactors general result (heterogeneous and homogeneous boxes)

        Args:
            homogeneous_boxes: configurations of homogeneous boxes
            heterogeneous_boxes: configurations of heterogeneous boxes
        """

        self.logger.debug('Refactoring all results...')
        result = copy.deepcopy(homogeneous_boxes)
        if homogeneous_boxes == {}:
            return heterogeneous_boxes
        elif heterogeneous_boxes == {}:
            return homogeneous_boxes 
        else:
            number_of_homogeneous_boxes = max(result.keys())
            number_of_heterogeneous_boxes = len(heterogeneous_boxes)
    
            for i in range(1,number_of_heterogeneous_boxes+1):
                result[number_of_homogeneous_boxes+i] = heterogeneous_boxes[i]
        
            return result
        
    def howManyInBoxes(
        self,
        box: Boxes,
        sku_info:Dict,
    ) -> int:

        """Group SKUs from order to promax code  

        Args:
            original_orders: orders from input - skus grouped by invoice number
        """
        dimension_box_height = box.height
        dimension_box_length = box.length
        dimension_box_width = box.width
        box_dimensions = {
            'height': dimension_box_height, 
            'length':dimension_box_length, 
            'width':dimension_box_width
            }
        sku_dimensions = {
            'height':{'value':sku_info.height, 'dim1': 'length', 'dim2':'width'}, 
            'length':{'value':sku_info.length, 'dim1': 'height', 'dim2':'width'}, 
            'width':{'value':sku_info.width, 'dim1': 'height', 'dim2':'length'}
            }
        def fit_in_box(sku_measure, box_measure):
            """Checks if SKU dimension fits into box dimension
               ex: comparing the height of a SKU with the height of the box in order 
               to see if the SKU fits standing up 

            Args:
                sku_measure: measure (height, width or length in cm) of the SKU
                box_measure: measure (height, width or length in cm) of the box
            """
            if sku_measure <= box_measure:
                return True
            else:
                return False

        def how_many_times_fits_in_box(sku_measure, box_measure):
            """Returns how many of a SKU given dimension fits in a box's given dimension 
               ex: if we want to place a SKU standing up in a box, how many SKUs of this type
               can we stack on top of one another without exceeding the box's height?   

            Args:
                sku_measure: measure (height, width or length in cm) of the SKU
                box_measure: measure (height, width or length in cm) of the box
            """
            return int((box_measure - (box_measure%sku_measure))/sku_measure)

        def area_that_fits_in_box(dimension_sku_1, dimension_sku_2, dimension_box_1, dimension_box_2):
            """Checks if SKU area fits into box area
               ex: if we want to place a SKU standing up in a box, how many SKUs of this type
               can we place side by side standing up without exceeding the box's base area? 

            Args:
                dimension_sku_1: measure 1 (height, width or length in cm) of the SKU
                dimension_sku_2: measure 2 (height, width or length in cm - must be different
                from dimension_sku_1) of the SKU
                dimension_box_1: measure 1 (height, width or length in cm) of the box
                dimension_box_2: measure 2 (height, width or length in cm - must be different
                from dimension_sku_1) of the box
            """
            result = 0
            if (fit_in_box(dimension_sku_1, dimension_box_1) == True) and (fit_in_box(dimension_sku_2, dimension_box_2) == True):
                fit_1 = how_many_times_fits_in_box(dimension_sku_1, dimension_box_1)
                fit_2 = how_many_times_fits_in_box(dimension_sku_2, dimension_box_2)
                result = fit_1*fit_2

            return result




        sku_quantity = []
        for sd in box_dimensions.keys():
            
            dimension_main = box_dimensions["height"] 

            #dim1
            dimension_main_sku = sku_dimensions[sd]['value']
            dimension1_1 = sku_dimensions[sku_dimensions[sd]['dim1']]['value']
            dimension2_1 = sku_dimensions[sku_dimensions[sd]['dim2']]['value']

            dimension1_2 = sku_dimensions[sku_dimensions[sd]['dim2']]['value']
            dimension2_2 = sku_dimensions[sku_dimensions[sd]['dim1']]['value']

            result_general = 0
            result_case_1 = 0 
            result_case_2 = 0
            if fit_in_box(dimension_main_sku, dimension_main) == True:

                #case 1 

                result_case_1 = area_that_fits_in_box(
                                    dimension1_1, 
                                    dimension1_2, 
                                    box_dimensions['length'], 
                                    box_dimensions['width'])
                #case 2
                result_case_2 = area_that_fits_in_box(
                                    dimension2_1, 
                                    dimension2_2, 
                                    box_dimensions['length'], 
                                    box_dimensions['width']
                                    )
                result_general = max(result_case_1, result_case_2)*how_many_times_fits_in_box(dimension_main_sku, dimension_main)
            
            sku_quantity.append(result_general)
        return max(sku_quantity)

        
    def homogeneous_boxes(
        self,
        orders,
        box,
        skus
    ) -> Dict:

        """Returns the configuration of homogeneous boxes - that is, boxes that have only one
           type of SKU  

        Args:
            orders: orders with SKUs and respective quantity
            box: information about the box in which the SKUs will be placed
            skus: information about the skus (dimensions)
        """
        self.logger.debug('Calculating homogeneous_boxes in caixaStep...')
        hom_boxes = {}
        new_orders_to_het_boxes = {}
        hom_boxes_numbers = 0
        capacities = {}
        not_palletized = {}
        
        for s in orders.keys():
            box_configuration = {}
           
            sku_quantity_capacity = self.howManyInBoxes(
                                        box = box, 
                                        sku_info = skus[s])
            capacities[s] = sku_quantity_capacity
            if sku_quantity_capacity > orders[s]:
                new_orders_to_het_boxes[s] = orders[s]
              
            else:
                if sku_quantity_capacity >=1:
                    sku_to_heterogeneous_boxes = orders[s]%sku_quantity_capacity
                    sku_to_homogeneous_boxes_qt_boxes = int((orders[s]-sku_to_heterogeneous_boxes)/sku_quantity_capacity)
                    box_configuration = {s:sku_quantity_capacity}
                
                    for i in range(hom_boxes_numbers+1, hom_boxes_numbers+sku_to_homogeneous_boxes_qt_boxes + 1):
                        hom_boxes[i] = box_configuration
                        hom_boxes_numbers = hom_boxes_numbers + 1
                    if sku_to_heterogeneous_boxes > 0:
                        new_orders_to_het_boxes[s] = sku_to_heterogeneous_boxes
                else:
                    not_palletized[s] = orders[s]
        self.logger.debug(f'result of how many fits in box for each SKU = {capacities}')
        self.logger.debug(f'homogeneous boxes = {hom_boxes}')
        self.logger.debug(f'items to heterogeneous boxes = {new_orders_to_het_boxes}')

        return {'hom_boxes': hom_boxes, 'new_orders': new_orders_to_het_boxes, 'not_palletized': not_palletized}






