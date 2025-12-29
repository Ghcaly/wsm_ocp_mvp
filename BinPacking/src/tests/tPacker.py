import json
import unittest

from boxing.outputToInput import OutputToInput
from boxing.output import Output
from boxing.step import Step
from boxing.input import Input
from boxing.caixaStep import CaixaStep
from boxing.pacoteStep import PacoteStep
from boxing.garrafeiraStep import GarrafeiraStep

class TPacker(unittest.TestCase):
    
    def refactor_dict(self, dict1):
        return {str(k):dict1[k] for k in dict1.keys()}

    def t_packer_output(self, output, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        test_output = data
        message = "First value and second value are not equal !"
        self.assertEqual(test_output, output, message)

