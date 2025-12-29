
import json
import unittest

from boxing.outputToInput import OutputToInput
from boxing.output import Output
from boxing.step import Step
from boxing.input import Input
from boxing.caixaStep import CaixaStep
from boxing.pacoteStep import PacoteStep
from boxing.garrafeiraStep import GarrafeiraStep

class TFakeInput(unittest.TestCase):

    """Represents a mock class to test optimizer.
    """

    def t_equal(self, val1, val2, message):
        return self.assertEqual(val1, val2, message)

    def t_input_orders(self, input, filename, input_step):
        with open(filename) as json_file:
            data = json.load(json_file)
        test_input_orders = {str(k):{str(k2):int(data[input_step][k][k2]) for k2 in data[input_step][k].keys()} for k in data[input_step].keys()}
        input_orders = input.orders.orders_by_invoice
        message = "First value and second value are not equal !"
        for od in input_orders.keys():
            self.t_equal(input_orders[od], test_input_orders[od], message)


