from py3dbp import Packer, Bin, Item

from boxing.step import Step
from boxing.input import Input
from boxing.output import Output
from boxing.outputToInput import OutputToInput
from boxing.caixaStep import CaixaStep
from boxing.pacoteStep import PacoteStep
from boxing.garrafeiraStep import GarrafeiraStep
from boxing.utils import Utils

from typing import List, Dict, Tuple, Set, Optional
import numpy as np
import pandas as pd
import copy
import pathlib
import os


class Configuration:


    def __init__(
        self,
        filepath: str,
        res_dir = '/results',
        params_dir = '/params'
    ) -> None:

        """
        Represents the class that reads and writes parameters for the algorithm.
        """  
        self._utils = Utils()
        self._filepath = filepath
        self._parameters_file = '/parameters.json'
        self._params_dir = params_dir
        self._res_dir = res_dir
        self._parameters = self.read_file_parameters()
        self._box_filename = '/'+ self.get_box_filename()
        self._boxes_dict = self.read_box_file()
        self._steps = self.get_steps()
        self._max_weight = self.get_max_weight()


    @property
    def max_weight(self) -> float:
        """Returns max weight for the boxes
        """
        return self._max_weight

    @property
    def filepath(self) -> str:
        """Returns current directory's path
        """
        return self._filepath

    @property
    def utils(self) -> Utils:
        """Returns configurations' Utils object
        """
        return self._utils

    @property
    def parameters(self) -> Dict:
        """Returns parameters
        """
        return self._parameters

    @property
    def parameters_file(self) -> str:
        """Returns parameters filename
        """
        return self._parameters_file

    @property
    def box_filename(self) -> str:
        """Returns box filename
        """
        return self._box_filename

    @property
    def boxes_dict(self) -> str:
        """Returns boxes information
        """
        return self._boxes_dict

    @property
    def steps(self) -> str:
        """Returns algorithm steps
        """
        return self._steps
    @property
    def res_dir(self) -> str:
        """Returns results folder
        """
        return self._res_dir
    @property
    def params_dir(self) -> str:
        """Returns parameters folder
        """
        return self._params_dir

    @property
    def max_weight(self) -> float:
        """Returns max weight for the boxes
        """
        return self._max_weight

    def read_file_parameters(self) -> Dict:
        if os.path.exists(self.filepath + self.params_dir+ self.parameters_file):
            return self.utils.open_json(self.filepath + self.params_dir + self.parameters_file) 
            
        else:
            if os.path.exists(self.filepath + self.params_dir) == False:
                os.mkdir(self.filepath + self.params_dir)
            default_params = {"boxes_file": "boxes_input.json",
                              "steps": {
                                  "1": "Pacote",
                                  "2": "Garrafeira",
                                  "3": "Caixa",
                              },
                              "res_dir": "results",
                              "max_weight": 25
                              }
            self.utils.write_json(self.filepath + self.params_dir + self.parameters_file, default_params)
            return self.utils.open_json(self.filepath + self.params_dir + self.parameters_file)

    def get_box_filename(self) -> str:
        return self.parameters['boxes_file']

    def get_steps(self) -> str:
        return self.parameters['steps']

    def get_max_weight(self) -> float:
        return self.parameters['max_weight']

    def read_box_file(self) -> Dict:
        if os.path.exists(self.filepath + self.params_dir + self.box_filename):
            return self.utils.open_json(self.filepath + self.params_dir +self.box_filename)
        else:
            default_boxes_params = {
                            "1": {
                                "box_type": "garrafeira",
                                "length": 0,
                                "width": 0,
                                "height": 0,
                                "box_slots": 9,
                                "box_slot_diameter": 10.392304
                            },
                            "2": {
                                "box_type": "caixa",
                                "length": 40,
                                "width": 58,
                                "height": 34,
                                "box_slots": 0,
                                "box_slot_diameter": 0
                            }
                        }
            self.utils.write_json(self.filepath + self.params_dir + self.box_filename, default_boxes_params)
        
        return self.utils.open_json(self.filepath + self.params_dir +self.box_filename)

    def write_parameters(self, json_content) -> None:
        return self.utils.write_json(self.filepath + self.parameters_file, json_content)

    def write_box_file(self, json_content) -> None:
        return self.utils.write_json(self.box_filename, json_content)

        

