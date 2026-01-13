from py3dbp import Packer, Bin, Item

from boxing.step import Step
from boxing.input import Input
from boxing.output import Output
from boxing.outputToInput import OutputToInput
from boxing.caixaStep import CaixaStep
from boxing.pacoteStep import PacoteStep
from boxing.garrafeiraStep import GarrafeiraStep
from boxing.configuration import Configuration
import logging
from typing import List, Dict, Tuple, Set, Optional
import numpy as np
import pandas as pd
import copy
from boxing.utils import Utils
from boxing.logger import BoxingLogger
import traceback

class BoxerPacker:

    """Represents the class that uses the heuristics from the py3dbp library and executes
    the packing process for boxes with potentially more than one type of SKU.
    """

    def __init__(
        self, 
        general_input: Input,
        config: Configuration,
        verbose: bool,
        map_id: str
    ) -> None:

        """
        Args:
            input: input object
            config: configuration object
            verbose: logger class parameter
        """   

        self._verbose = verbose
        self._map_id = map_id
        self._boxes = general_input.boxes
        self._number_of_boxes = general_input.number_of_boxes
        self._skus_info = general_input.skus
        self._orders = general_input.orders
        self._steps = config.steps
        self._pacote_step = PacoteStep(verbose = verbose, map_id = map_id)
        self._garrafeira_step = GarrafeiraStep(verbose = verbose, map_id = map_id)
        self._caixa_step = CaixaStep(verbose = verbose, map_id = map_id)
        self._general_input = general_input
        self._box_log_utils = BoxingLogger(name =  'input_log', map_id = map_id, verbose = self.verbose)
        self._logger = self._box_log_utils.logger
        
    
    @property
    def verbose(self) -> bool:
        """Returns verbose
        """
        return self._verbose

    @property
    def map(self) -> str:
        """Gets the map identifier.
        """
        return self._map
        
    @property
    def boxes(self) -> Dict:
        """Returns boxes information
        """
        return self._boxes

    @property
    def steps(self) -> Dict:
        """Returns steps information
        """
        return self._steps
    
    @property
    def number_of_boxes(self) -> int:
        """Number of available boxes for each type of box
        """
        return self._number_of_boxes
   
    @property
    def skus_info(self) -> Dict:
        """Returns information about SKUs
        """
        return self._skus_info

    @property
    def orders(self) -> Dict:
        """Returns information about orders
        """
        return self._orders

    @property
    def pacote_step(self) -> PacoteStep:
        """Returns PacoteStep object
        """
        return self._pacote_step

    @property
    def garrafeira_step(self) -> GarrafeiraStep:
        """Returns GarrafeiraStep object
        """
        return self._garrafeira_step

    @property
    def caixa_step(self) -> CaixaStep:
        """Returns CaixaStep object
        """
        return self._caixa_step

    @property
    def general_input(self) -> Dict:
        """Returns general input information
        """
        return self._general_input
    
    @property
    def logger(self) -> logging:
        """Gets the logger manager object with modifications made by
           the configure_logging function.
        """
        return self._logger

    def sub_format_result(self,
                          steps_names: str,
                          sok: str,
                          steps_outputs: Dict,
                          steps_boxes: str,
                          final_result: Dict,
                          caixas: Dict,
                          box_number: int) -> Tuple:
        
        current_step_result = steps_outputs[sok][steps_names].step_result
        if steps_names == 'Pacote':
            final_result[steps_names.lower() + 's'] = current_step_result

        else:
            current_step_box_dict = steps_boxes[steps_names]
            current_step_box_key = list(current_step_box_dict.keys())[0]
            current_step_box = current_step_box_dict[current_step_box_key].box
            for k in current_step_result.keys():
                box_number = box_number + 1
                caixas[str(box_number)] = {current_step_box:current_step_result[k]}
        return final_result, caixas, box_number

    def format_result(self, 
                      steps_outputs: Dict,
                      steps_boxes: Dict
    ) -> Dict:
        final_result = {}
        steps_outputs_copy = copy.deepcopy(steps_outputs)
        final_result = {}
        caixas = {}
        box_number = 0
        for sok in steps_outputs.keys():
            steps_outputs_copy.pop(sok)
            steps_names = list(steps_outputs[sok].keys())[0]
            final_result, caixas, box_number = self.sub_format_result(steps_names,
                                                                      sok,
                                                                      steps_outputs,
                                                                      steps_boxes,
                                                                      final_result,
                                                                      caixas,
                                                                      box_number)

        final_result['caixas'] = caixas        
        return final_result

    def apply(
        self
    ) -> Tuple:
        self.logger.debug("Entered BoxerPacker...")

        utils = Utils()
        steps_copy = {int(k): self.steps[k] for k in self.steps.keys()}
        st_input = self.general_input

        steps_obj = {self._garrafeira_step.name: self._garrafeira_step,
                        self._caixa_step.name: self._caixa_step,
                        self._pacote_step.name: self._pacote_step}
        steps_outputs = {}
        steps_boxes = {}
        self.logger.debug("Looping over steps...")
        nao_paletizados = {}
        nao_paletizados_out = {}
        try:
            for _ in range(len(self.steps.keys())):
                step_key = min(list(steps_copy.keys()))
                step_name = steps_copy[step_key]
                current_step = steps_obj[step_name]

                current_output = current_step.apply(step_input = st_input)                
                steps_outputs[step_key] = {step_name:current_output}
                nao_paletizados_out[step_key] = current_output.skus_not_processed
                steps_copy.pop(step_key)
                nao_paletizados = utils.refactor_item_list(self.skus_info, nao_paletizados, nao_paletizados_out[step_key])
                if steps_copy:
               
                    next_step_key = min(list(steps_copy.keys()))

                    next_step_name = steps_copy[next_step_key]
                    st_input = OutputToInput(name = next_step_name+'_input',
                                                output = current_output,
                                                original_input = self.general_input,
                                                step_name = next_step_name,
                                                number_of_boxes = self.number_of_boxes).apply()
                    steps_boxes[next_step_name] = st_input.boxes

            
            
            final_result = self.format_result(steps_outputs,
                                         steps_boxes)
            
            self.logger.debug(f"Final result = {final_result}.")
            return final_result, nao_paletizados
        except Exception as e:
            err_stck = ''.join(map(lambda x: str(x).replace('\n', ' -- '), traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            self.logger.error(f"Looping over steps: fatal error in execution. - message: {e}, stack trace: {err_stck}")
            raise

