import unittest

from boxing.configuration import Configuration
from boxing.utils import Utils

class TConfiguration(unittest.TestCase):
    
    def t_parameters(self, parameters_data, test_filepath, boxes_filetest):
        config = Configuration(filepath = test_filepath)
        config.write_parameters(json_content = parameters_data)
        config = Configuration(filepath = test_filepath)
        message = "First value and second value are not equal !"
        self.assertEqual(config.filepath, test_filepath, message)
        self.assertEqual(config.parameters, parameters_data, message)
        self.assertEqual(config.parameters_file, '/parameters.json', message)
        self.assertEqual(config.box_filename, '/' + parameters_data['boxes_file'], message)
        self.assertEqual(config.boxes_dict, boxes_filetest, message)
        self.assertEqual(config.steps, parameters_data['steps'], message)
        self.assertEqual(config.max_weight, parameters_data['max_weight'], message)
