import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from core.services.binpacking import get_calculated_boxes


class BinpackingTest(unittest.TestCase):

    @patch('core.services.binpacking.OutputConverter')
    @patch('core.services.binpacking.UnitBoxing')
    @patch('core.services.binpacking.InputConverter')
    def test_get_calculated_boxes_success(self, mock_input_converter, mock_unit_boxing, mock_output_converter):
        # Arrange
        input_obj = {'test': 'data'}
        converted_input = {'converted': 'input'}
        algo_result = {'algo': 'result'}
        final_result = {'final': 'result'}
        
        mock_input_converter_instance = Mock()
        mock_input_converter.return_value = mock_input_converter_instance
        mock_input_converter_instance.convert.return_value = converted_input
        
        mock_unit_boxing_instance = Mock()
        mock_unit_boxing.return_value = mock_unit_boxing_instance
        mock_unit_boxing_instance.apply.return_value = algo_result
        
        mock_output_converter_instance = Mock()
        mock_output_converter.return_value = mock_output_converter_instance
        mock_output_converter_instance.convert.return_value = final_result
        
        # Act
        result = get_calculated_boxes(input_obj)
        
        # Assert
        mock_input_converter.assert_called_once()
        mock_input_converter_instance.convert.assert_called_once_with(input_obj)
        mock_unit_boxing.assert_called_once_with(json_input=converted_input, verbose=False)
        mock_unit_boxing_instance.apply.assert_called_once()
        mock_output_converter.assert_called_once()
        mock_output_converter_instance.convert.assert_called_once_with(algo_result)
        self.assertEqual(result, final_result)

    @patch('core.services.binpacking.OutputConverter')
    @patch('core.services.binpacking.UnitBoxing')
    @patch('core.services.binpacking.InputConverter')
    def test_get_calculated_boxes_with_complex_input(self, mock_input_converter, mock_unit_boxing, mock_output_converter):
        # Arrange
        complex_input = {
            'maps': [{'code': 1, 'clients': []}],
            'skus': [{'code': 1, 'length': 10}],
            'boxes': [{'code': 1, 'length': 20}]
        }
        converted_input = {'processed': 'complex_input'}
        algo_result = {'complex': 'result'}
        final_result = {'processed': 'complex_result'}
        
        mock_input_converter_instance = Mock()
        mock_input_converter.return_value = mock_input_converter_instance
        mock_input_converter_instance.convert.return_value = converted_input
        
        mock_unit_boxing_instance = Mock()
        mock_unit_boxing.return_value = mock_unit_boxing_instance
        mock_unit_boxing_instance.apply.return_value = algo_result
        
        mock_output_converter_instance = Mock()
        mock_output_converter.return_value = mock_output_converter_instance
        mock_output_converter_instance.convert.return_value = final_result
        
        # Act
        result = get_calculated_boxes(complex_input)
        
        # Assert
        self.assertEqual(result, final_result)
        mock_input_converter_instance.convert.assert_called_once_with(complex_input)

    @patch('core.services.binpacking.OutputConverter')
    @patch('core.services.binpacking.UnitBoxing')
    @patch('core.services.binpacking.InputConverter')
    def test_get_calculated_boxes_input_converter_exception(self, mock_input_converter, mock_unit_boxing, mock_output_converter):
        # Arrange
        input_obj = {'invalid': 'data'}
        
        mock_input_converter_instance = Mock()
        mock_input_converter.return_value = mock_input_converter_instance
        mock_input_converter_instance.convert.side_effect = ValueError("Invalid input")
        
        # Act & Assert
        with self.assertRaises(ValueError):
            get_calculated_boxes(input_obj)
        
        mock_input_converter_instance.convert.assert_called_once_with(input_obj)
        mock_unit_boxing.assert_not_called()
        mock_output_converter.assert_not_called()

    @patch('core.services.binpacking.OutputConverter')
    @patch('core.services.binpacking.UnitBoxing')
    @patch('core.services.binpacking.InputConverter')
    def test_get_calculated_boxes_unit_boxing_exception(self, mock_input_converter, mock_unit_boxing, mock_output_converter):
        # Arrange
        input_obj = {'test': 'data'}
        converted_input = {'converted': 'input'}
        
        mock_input_converter_instance = Mock()
        mock_input_converter.return_value = mock_input_converter_instance
        mock_input_converter_instance.convert.return_value = converted_input
        
        mock_unit_boxing_instance = Mock()
        mock_unit_boxing.return_value = mock_unit_boxing_instance
        mock_unit_boxing_instance.apply.side_effect = RuntimeError("Boxing algorithm failed")
        
        # Act & Assert
        with self.assertRaises(RuntimeError):
            get_calculated_boxes(input_obj)
        
        mock_input_converter_instance.convert.assert_called_once_with(input_obj)
        mock_unit_boxing.assert_called_once_with(json_input=converted_input, verbose=False)
        mock_unit_boxing_instance.apply.assert_called_once()
        mock_output_converter.assert_not_called()

    @patch('core.services.binpacking.OutputConverter')
    @patch('core.services.binpacking.UnitBoxing')
    @patch('core.services.binpacking.InputConverter')
    def test_get_calculated_boxes_output_converter_exception(self, mock_input_converter, mock_unit_boxing, mock_output_converter):
        # Arrange
        input_obj = {'test': 'data'}
        converted_input = {'converted': 'input'}
        algo_result = {'algo': 'result'}
        
        mock_input_converter_instance = Mock()
        mock_input_converter.return_value = mock_input_converter_instance
        mock_input_converter_instance.convert.return_value = converted_input
        
        mock_unit_boxing_instance = Mock()
        mock_unit_boxing.return_value = mock_unit_boxing_instance
        mock_unit_boxing_instance.apply.return_value = algo_result
        
        mock_output_converter_instance = Mock()
        mock_output_converter.return_value = mock_output_converter_instance
        mock_output_converter_instance.convert.side_effect = KeyError("Missing key in result")
        
        # Act & Assert
        with self.assertRaises(KeyError):
            get_calculated_boxes(input_obj)
        
        mock_input_converter_instance.convert.assert_called_once_with(input_obj)
        mock_unit_boxing_instance.apply.assert_called_once()
        mock_output_converter_instance.convert.assert_called_once_with(algo_result)

    @patch('core.services.binpacking.OutputConverter')
    @patch('core.services.binpacking.UnitBoxing')
    @patch('core.services.binpacking.InputConverter')
    def test_get_calculated_boxes_verbose_false(self, mock_input_converter, mock_unit_boxing, mock_output_converter):
        # Arrange
        input_obj = {'test': 'data'}
        converted_input = {'converted': 'input'}
        
        mock_input_converter_instance = Mock()
        mock_input_converter.return_value = mock_input_converter_instance
        mock_input_converter_instance.convert.return_value = converted_input
        
        mock_unit_boxing_instance = Mock()
        mock_unit_boxing.return_value = mock_unit_boxing_instance
        
        # Act
        get_calculated_boxes(input_obj)
        
        # Assert - Verify that UnitBoxing is called with verbose=False
        mock_unit_boxing.assert_called_once_with(json_input=converted_input, verbose=False)

    @patch('core.services.binpacking.OutputConverter')
    @patch('core.services.binpacking.UnitBoxing')
    @patch('core.services.binpacking.InputConverter')
    def test_get_calculated_boxes_empty_input(self, mock_input_converter, mock_unit_boxing, mock_output_converter):
        # Arrange
        empty_input = {}
        converted_input = {'empty': 'converted'}
        algo_result = {'empty': 'result'}
        final_result = {'empty': 'final'}
        
        mock_input_converter_instance = Mock()
        mock_input_converter.return_value = mock_input_converter_instance
        mock_input_converter_instance.convert.return_value = converted_input
        
        mock_unit_boxing_instance = Mock()
        mock_unit_boxing.return_value = mock_unit_boxing_instance
        mock_unit_boxing_instance.apply.return_value = algo_result
        
        mock_output_converter_instance = Mock()
        mock_output_converter.return_value = mock_output_converter_instance
        mock_output_converter_instance.convert.return_value = final_result
        
        # Act
        result = get_calculated_boxes(empty_input)
        
        # Assert
        self.assertEqual(result, final_result)
        mock_input_converter_instance.convert.assert_called_once_with(empty_input)


if __name__ == '__main__':
    unittest.main()
