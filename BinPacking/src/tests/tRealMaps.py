
import unittest

class TRealMaps(unittest.TestCase):
    
    def call_test(self, val1, val2):
        message = "First value and second value are not equal !"
        self.assertEqual(val1, val2, message)
    
    def t_maps(self, test_res, algo_res):
        for m in algo_res.keys():
            self.call_test(algo_res[m], test_res[m])

        
        




