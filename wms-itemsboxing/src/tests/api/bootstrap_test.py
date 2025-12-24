import unittest
from unittest.mock import Mock, patch
from flask import Flask
from api.bootstrap import default_error_handler, configure_api


class BootstrapTest(unittest.TestCase):

    def test_default_error_handler_with_exception(self):
        # Arrange
        error = Exception("Test error")

        # Act
        response, status_code = default_error_handler(error)

        # Assert
        self.assertEqual(response, {'message': 'Test error'})
        self.assertEqual(status_code, 500)  # Default error code

    def test_default_error_handler_with_exception_with_code(self):
        # Arrange
        error = Exception("Test error")
        error.code = 400

        # Act
        response, status_code = default_error_handler(error)

        # Assert
        self.assertEqual(response, {'message': 'Test error'})
        self.assertEqual(status_code, 400)

    def test_default_error_handler_with_string_error(self):
        # Arrange
        error = "String error message"

        # Act
        response, status_code = default_error_handler(error)

        # Assert
        self.assertEqual(response, {'message': 'String error message'})
        self.assertEqual(status_code, 500)  # Default error code

    @patch('api.bootstrap.Blueprint')
    @patch('api.bootstrap.api_schema')
    def test_configure_api(self, mock_api_schema, mock_blueprint):
        # Arrange
        app = Flask(__name__)
        app.config['REVERSE_PROXY_PATH'] = '/api'
        mock_blueprint_instance = Mock()
        mock_blueprint.return_value = mock_blueprint_instance
        
        # Mock the register_blueprint method
        app.register_blueprint = Mock()

        # Act
        configure_api(app)

        # Assert
        mock_blueprint.assert_called_once_with('api', unittest.mock.ANY, url_prefix='/api')
        mock_api_schema.init_app.assert_called_once_with(mock_blueprint_instance)
        app.register_blueprint.assert_called_once_with(mock_blueprint_instance)

    def test_api_schema_exists(self):
        # Test that api_schema is properly initialized
        from api.bootstrap import api_schema
        self.assertIsNotNone(api_schema)
        self.assertEqual(api_schema.version, '1.0')
        self.assertEqual(api_schema.title, 'Items Boxing API')
