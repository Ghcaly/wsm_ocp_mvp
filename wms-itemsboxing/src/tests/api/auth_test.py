import unittest
from unittest.mock import Mock, patch
from flask import Flask
from api.auth import is_swagger, is_authorized, configure_auth
from api.utils import HttpStatus
from werkzeug.exceptions import Unauthorized
import jwt


class AuthTest(unittest.TestCase):
    
    # Constants
    TEST_API_PATH = '/api/test'

    def test_is_swagger_should_return_true_when_endpoint_in_swagger_endpoints(self):
        # Arrange
        request = Mock()
        request.endpoint = 'api.doc'
        request.url = 'http://localhost/test'

        # Act
        result = is_swagger(request)

        # Assert
        self.assertTrue(result)

    def test_is_swagger_should_return_true_when_url_contains_swaggerui(self):
        # Arrange
        request = Mock()
        request.endpoint = 'other.endpoint'
        request.url = 'http://localhost/swaggerui/index.html'

        # Act
        result = is_swagger(request)

        # Assert
        self.assertTrue(result)

    def test_is_swagger_should_return_false_when_not_swagger(self):
        # Arrange
        request = Mock()
        request.endpoint = 'other.endpoint'
        request.url = 'http://localhost/api/test'

        # Act
        result = is_swagger(request)

        # Assert
        self.assertFalse(result)

    def test_is_authorized_should_return_false_when_no_authorization_header(self):
        # Arrange
        request = Mock()
        request.headers = {}

        # Act
        result = is_authorized(request)

        # Assert
        self.assertFalse(result)

    @patch('api.auth.jwt.decode')
    @patch('api.auth.config.JWT_KEY', 'test_key')
    def test_is_authorized_should_return_true_when_valid_token(self, mock_jwt_decode):
        # Arrange
        request = Mock()
        request.headers = {'Authorization': 'valid_token'}
        mock_jwt_decode.return_value = {'user': 'test'}

        # Act
        result = is_authorized(request)

        # Assert
        self.assertTrue(result)
        mock_jwt_decode.assert_called_once_with('valid_token', 'test_key', algorithms=['HS256'])

    @patch('api.auth.jwt.decode')
    @patch('api.auth.config.JWT_KEY', 'test_key')
    def test_is_authorized_should_return_false_when_invalid_token(self, mock_jwt_decode):
        # Arrange
        request = Mock()
        request.headers = {'Authorization': 'invalid_token'}
        mock_jwt_decode.side_effect = jwt.InvalidTokenError()

        # Act
        result = is_authorized(request)

        # Assert
        self.assertFalse(result)

    @patch('api.auth.is_authorized')
    @patch('api.auth.is_swagger')
    def test_configure_auth_should_allow_authorized_request(self, mock_is_swagger, mock_is_authorized):
        # Arrange
        app = Flask(__name__)
        mock_is_authorized.return_value = True
        mock_is_swagger.return_value = False
        
        configure_auth(app)

        # Act
        with app.test_request_context(self.TEST_API_PATH, method='GET'):
            response = app.preprocess_request()

        # Assert
        self.assertIsNone(response)

    @patch('api.auth.is_authorized')
    @patch('api.auth.is_swagger')
    def test_configure_auth_should_allow_swagger_request(self, mock_is_swagger, mock_is_authorized):
        # Arrange
        app = Flask(__name__)
        mock_is_authorized.return_value = False
        mock_is_swagger.return_value = True
        
        configure_auth(app)

        # Act
        with app.test_request_context('/swaggerui/', method='GET'):
            response = app.preprocess_request()

        # Assert
        self.assertIsNone(response)

    @patch('api.auth.is_authorized')
    @patch('api.auth.is_swagger')
    def test_configure_auth_should_allow_options_request(self, mock_is_swagger, mock_is_authorized):
        # Arrange
        app = Flask(__name__)
        mock_is_authorized.return_value = False
        mock_is_swagger.return_value = False
        
        configure_auth(app)

        # Act
        with app.test_request_context(self.TEST_API_PATH, method='OPTIONS'):
            response = app.preprocess_request()

        # Assert
        self.assertIsNone(response)

    @patch('api.auth.is_authorized')
    @patch('api.auth.is_swagger')
    def test_configure_auth_should_return_unauthorized_when_not_authorized(self, mock_is_swagger, mock_is_authorized):
        # Arrange
        app = Flask(__name__)
        mock_is_authorized.return_value = False
        mock_is_swagger.return_value = False
        
        configure_auth(app)

        # Act
        with app.test_request_context(self.TEST_API_PATH, method='GET'):
            response = app.preprocess_request()

        # Assert
        self.assertIsNotNone(response)
        self.assertEqual(response[0], '')
        self.assertEqual(response[1], HttpStatus.Unauthorized.code)
