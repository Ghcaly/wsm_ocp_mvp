import json
import unittest

from boxing.orders import Orders

class TOrders(unittest.TestCase):
    
    def refactor_dict(self, dict1):
        return {k:int(dict1[k]) for k in dict1.keys()}

    def t_orders_result(self, map_number, orders_to_test, filename_test):
        with open(filename_test) as json_file:
            data = json.load(json_file)
        test_orders = {mapa:{nf:self.refactor_dict(data[mapa][nf]) for nf in data[mapa].keys()} for mapa in data.keys()}
        orders = {map_number: orders_to_test}
        message = "First value and second value are not equal !"
        self.assertEqual(test_orders, orders, message)


