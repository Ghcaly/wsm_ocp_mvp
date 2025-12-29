import logging
import logging.config
class BoxingLogger():
    """Represents the class with auxiliary functions for logs written by the library.
    """

    def __init__(
            self,
            name: str,
            map_id: str,
            verbose: False
        ) -> None:
        """Initializes the boxing logger class.
        """
        self._map_id = map_id
        self._verbose = verbose
        self._logger = self.configure_logging(name = name) 
        
    @property
    def map_id(self) -> str:
        """Gets the map identifier.
        """
        return self._map_id

    @property
    def logger(self) -> logging:
        """Gets the logging object.
        """
        return self._logger

    @property
    def verbose(self) -> bool:
        """Gets the verbose option.
        """
        return self._verbose

    def configure_logging(self, name, config = True):
        if self.map_id != None and config == True:
            extra = {'map_id':self.map_id}
            FORMAT = ('[Map/identifier: %(map_id)s] %(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
            '[trace_id=%(dd.trace_id)s span_id=%(dd.span_id)s] '
            '- %(message)s')
            logger = logging.getLogger(name)
            if self.verbose == True:
                logger.setLevel(logging.DEBUG)
                logging.basicConfig(format=FORMAT) 
            else:
                logger.setLevel(logging.ERROR)
                logging.basicConfig(format=FORMAT, level = logging.ERROR)
            logger = logging.LoggerAdapter(logger, extra)
            return logger
        
    def logging_box_un(self, logger, box, name, mode):
        if mode == 'info':
            logger.info(f"Class {name} - input box: [[(1) name, (2) box type, (3) [slots diameter, number of slots], (4) [height, width, length] ]] = [[ (1) {box.box}, (2) {box.box_type}, (3) [{box.box_slot_diameter}, {box.box_slots}], (4) [{box.height}, {box.width}, {box.length}] ]] ")
        else:
            logger.debug(f"Class {name} - input box: [[(1) name, (2) box type, (3) [slots diameter, number of slots], (4) [height, width, length] ]] = [[ (1) {box.box}, (2) {box.box_type}, (3) [{box.box_slot_diameter}, {box.box_slots}], (4) [{box.height}, {box.width}, {box.length}] ]] ")

    def logging_sku_un(self, logger, sku, name, mode):
        if mode == 'info':
            logger.info(f"Class {name} input sku: [[ (1) promax code, (2) is it bottle?, (3) units in boxes, (4) [height, width, length], (5) [gross weight], (6) [subcategory] ]] = [[ (1) {sku.promax_code}, (2) {sku.is_bottle}, (3) {sku.units_in_boxes}, (4) [{sku.height}, {sku.width}, {sku.length}], (5) [{sku.gross_weight}], (6) [{sku.subcategory}] ]]")
        else:
            logger.debug(f"Class {name} input sku: [[ (1) promax code, (2) is it bottle?, (3) units in boxes, (4) [height, width, length], (5) [gross weight], (6) [subcategory] ]] = [[ (1) {sku.promax_code}, (2) {sku.is_bottle}, (3) {sku.units_in_boxes}, (4) [{sku.height}, {sku.width}, {sku.length}] , (5) [{sku.gross_weight}], (6) [{sku.subcategory}] ]]")

    def logging_skus(self, logger, input, name, mode, input_option = True):
        if input_option:
            for sku in input.skus.keys():
                self.logging_sku_un(logger, input.skus[sku], name, mode)

    def logging_boxes(self, logger, input, name, mode, input_option = True):
        if input_option:
            for box in input.boxes.keys():
                self.logging_box_un(logger, input.boxes[box], name, mode)
        else:
            for box in input.keys():
                self.logging_box_un(logger, input[box], name, mode)
        
    def logging_input(self, input, logger, name, print_full_info = False, mode = 'debug'):
        if mode == 'info':
            logger.info(f"Initializing {name} class. Input object name: {input.name}. Input orders: {input.orders.orders_by_invoice}")
            if print_full_info:
                self.logging_skus(logger, input, name, 'info')
            self.logging_boxes(logger, input, name, 'info')
            logger.info(f"Class {name} input object number_of_boxes: {input.number_of_boxes}")
        else:
            logger.debug(f"Initializing {name} class. Input object name: {input.name}. Input orders: {input.orders.orders_by_invoice}")
            if print_full_info:
                self.logging_skus(logger, input, name, 'debug')
            self.logging_boxes(logger, input, name, 'debug')
            logger.debug(f"Class {name} input object number_of_boxes: {input.number_of_boxes}")

        
