import json
import unittest
import copy

from boxing.configuration import Configuration
from boxing.utils import Utils

class TUnitBoxing(unittest.TestCase):
    def replace_str_to_int(self, data):
        new_caixas = {}
        new_data = copy.deepcopy(data)
        for c in data['caixas'].keys():
            new_caixas[int(c)] = copy.deepcopy(data['caixas'][c])
        new_data['caixas'] = new_caixas
        return new_data

    def t_unit_boxing(self, boxing_result, test_filepath, flag_families = 1):
        with open(test_filepath) as json_file:
            data = json.load(json_file)
        test_output = data
        if flag_families == 0:
            test_output = self.replace_str_to_int(test_output)
        message = "First value and second value are not equal !"
        print('test output: ', test_output)
        print('boxing_result: ', boxing_result)
        self.assertEqual(test_output, boxing_result, message)
