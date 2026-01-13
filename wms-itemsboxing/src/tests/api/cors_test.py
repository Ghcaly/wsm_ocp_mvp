import unittest
from unittest.mock import Mock, MagicMock
from flask import Flask
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from api.cors import configure_cors


class CorsTest(unittest.TestCase):
    
    # Constants
    TEST_ROUTE = '/test'
    ALLOWED_METHODS = 'GET,POST,PUT,DELETE,OPTIONS'

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

    def test_configure_cors_adds_after_request_handler(self):
        # Arrange
        original_after_request_funcs = len(self.app.after_request_funcs.get(None, []))
        
        # Act
        configure_cors(self.app)
        
        # Assert
        new_after_request_funcs = len(self.app.after_request_funcs.get(None, []))
        self.assertEqual(new_after_request_funcs, original_after_request_funcs + 1)

    def test_after_request_handler_sets_cors_headers(self):
        # Arrange
        configure_cors(self.app)
        
        with self.app.test_client() as client:
            # Create a simple route for testing
            @self.app.route(self.TEST_ROUTE)
            def test_route():
                return 'test'
            
            # Act
            response = client.get(self.TEST_ROUTE)
            
            # Assert
            self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
            self.assertEqual(
                response.headers.get('Access-Control-Allow-headers'), 
                'authorization,content-type,accept,referer,user-agent'
            )
            self.assertEqual(
                response.headers.get('Access-Control-Allow-Methods'), 
                self.ALLOWED_METHODS
            )

    def test_after_request_handler_preserves_existing_headers(self):
        # Arrange
        configure_cors(self.app)
        
        with self.app.test_client() as client:
            @self.app.route(self.TEST_ROUTE)
            def test_route():
                from flask import make_response
                response = make_response('test')
                response.headers['Custom-Header'] = 'custom-value'
                return response
            
            # Act
            response = client.get(self.TEST_ROUTE)
            
            # Assert
            self.assertEqual(response.headers.get('Custom-Header'), 'custom-value')
            self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')

    def test_after_request_handler_works_with_different_methods(self):
        # Arrange
        configure_cors(self.app)
        
        with self.app.test_client() as client:
            @self.app.route(self.TEST_ROUTE, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
            def test_route():
                return 'test'
            
            # Test different HTTP methods
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
            
            for method in methods:
                # Act
                response = client.open(self.TEST_ROUTE, method=method)
                
                # Assert
                self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
                self.assertEqual(
                    response.headers.get('Access-Control-Allow-Methods'), 
                    self.ALLOWED_METHODS
                )

    def test_after_request_handler_returns_response(self):
        # Arrange
        configure_cors(self.app)
        
        with self.app.test_client() as client:
            @self.app.route(self.TEST_ROUTE)
            def test_route():
                return 'test response'
            
            # Act
            response = client.get(self.TEST_ROUTE)
            
            # Assert
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_data(as_text=True), 'test response')

    def test_configure_cors_with_mock_app(self):
        # Arrange
        mock_app = Mock()
        mock_after_request_decorator = Mock()
        mock_app.after_request = mock_after_request_decorator
        
        # Act
        configure_cors(mock_app)
        
        # Assert
        mock_app.after_request.assert_called_once()

    def test_after_request_handler_modifies_response_headers(self):
        # Test that the after_request handler actually modifies the response object
        # Arrange
        mock_response = Mock()
        mock_headers = {}
        mock_response.headers = mock_headers
        
        configure_cors(self.app)
        
        # Get the after_request handler that was registered
        after_request_handler = self.app.after_request_funcs[None][0]
        
        # Act
        result = after_request_handler(mock_response)
        
        # Assert
        self.assertEqual(result, mock_response)
        self.assertEqual(mock_headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(
            mock_headers['Access-Control-Allow-headers'], 
            'authorization,content-type,accept,referer,user-agent'
        )
        self.assertEqual(
            mock_headers['Access-Control-Allow-Methods'], 
            'GET,POST,PUT,DELETE,OPTIONS'
        )


if __name__ == '__main__':
    unittest.main()
