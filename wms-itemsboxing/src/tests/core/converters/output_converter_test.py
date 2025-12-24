import unittest
import json
import os
from tests import data_path
from core.converters.output_converter import OutputConverter
from core.converters.errors import OutputConversionError


class OutputConverterTest(unittest.TestCase):

    def test_should_convert_output_to_model(self):
        # Arrange
        with open(os.path.join(data_path, 'lib_output01.json')) as fp:
            model = json.load(fp)

        with open(os.path.join(data_path, 'output01.json')) as fp:
            expected = json.load(fp)

        # Act
        result = OutputConverter().convert(model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_items_with_dict_data(self):
        # Arrange
        model = {
            "box1": {
                "12": {
                    "123": 1,
                    "456": 2,
                }
            },
            "box2": {
                "34": {
                    "789": 3,
                    "012": 4,
                }
            }
        }

        expected = {
            "test": [
                {
                    "code": 12,
                    "skus": [
                        {"code": 123, "quantity": 1},
                        {"code": 456, "quantity": 2}
                    ]
                },
                {
                    "code": 34,
                    "skus": [
                        {"code": 789, "quantity": 3},
                        {"code": 12, "quantity": 4}
                    ]
                }
            ]
        }

        # Act
        result = OutputConverter()._convert_items('test', model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_items_with_empty_dict(self):
        # Arrange
        model = {}

        expected = {"test": []}

        # Act
        result = OutputConverter()._convert_items('test', model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_items_with_empty_list(self):
        # Arrange
        model = []

        expected = {"test": []}

        # Act
        result = OutputConverter()._convert_items('test', model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_skus_with_empty_dict(self):
        # Arrange
        model = {}

        expected = []

        # Act
        result = OutputConverter()._convert_skus(model)

        # Assert
        self.assertListEqual(expected, result)

    def test_should_raise_error_when_model_is_invalid(self):
        # Arrange
        model = {}
        message = "Couldn't convert output model: KeyError: 'caixas'."

        # Act/Assert
        with self.assertRaises(OutputConversionError) as err:
            OutputConverter().convert(model)

        self.assertEqual(str(err.exception), message)

    def test_should_raise_error_when_model_is_not_a_dict(self):
        # Arrange
        model = dict
        message = "Couldn't convert output model: UnexpectedType: Object of type 'type' can't be converted. Expected type: 'dict'."

        # Act/Assert
        with self.assertRaises(OutputConversionError) as err:
            OutputConverter().convert(model)

        self.assertEqual(str(err.exception), message)

    def test_should_convert_skus(self):
        # Arrange
        model = {
            "777": 1,
            "999": 2,
        }

        expected = [
            {
                "code": 777,
                "quantity": 1
            },
            {
                "code": 999,
                "quantity": 2
            }
        ]

        # Act
        result = OutputConverter()._convert_skus(model)

        # Assert
        self.assertListEqual(expected, result)

    def test_should_convert_maps(self):
        # Arrange
        model = {
            "12": {
                "123": 1,
                "456": 2,
            }
        }

        expected = {
            "code": 12,
            "skus": [
                {
                    "code": 123,
                    "quantity": 1
                },
                {
                    "code": 456,
                    "quantity": 2
                }
            ]
        }

        # Act
        result = OutputConverter()._convert_item(model)

        # Assert
        self.assertDictEqual(expected, result)

    def test_should_convert_item_list(self):
        # Arrange
        model = [
            {
                "123": 1,
                "456": 2,
                "789": 2,
                "012": 7
            }
        ]

        expected = {'test': [
            {'code': 123, 'quantity': 1},
            {'code': 456, 'quantity': 2},
            {'code': 789, 'quantity': 2},
            {'code': 12, 'quantity': 7}
        ]}

        # Act
        result = OutputConverter()._convert_items('test', model)

        # Assert
        self.assertDictEqual(expected, result)
