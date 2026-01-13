import json
import unittest

from boxing.outputToInput import OutputToInput
from boxing.output import Output
from boxing.step import Step
from boxing.input import Input
from boxing.caixaStep import CaixaStep
from boxing.pacoteStep import PacoteStep
from boxing.garrafeiraStep import GarrafeiraStep

class TFakeOutput(unittest.TestCase):
    
    def refactor_dict(self, dict1):
        return {str(k):dict1[k] for k in dict1.keys()}

    def t_output(self, output, filename, step, output_part):
        with open(filename) as json_file:
            data = json.load(json_file)
        test_output_orders = {str(k):self.refactor_dict(data[step][output_part][k]) for k in data[step][output_part].keys()}
        output_orders = output.new_orders.orders_by_invoice 
        message = "First value and second value are not equal !"
        self.assertEqual(test_output_orders, output_orders, message)

import unittest
