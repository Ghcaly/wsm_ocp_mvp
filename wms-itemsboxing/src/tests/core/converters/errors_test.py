import unittest
from core.converters.errors import ConversionError, UnexpectedType, InputConversionError, OutputConversionError


class ConversionErrorTest(unittest.TestCase):

    def test_conversion_error_initialization(self):
        # Arrange
        message = "Test error message"

        # Act
        error = ConversionError(message)

        # Assert
        self.assertEqual(str(error), message)
        self.assertIsInstance(error, RuntimeError)

    def test_unexpected_type_with_object_only(self):
        # Arrange
        obj = 123

        # Act
        error = UnexpectedType(obj)

        # Assert
        expected_message = "Object of type 'int' can't be converted"
        self.assertEqual(str(error), expected_message)
        self.assertIsInstance(error, ConversionError)

    def test_unexpected_type_with_expected_type(self):
        # Arrange
        obj = 123
        expected_type = "str"

        # Act
        error = UnexpectedType(obj, expected_type)

        # Assert
        expected_message = "Object of type 'int' can't be converted. Expected type: 'str'"
        self.assertEqual(str(error), expected_message)
        self.assertIsInstance(error, ConversionError)

    def test_unexpected_type_with_none_expected_type(self):
        # Arrange
        obj = []
        expected_type = None

        # Act
        error = UnexpectedType(obj, expected_type)

        # Assert
        expected_message = "Object of type 'list' can't be converted"
        self.assertEqual(str(error), expected_message)

    def test_input_conversion_error_with_key_error(self):
        # Arrange
        parent_error = KeyError("missing_key")

        # Act
        error = InputConversionError(parent_error)

        # Assert
        expected_message = "Couldn't convert input model: KeyError: 'missing_key'."
        self.assertEqual(str(error), expected_message)
        self.assertIsInstance(error, ConversionError)

    def test_input_conversion_error_with_value_error(self):
        # Arrange
        parent_error = ValueError("invalid value")

        # Act
        error = InputConversionError(parent_error)

        # Assert
        expected_message = "Couldn't convert input model: ValueError: invalid value."
        self.assertEqual(str(error), expected_message)

    def test_output_conversion_error_with_key_error(self):
        # Arrange
        parent_error = KeyError("missing_key")

        # Act
        error = OutputConversionError(parent_error)

        # Assert
        expected_message = "Couldn't convert output model: KeyError: 'missing_key'."
        self.assertEqual(str(error), expected_message)
        self.assertIsInstance(error, ConversionError)

    def test_output_conversion_error_with_type_error(self):
        # Arrange
        parent_error = TypeError("wrong type")

        # Act
        error = OutputConversionError(parent_error)

        # Assert
        expected_message = "Couldn't convert output model: TypeError: wrong type."
        self.assertEqual(str(error), expected_message)
