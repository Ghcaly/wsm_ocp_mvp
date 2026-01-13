from typing import List, Dict
import json
import unittest

from boxing.boxes import Boxes

class TBoxes(unittest.TestCase):

    def t_equal(self, val1, val2, message):
        return self.assertEqual(val1, val2, message)

    def t_boxes_result(self, box_obj, box_key, filename_test):
        with open(filename_test) as json_file:
            data = json.load(json_file)
        test_box = data[box_key]
        message = "First value and second value are not equal !"
        self.t_equal(str(box_key), box_obj.box, message)
        self.t_equal(str(test_box['box_type']), box_obj.box_type, message)
        self.t_equal(float(test_box['height']), box_obj.height, message)
        self.t_equal(float(test_box['width']), box_obj.width, message)
        self.t_equal(float(test_box['length']), box_obj.length, message)
        self.t_equal(int(test_box['box_slots']), box_obj.box_slots, message)
        self.t_equal(float(test_box['box_slot_diameter']), box_obj.box_slot_diameter, message)
        



