from typing import List, Dict
import logging

from boxing.logger import BoxingLogger
class Items:

    """
    Gets items' part from the original input and keeps the information
    in order to insert it into the algorithm
    Args:
        input_data: Dict (sku information)
        promax_code: sku promax code
        boxes: available boxes for the algorithm
    """ 


    def __init__(
        self, 
        input_data: Dict,
        promax_code: str,
        map_id: str,
        verbose: bool
    ) -> None:

        self._verbose = verbose
        self._box_log_utils = BoxingLogger(map_id = map_id, name =  promax_code+'_item_log', verbose = self.verbose)
        self._logger = self.box_log_utils.logger
        self._promax_code = str(promax_code)
        self._height = float(self.get_dimension(input_data, 'height'))
        self._width = float(self.get_dimension(input_data, 'width'))
        self._length = float(self.get_dimension(input_data, 'length'))
        self._units_in_boxes = int(self.get_pacote_fechado(input_data))
        self._is_bottle = bool(self.get_if_is_bottle(input_data))
        self._gross_weight = float(self.get_gross_weight(input_data))
        self._subcategory = str(input_data['subcategory'])

    @property
    def verbose(self) -> bool:
        return self._verbose

    @property
    def gross_weight(self) -> float:
        return self._gross_weight

    @property
    def promax_code(self) -> str:
        return self._promax_code

    @property
    def height(self) -> float:
        return self._height 

    @property
    def length(self) -> float:
        return self._length 

    @property
    def width(self) -> float:
        return self._width  

    @property
    def units_in_boxes(self) -> int:
        return self._units_in_boxes 

    @property
    def is_bottle(self) -> bool:
        return self._is_bottle

    @property
    def box_log_utils(self) -> BoxingLogger:
        return self._box_log_utils

    @property
    def logger(self) -> logging:
        return self._logger

    @property
    def subcategory(self) -> int:
        return self._subcategory

    def test_dimensions(self, dim, class_source):
        val = getattr(self,dim) 
        if val > 0:
            return True 
        else:
            self.logger.warning(f'Item {self.promax_code} has input dimension field {dim.upper()} = {val} and this is an inadequate value. Ignoring item in further calculations. Souce: {class_source}')
            return False

    def test_all_dimensions(self, class_source):
        dim = ['height', 'length', 'width']
        res = [self.test_dimensions(d, class_source) for d in dim]
        ct = res.count(False)
        if False in res:
            return [False, ct] 
        else:
            return [True, ct]

    def get_if_is_bottle(self, input_data):
        if 'tipo_garrafa' in input_data and type(input_data['tipo_garrafa']) != int:
            self.logger.warning(f'Item {self.promax_code} has input field TIPO_GARRAFA different than int. Setting field to 0 (as type not bottle)')
            return 0
        elif 'tipo_garrafa' in input_data and input_data['tipo_garrafa'] in [0,1]:
            return input_data['tipo_garrafa']
        elif 'tipo_garrafa' in input_data and int(input_data['tipo_garrafa']) not in [0,1]:
            tg = input_data['tipo_garrafa']
            self.logger.warning(f'Item {self.promax_code} has input field TIPO_GARRAFA equal to {tg}. Setting field to 0 (as type not bottle)')
            return 0
        elif 'tipo_garrafa' not in input_data:
            self.logger.warning(f'Item {self.promax_code} has NO input field TIPO_GARRAFA. Setting field to 0 (as type not bottle)')
            return 0
        else:
            self.logger.warning(f'Item {self.promax_code} has UNKNOWN mistake input field TIPO_GARRAFA. Setting field to 0 (as type not bottle)')
            return 0

    def get_dimension(self, input_data, dim, repl_val = -1):
        if type(input_data[dim]) not in [float, int] or (type(input_data[dim]) == str and input_data[dim].isnumeric() == False):
            self.logger.warning(f'Item {self.promax_code} has input field {dim.upper()} different than numeric. Setting field to {repl_val}')
            return repl_val
        elif float(input_data[dim]) > 0:
            return input_data[dim]
        elif float(input_data[dim]) <= 0:
            tg = input_data[dim]
            self.logger.warning(f'Item {self.promax_code} has input field {dim.upper()} equal to {tg}. Setting field to {repl_val} ')
            return repl_val
        elif dim not in input_data:
            self.logger.warning(f'Item {self.promax_code} has NO input field {dim.upper()}. Setting field to {repl_val} ')
            return repl_val
        else:
            self.logger.warning(f'Item {self.promax_code} has UNKNOWN mistake input field {dim.upper()}. Setting field to {repl_val}')
            return repl_val
    
    def get_gross_weight(self, input_data, repl_val = -1):
        if type(input_data["gross_weight"]) not in [float, int] or (type(input_data["gross_weight"]) == str and input_data["gross_weight"].isnumeric() == False):
            self.logger.warning(f'Item {self.promax_code} has input field {"gross_weight".upper()} different than numeric. Setting field to {repl_val}')
            return repl_val
        elif float(input_data["gross_weight"]) > 0:
            return input_data["gross_weight"]
        elif float(input_data["gross_weight"]) <= 0:
            tg = input_data["gross_weight"]
            self.logger.warning(f'Item {self.promax_code} has input field {"gross_weight".upper()} equal to {tg}. Setting field to {repl_val} ')
            return repl_val
        elif "gross_weight" not in input_data:
            self.logger.warning(f'Item {self.promax_code} has NO input field {"gross_weight".upper()}. Setting field to {repl_val} ')
            return repl_val
        else:
            self.logger.warning(f'Item {self.promax_code} has UNKNOWN mistake input field {"gross_weight".upper()}. Setting field to {repl_val}')
            return repl_val

    def get_pacote_fechado(self, input_data):
        if type(input_data['units_in_boxes']) != int:
            self.logger.warning(f'Item {self.promax_code} has input field UNITS_IN_BOXES different than int. Setting field to 1 (will not be processed in closed packages step.)')
            return 1
        elif int(input_data['units_in_boxes']) >= 1:
            return input_data['units_in_boxes']
        elif int(input_data['units_in_boxes']) < 1:
            tg = input_data['units_in_boxes']
            self.logger.warning(f'Item {self.promax_code} has input field UNITS_IN_BOXES equal to {tg}. Setting field to 1 (will not be processed in closed packages step.)')
            return 1
        elif 'units_in_boxes' not in input_data:
            self.logger.warning(f'Item {self.promax_code} has NO input field UNITS_IN_BOXES. Setting field to 0 (as type not bottle)')
            return 1
        else:
            self.logger.warning(f'Item {self.promax_code} has UNKNOWN mistake input field TIPO_GARRAFA. Setting field to 1 (will not be processed in closed packages step.)')
            return 1

    def check_skus_fields_caixa(self, item):
        problems = {}
        if item.units_in_boxes < 1:
            problems['units_in_boxes'] = str(item.units_in_boxes)
        if item.length < 0:
            problems['length'] = str(item.length)
        if item.width < 0:
            problems['width'] = str(item.width)
        if item.height < 0:
            problems['height'] = str(item.height)
        if type(item.tipo_garrafa) != bool:
            problems['tipo_garrafa'] = str(item.tipo_garrafa)
        return problems 

    def fit_dimension(self, dim_sku, dim_box):
        if dim_sku <= dim_box:
            return True
        else:           
            return False

    def fit_both_dimensions(self, dims_sku, dims_box, box):
        result = True
        for i in range(2):
            if self.fit_dimension(getattr(self,dims_sku[i]), getattr(box,dims_box[i])) == False:
                result = False 
        return result

    def truth_test_fits_and(self, fit1, fit2):
        if (fit1 == True and fit2 == True):
            return True 
        else:
            return False

    def truth_test_fits_or(self, fit1, fit2):
        if (fit1 == True or fit2 == True):
            return True 
        else:
            return False

    def fit_in_box_caixa_check_dimensions(self, box):
        possible_dimension_combinations = [[['length', 'width'], ['width', 'length']], [['length', 'height'], ['height', 'length']], [['width', 'height'], ['height', 'width']]]
        possible_first_dimension = ['height', 'width', 'length']
        box_dimensions_to_compare = ['width', 'length']
        fits = []
        for i in range(len(possible_first_dimension)):
            fit_height = False
            final_fit = False
            dim_sku = possible_first_dimension[i]
            combination1 = possible_dimension_combinations[i][0]
            combination2 = possible_dimension_combinations[i][1]
            fit_dim_box = self.fit_dimension(getattr(self,dim_sku), getattr(box, 'height'))
            if fit_dim_box == True:
                fit_height = True
            f1 = self.fit_both_dimensions(combination1, box_dimensions_to_compare, box)
            f2 = self.fit_both_dimensions(combination2, box_dimensions_to_compare, box)
            final_fit1 = self.truth_test_fits_and(f1, fit_height)
            final_fit2 = self.truth_test_fits_and(f2, fit_height)
            final_fit = self.truth_test_fits_or(final_fit1, final_fit2)
            fits.append(final_fit)
        if True in fits:
            return True
        else:
            return False

    def fit_in_box_caixa(self, box):
        if self.is_bottle == 1 or (self.is_bottle == 0 and box.box_type != 'garrafeira'):
            fits = self.fit_in_box_caixa_check_dimensions(box)
            if self.length*self.height*self.width <= box.length*box.height*box.width and fits == True:
                return True 
            else:
                self.logger.warning(f'Item {self.promax_code} does not fit in box {box.box} and will not be processed at the moment. Item dimensions (height, width, length): ({self.height}, {self.width}, {self.length}). Box dimensions (height, width, length): ({box.height}, {box.width}, {box.length})')
                return False
        elif self.is_bottle == 0 and box.box_type == 'garrafeira':
            return False
        
    def fit_in_box(self, box) -> List:
        if box.box_type == 'caixa':
            return [self.fit_in_box_caixa(box), 0]    
        elif box.box_type == 'garrafeira' and self.is_bottle and self.length <= box.box_slot_diameter and self.width <= box.box_slot_diameter:
            return [True, 1]
        else:
            self.logger.warning(f'Item {self.promax_code} of type bottle = {self.is_bottle} does not fit in box {box.box} of type {box.box_type}')
            return [False, 1]



