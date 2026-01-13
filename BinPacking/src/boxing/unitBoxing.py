import os
import traceback
import time
from typing import Dict

from boxing.input import Input
from boxing.configuration import Configuration
from boxing.orders import Orders
from boxing.boxes import Boxes
from boxing.items import Items
from boxing.packer import BoxerPacker
from boxing.utils import Utils
from boxing.logger import BoxingLogger
from boxing.family_separator import FamilySeparator
from boxing.final_result_processor import finalResultProcessor
from boxing.sku_checker import skuChecker

class UnitBoxing:

    """Represents the class that calls all routines for the algorithm.
    """

    def __init__(
        self,
        json_input: Dict,
        verbose: bool
    ) -> None:

        self._json_input = json_input
        self._number_of_boxes = 100
        self._verbose = verbose

    @property
    def json_input(self) -> Dict:
        return self._json_input

    @property
    def number_of_boxes(self) -> int:
        return self._number_of_boxes

    @property
    def verbose(self) -> bool:
        return self._verbose

    def apply(self):
        start_time = time.time()
        directory_path = str(os.path.abspath(os.getcwd()))
        config = Configuration(filepath=directory_path)
        map_number = list(self.json_input.keys())[0]
        map_config = self.json_input[map_number]
        sku_checker = skuChecker()
        box_log_utils = BoxingLogger(
            name='unitBoxing_log', map_id=map_number, verbose=self.verbose)
        logger = box_log_utils.logger
        logger.info(f'INPUT: {self.json_input}')
        try:
            map_boxes = self.json_input['boxes']
            algo_boxes = {b: Boxes(
                box_name=b, input_data=map_boxes[b], map_id=map_number, verbose=self.verbose) for b in map_boxes.keys()}
            map_items = self.json_input['skus']
            algo_items = {s: Items(
                promax_code=s, input_data=map_items[s], map_id=map_number, verbose=self.verbose) for s in map_items.keys()}
            new_map_config, nao_paletizados = sku_checker.check_all_skus_missing(map_config, algo_items)
            input_orders = Orders(
                input_data=new_map_config, map_number=map_number)
            logger.debug(
                f"Orders by invoice: {input_orders.orders_by_invoice}")
            family_separator = FamilySeparator(algo_items, map_number, self.json_input['family_groups'], self.verbose)
            groups = family_separator.group_families(input_orders)
            orders_by_family = family_separator.filter_maps(input_orders, groups)
            group_results = []
            for obf in orders_by_family:
                group_orders_by_invoice = Orders(input_data=obf, map_number=map_number)
                algo_input = Input('original_input', orders=group_orders_by_invoice, skus_info=algo_items,
                                boxes_info=algo_boxes, number_of_boxes=self.number_of_boxes, max_weight=config.max_weight)
                box_log_utils.logging_input(
                    input=algo_input, logger=logger, name='unit_boxing', print_full_info=True, mode='debug')
                logger.debug("Calling BoxerPacker...")
                boxer_packer = BoxerPacker(
                    general_input=algo_input, config=config, verbose=self.verbose, map_id=map_number)
                result, nao_paletizados_pt2 = boxer_packer.apply()
                utils = Utils()
                nao_paletizados = utils.refactor_item_list(
                    algo_items, nao_paletizados, nao_paletizados_pt2)
                if os.path.exists(directory_path + '/results/') == False:
                    os.mkdir(directory_path + '/results/')
                utils.write_json(json_filename=directory_path +
                                '/results/result.json', json_content=result)
                result['nao_paletizados'] = [nao_paletizados]
                group_results.append(result)
                logger.info(f"Result = {result}")
            final_result_processor = finalResultProcessor()
            final_result =final_result_processor.join_final_result(group_results)
            return final_result
        except Exception as e:
            err_stck = ''.join(map(lambda x: str(x).replace(
                '\n', ' -- '), traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            logger.error(
                f"Fatal error in execution. - message: {e}, stack trace: {err_stck}")
            exec_time_secs = (time.time() - start_time)
            raise
