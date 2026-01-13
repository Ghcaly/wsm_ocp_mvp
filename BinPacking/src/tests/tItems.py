import json
import unittest

from boxing.items import Items

class TItems(unittest.TestCase):
    
    def t_equal(self, val1, val2, message):
        return self.assertEqual(val1, val2, message)

    def t_items_in_boxes(self, item_test, item_obj, boxes, message):
        for i in range(len(boxes)):
            box_result = item_obj.fit_in_box(boxes[i])[0]
            self.t_equal(bool(item_test['fit_box_'+str(i+1)]), box_result, message)

    def t_items_result(self, item_obj, item_key, filename_test, boxes):
        with open(filename_test) as json_file:
            data = json.load(json_file)
        t_item = data[item_key]
        message = "First value and second value are not equal !"
        self.t_equal(str(item_key), item_obj.promax_code, message)
        self.t_equal(float(t_item['height']), item_obj.height, message)
        self.t_equal(float(t_item['width']), item_obj.width, message)
        self.t_equal(float(t_item['length']), item_obj.length, message)
        self.t_equal(int(t_item['units_in_boxes']), item_obj.units_in_boxes, message)
        self.t_equal(bool(int(t_item['tipo_garrafa'])), item_obj.is_bottle, message)
        self.t_items_in_boxes(t_item, item_obj, boxes, message)
        



