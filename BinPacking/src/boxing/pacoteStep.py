import logging
import traceback
import copy
from typing import List, Dict, Tuple, Set, Optional 

from boxing.pacote_step_weight_checker import PacoteStepWeightChecker
from boxing.step import Step
from boxing.input import Input
from boxing.output import Output
from boxing.orders import Orders 
from boxing.boxes import Boxes
from boxing.items import Items
from boxing.utils import Utils
from boxing.logger import BoxingLogger


class PacoteStep(Step):
    
    """First phase of the boxing algorithm: check for SKUs that can stay in their original packages
    Ex: if an order placed has 13 Red Label bottles and the supplier sends them in boxes of 12 bottles,
    the algorithm instructs to get a full closed box and the remaining bottle goes to the next part of the 
    algorithm
    """

    def __init__(
        self,
        verbose: bool,
        map_id: str
    ) -> None:
        super().__init__(name = 'Pacote', map_id = map_id, verbose = verbose)

    def calculate_closed_packages(
        self,   
        units_in_box: int,
        order: Dict,
        sku: str,
        orders: Dict,
        items: Dict[str, Items],
        closed_skus: Dict,
        od_i: int,
        only_one_item: List,
        max_weight: float
    ) -> Dict:
        
        if units_in_box > 1:
            qt_sku_order = order[sku]
            package_weight = PacoteStepWeightChecker().calculate_package_weight(sku, items, max_weight)
            if qt_sku_order >= units_in_box and package_weight:
                qt_in_boxes = (qt_sku_order - (qt_sku_order%units_in_box))
                closed_skus[sku] = closed_skus[sku] + int(qt_in_boxes)
                orders[od_i][sku] = int(orders[od_i][sku]) - int(qt_in_boxes)
        else: 
            only_one_item.append(sku)
            self.logger.warning(f'Weight violation - SKU {sku} cannot be placed in a closed package due to excess weight - will be considered as having one unit in closed package')
        return {'orders': orders, 'closed_skus': closed_skus, 'only_one_item': only_one_item}

    def refactor_new_orders(
        self,
        orders: Dict
    ) -> Dict:
        new_orders = copy.deepcopy(orders)
        for od in orders.keys():
            for s in orders[od].keys():
                if orders[od][s] == 0:
                    new_orders[od].pop(s)
            if new_orders[od] == {}:
                new_orders.pop(od)
        return new_orders
    

    def apply(
        self,
        step_input: Input
    ) -> Tuple:

        """Applies the main procedures for this class, identifying what items 
        can stay in their original packaging. 
        """
        new_orders = {}
        try:
            self.logger.debug('Entering apply function from PacoteStep class...')
            input_pacotes = step_input
            self.box_log_utils.logging_input(input = input_pacotes,
                                        logger = self.logger,
                                        name = 'pacote_step')
            original_orders = input_pacotes.orders.orders_by_invoice
            items = input_pacotes.skus
            closed_skus = {k:0 for k in items.keys()}
            orders = copy.deepcopy(original_orders)
            self.logger.debug('Calculating Items and quantities that can stay in their original closed packages...')
            only_one_item = []
            for od in orders.keys():

                order = orders[od]
                for sku in order.keys():
                    if sku in list(items.keys()):
                        units_in_box = items[sku].units_in_boxes

                        closed_packages_result = self.calculate_closed_packages(
                                                                               units_in_box = units_in_box,
                                                                               order = order,
                                                                               sku = sku,
                                                                               orders = orders,
                                                                               items = items,
                                                                               closed_skus = closed_skus,
                                                                               od_i = od,
                                                                               only_one_item = only_one_item,
                                                                               max_weight = step_input.max_weight
                                                                               )
                        orders = closed_packages_result['orders']
                        closed_skus = closed_packages_result['closed_skus']
                        only_one_item = closed_packages_result['only_one_item']
                    else:
                        self.logger.error(f'Item {sku} - INFORMATION NOT FOUND.')

            if len(only_one_item) > 0:
                self.logger.warning(f'SKUs that have only 1 unit in closed package: {only_one_item}')
            closed_skus_final = {}
            for cs in closed_skus.keys():
                if closed_skus[cs] > 0:
                    closed_skus_final[cs] = closed_skus[cs] 
            new_orders = self.refactor_new_orders(orders = orders)
            self.logger.debug(f'New orders result: {new_orders}, closed skus result: {closed_skus_final}')
            output = Output(name = 'PacoteOutput', new_orders = new_orders, step_result = closed_skus_final, map_number = input_pacotes.orders.map, skus_not_processed = {}, verbose = self.verbose)
            return output
        except Exception as e:
            err_stck = ''.join(map(lambda x: str(x).replace('\n', ' -- '), traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            self.logger.error(f"Applying PacoteStep: fatal error in execution. - message: {e}, stack trace: {err_stck}")
            raise
            