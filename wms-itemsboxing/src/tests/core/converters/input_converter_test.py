import unittest
import json
import os
from tests import data_path
from core.converters.input_converter import InputConverter
from core.converters.errors import InputConversionError


class InputConverterTest(unittest.TestCase):

    def test_should_convert_model_to_input(self):
        # Arrange
        with open(os.path.join(data_path, 'input01.json')) as fp:
            model = json.load(fp)

        with open(os.path.join(data_path, 'lib_input01.json')) as fp:
            expected = json.load(fp)

        # Act
        result = InputConverter().convert(model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_skus_with_subcategory(self):
        # Arrange
        model = [{
            "code": 999,
            "length": 7.0,
            "height": 30.5,
            "width": 8.0,
            "units_in_boxes": 12,
            "is_bottle": False,
            "gross_weight": 10.5,
            "subcategory": "12345678-1234-1234-1234-123456789012"
        }]

        expected = {
            "test": {
                "999": {
                    "length": 7.0,
                    "height": 30.5,
                    "width": 8.0,
                    "units_in_boxes": 12,
                    "tipo_garrafa": 0,
                    "gross_weight": 10.5,
                    "subcategory": "12345678-1234-1234-1234-123456789012"
                }
            }
        }

        # Act
        result = InputConverter()._convert_skus('test', model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_skus_with_none_subcategory(self):
        # Arrange
        model = [{
            "code": 999,
            "length": 7.0,
            "height": 30.5,
            "width": 8.0,
            "units_in_boxes": 12,
            "is_bottle": False,
            "subcategory": None
        }]

        expected = {
            "test": {
                "999": {
                    "length": 7.0,
                    "height": 30.5,
                    "width": 8.0,
                    "units_in_boxes": 12,
                    "tipo_garrafa": 0,
                    "gross_weight": 0,
                    "subcategory": "00000000-0000-0000-0000-000000000000"
                }
            }
        }

        # Act
        result = InputConverter()._convert_skus('test', model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_family_groups_with_items(self):
        # Arrange
        model = [{
            "subcategory": "12345678-1234-1234-1234-123456789012",
            "cant_go_with": ["87654321-4321-4321-4321-210987654321"]
        }]

        expected = {
            "test": [{
                "subcategory": "12345678-1234-1234-1234-123456789012",
                "cant_go_with": ["87654321-4321-4321-4321-210987654321"]
            }]
        }

        # Act
        result = InputConverter()._convert_family_groups('test', model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_family_groups_with_none_items(self):
        # Arrange
        model = None

        expected = {
            "test": [{
                "subcategory": "00000000-0000-0000-0000-000000000000",
                "cant_go_with": []
            }]
        }

        # Act
        result = InputConverter()._convert_family_groups('test', model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_raise_error_when_model_is_invalid(self):
        # Arrange
        model = {}
        message = "Couldn't convert input model: KeyError: 'maps'."

        # Act/Assert
        with self.assertRaises(InputConversionError)as err:
            InputConverter().convert(model)

        self.assertEqual(str(err.exception), message)

    def test_should_raise_error_when_model_is_not_a_dict(self):
        # Arrange
        model = dict
        message = "Couldn't convert input model: UnexpectedType: Object of type 'type' can't be converted. Expected type: 'dict'."

        # Act/Assert
        with self.assertRaises(InputConversionError) as err:
            InputConverter().convert(model)

        self.assertEqual(str(err.exception), message)

    def test_should_convert_client(self):
        # Arrange
        model = {
            "code": 234,
            "skus": [
                {
                    "code": 1,
                    "quantity": 2
                },
                {
                    "code": 2,
                    "quantity": 4
                }
            ]
        }

        expected = {
            "234": {
                "1": 2,
                "2": 4
            }
        }

        # Act
        result = InputConverter()._convert_client_and_skus(model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_maps(self):
        # Arrange
        model = [{
            "code": 123,
            "clients": [
                {
                    "code": 456,
                    "skus": [
                        {
                            "code": 1,
                            "quantity": 2
                        },
                        {
                            "code": 2,
                            "quantity": 4
                        }
                    ]
                }
            ]
        }]

        expected = {
            "123": {
                "456": {
                    "1": 2,
                    "2": 4
                }
            }
        }

        # Act
        result = InputConverter()._convert_maps(model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_skus(self):
        # Arrange
        model = [{
            "code": 999,
            "length": 7.0,
            "height": 30.5,
            "width": 8.0,
            "units_in_boxes": 12,
            "is_bottle": True,
            "gross_weight": 15.99
        }]

        expected = {
            "test": {
                "999": {
                    "length": 7.0,
                    "height": 30.5,
                    "width": 8.0,
                    "units_in_boxes": 12,
                    "tipo_garrafa": 1,
                    "gross_weight": 15.99,
                    "subcategory": '00000000-0000-0000-0000-000000000000'
                }
            }
        }

        # Act
        result = InputConverter()._convert_skus('test', model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_boxes(self):
        # Arrange
        model = [{
            "code": 999,
            "length": 7.0,
            "height": 30.5,
            "width": 8.0,
            "box_slots": 12,
            "box_slot_diameter": 1.5
        }]

        expected = {
            "test": {
                "999": {
                    "length": 7.0,
                    "height": 30.5,
                    "width": 8.0,
                    "box_slots": 12,
                    "box_slot_diameter": 1.5
                }
            }
        }

        # Act
        result = InputConverter()._convert_boxes('test', model)

        # Assert
        self.assertDictEqual(expected, result)
