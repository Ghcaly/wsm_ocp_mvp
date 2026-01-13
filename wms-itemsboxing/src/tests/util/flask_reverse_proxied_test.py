import unittest
from unittest.mock import Mock, MagicMock
from flask import Flask
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from util.flask_reverse_proxied import FlaskReverseProxied, ReverseProxied


class FlaskReverseProxiedTest(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

    def test_init_without_app(self):
        # Arrange & Act
        proxied = FlaskReverseProxied()
        
        # Assert
        self.assertIsNone(proxied.app)

    def test_init_with_app(self):
        # Arrange & Act
        proxied = FlaskReverseProxied(self.app)
        
        # Assert
        self.assertEqual(proxied.app, self.app)
        self.assertIsInstance(self.app.wsgi_app, ReverseProxied)

    def test_init_app(self):
        # Arrange
        proxied = FlaskReverseProxied()
        original_wsgi_app = self.app.wsgi_app
        
        # Act
        result = proxied.init_app(self.app)
        
        # Assert
        self.assertEqual(proxied.app, self.app)
        self.assertEqual(result, self.app)
        self.assertIsInstance(self.app.wsgi_app, ReverseProxied)
        self.assertNotEqual(self.app.wsgi_app, original_wsgi_app)

    def test_init_app_wraps_existing_wsgi_app(self):
        # Arrange
        proxied = FlaskReverseProxied()
        original_wsgi_app = self.app.wsgi_app
        
        # Act
        proxied.init_app(self.app)
        
        # Assert
        self.assertIsInstance(self.app.wsgi_app, ReverseProxied)
        self.assertEqual(self.app.wsgi_app.app, original_wsgi_app)


class ReverseProxiedTest(unittest.TestCase):

    # Constants
    API_V1 = '/api/v1'
    SERVER_CUSTOM = 'custom.example.com'
    FORWARDED_SERVER_CUSTOM = 'example.com'
    URL_SCHEME = 'wsgi.url_scheme'

    def setUp(self):
        self.mock_app = Mock()
        self.reverse_proxied = ReverseProxied(self.mock_app)

    def test_init(self):
        # Arrange & Act
        reverse_proxied = ReverseProxied(self.mock_app)
        
        # Assert
        self.assertEqual(reverse_proxied.app, self.mock_app)

    def test_call_without_headers(self):
        # Arrange
        environ = {}
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        result = self.reverse_proxied(environ, start_response)
        
        # Assert
        self.mock_app.assert_called_once_with(environ, start_response)
        self.assertEqual(result, 'response')

    def test_call_with_script_name_header(self):
        # Arrange
        environ = {
            'HTTP_X_SCRIPT_NAME': self.API_V1,
            'PATH_INFO': '/api/v1/test'
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ['SCRIPT_NAME'], self.API_V1)
        self.assertEqual(environ['PATH_INFO'], '/test')
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_with_script_name_but_no_matching_path_info(self):
        # Arrange
        environ = {
            'HTTP_X_SCRIPT_NAME': self.API_V1,
            'PATH_INFO': '/different/path'
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ['SCRIPT_NAME'], self.API_V1)
        self.assertEqual(environ['PATH_INFO'], '/different/path')  # Should remain unchanged
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_with_script_name_but_no_path_info(self):
        # Arrange
        environ = {
            'HTTP_X_SCRIPT_NAME': self.API_V1
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ['SCRIPT_NAME'], self.API_V1)
        self.assertNotIn('PATH_INFO', environ)
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_with_forwarded_server_custom(self):
        # Arrange
        environ = {
            'HTTP_X_FORWARDED_SERVER_CUSTOM': self.SERVER_CUSTOM
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ['HTTP_HOST'], self.SERVER_CUSTOM)
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_with_forwarded_server(self):
        # Arrange
        environ = {
            'HTTP_X_FORWARDED_SERVER': self.FORWARDED_SERVER_CUSTOM
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ['HTTP_HOST'], self.FORWARDED_SERVER_CUSTOM)
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_with_both_forwarded_servers_prefers_custom(self):
        # Arrange
        environ = {
            'HTTP_X_FORWARDED_SERVER_CUSTOM': self.SERVER_CUSTOM,
            'HTTP_X_FORWARDED_SERVER': self.FORWARDED_SERVER_CUSTOM
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ['HTTP_HOST'], self.SERVER_CUSTOM)
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_with_scheme_header(self):
        # Arrange
        environ = {
            'HTTP_X_SCHEME': 'https'
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ[self.URL_SCHEME], 'https')
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_with_all_headers(self):
        # Arrange
        environ = {
            'HTTP_X_SCRIPT_NAME': '/api',
            'PATH_INFO': '/api/test',
            'HTTP_X_FORWARDED_SERVER_CUSTOM': self.SERVER_CUSTOM,
            'HTTP_X_SCHEME': 'https'
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ['SCRIPT_NAME'], '/api')
        self.assertEqual(environ['PATH_INFO'], '/test')
        self.assertEqual(environ['HTTP_HOST'], self.SERVER_CUSTOM)
        self.assertEqual(environ[self.URL_SCHEME], 'https')
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_preserves_other_environ_variables(self):
        # Arrange
        environ = {
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/json',
            'HTTP_X_SCRIPT_NAME': '/api',
            'CUSTOM_VAR': 'custom_value'
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        self.assertEqual(environ['REQUEST_METHOD'], 'GET')
        self.assertEqual(environ['CONTENT_TYPE'], 'application/json')
        self.assertEqual(environ['CUSTOM_VAR'], 'custom_value')
        self.mock_app.assert_called_once_with(environ, start_response)

    def test_call_with_empty_headers(self):
        # Arrange
        environ = {
            'HTTP_X_SCRIPT_NAME': '',
            'HTTP_X_FORWARDED_SERVER_CUSTOM': '',
            'HTTP_X_FORWARDED_SERVER': '',
            'HTTP_X_SCHEME': ''
        }
        start_response = Mock()
        self.mock_app.return_value = 'response'
        
        # Act
        self.reverse_proxied(environ, start_response)
        
        # Assert
        # Empty strings should not modify environ
        self.assertNotIn('SCRIPT_NAME', environ)
        self.assertNotIn('HTTP_HOST', environ)
        self.assertNotIn(self.URL_SCHEME, environ)
        self.mock_app.assert_called_once_with(environ, start_response)


if __name__ == '__main__':
    unittest.main()
