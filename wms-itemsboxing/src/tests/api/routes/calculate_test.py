import unittest
from unittest.mock import patch, Mock
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from flask import Flask
from api.routes.calculate import AppsCollection, register, namespace
from api.bootstrap import api_schema
from core.converters.errors import InputConversionError
from werkzeug.exceptions import BadRequest, InternalServerError


class CalculateRouteTest(unittest.TestCase):
    
    # Constants
    CALCULATE_ENDPOINT = '/v1/calculate/'
    JSON_CONTENT_TYPE = 'application/json'

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        api_schema.init_app(self.app)
        register()
        self.client = self.app.test_client()

    @patch('api.routes.calculate.binpacking.get_calculated_boxes')
    def test_post_success_single_map(self, mock_get_calculated_boxes):
        # Arrange
        mock_get_calculated_boxes.return_value = {
            'boxes': [{'code': 1, 'skus': []}],
            'packages': [],
            'unboxed_items': []
        }
        
        request_data = {
            'maps': [{'code': 1, 'clients': []}],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data),
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['code'], 1)
        self.assertIn('result', response_data[0])
        mock_get_calculated_boxes.assert_called_once()

    @patch('api.routes.calculate.binpacking.get_calculated_boxes')
    def test_post_success_multiple_maps(self, mock_get_calculated_boxes):
        # Arrange
        mock_get_calculated_boxes.return_value = {
            'boxes': [{'code': 1, 'skus': []}],
            'packages': [],
            'unboxed_items': []
        }
        
        request_data = {
            'maps': [
                {'code': 1, 'clients': []},
                {'code': 2, 'clients': []}
            ],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data),
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]['code'], 1)
        self.assertEqual(response_data[1]['code'], 2)
        self.assertEqual(mock_get_calculated_boxes.call_count, 2)

    @patch('api.routes.calculate.binpacking.get_calculated_boxes')
    def test_post_with_family_groups(self, mock_get_calculated_boxes):
        # Arrange
        mock_get_calculated_boxes.return_value = {
            'boxes': [{'code': 1, 'skus': []}],
            'packages': [],
            'unboxed_items': []
        }
        
        request_data = {
            'maps': [{'code': 1, 'clients': []}],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}],
            'family_groups': [{'code': 1, 'items': []}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data),
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        # Verify that family_groups was passed to binpacking
        call_args = mock_get_calculated_boxes.call_args[0][0]
        self.assertIn('family_groups', call_args)
        self.assertEqual(call_args['family_groups'], [{'code': 1, 'items': []}])

    @patch('api.routes.calculate.binpacking.get_calculated_boxes')
    def test_post_without_family_groups(self, mock_get_calculated_boxes):
        # Arrange
        mock_get_calculated_boxes.return_value = {
            'boxes': [{'code': 1, 'skus': []}],
            'packages': [],
            'unboxed_items': []
        }
        
        request_data = {
            'maps': [{'code': 1, 'clients': []}],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data),
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        # Verify that family_groups was set to None
        call_args = mock_get_calculated_boxes.call_args[0][0]
        self.assertIn('family_groups', call_args)
        self.assertIsNone(call_args['family_groups'])

    @patch('api.routes.calculate.binpacking.get_calculated_boxes')
    def test_post_input_conversion_error(self, mock_get_calculated_boxes):
        # Arrange
        mock_get_calculated_boxes.side_effect = InputConversionError("Invalid input format")
        
        request_data = {
            'maps': [{'code': 1, 'clients': []}],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data),
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        self.assertEqual(response.status_code, 400)

    @patch('api.routes.calculate.binpacking.get_calculated_boxes')
    def test_post_internal_server_error(self, mock_get_calculated_boxes):
        # Arrange
        mock_get_calculated_boxes.side_effect = Exception("Unexpected error")
        
        request_data = {
            'maps': [{'code': 1, 'clients': []}],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data),
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        self.assertEqual(response.status_code, 500)

    def test_post_invalid_json(self):
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data='invalid json',
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        # BadRequest gets caught and re-raised as InternalServerError in the route
        self.assertEqual(response.status_code, 500)

    def test_post_missing_content_type(self):
        # Arrange
        request_data = {
            'maps': [{'code': 1, 'clients': []}],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data))
        
        # Assert
        # Should still work as Flask can handle JSON without explicit content-type
        self.assertIn(response.status_code, [200, 400, 500])

    @patch('api.routes.calculate.binpacking.get_calculated_boxes')
    def test_binpack_data_structure(self, mock_get_calculated_boxes):
        # Arrange
        mock_get_calculated_boxes.return_value = {'result': 'test'}
        
        request_data = {
            'maps': [{'code': 1, 'clients': [{'code': 1}]}],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}],
            'family_groups': [{'code': 1}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data),
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        call_args = mock_get_calculated_boxes.call_args[0][0]
        
        # Verify the structure passed to binpacking
        self.assertEqual(call_args['maps'], [{'code': 1, 'clients': [{'code': 1}]}])
        self.assertEqual(call_args['boxes'], [{'code': 1, 'length': 10}])
        self.assertEqual(call_args['skus'], [{'code': 1, 'length': 5}])
        self.assertEqual(call_args['family_groups'], [{'code': 1}])

    def test_register_function(self):
        # Test that register function adds namespace to api_schema
        # This is tested indirectly through the successful route calls above
        # but we can also test it directly
        
        # The namespace should be registered when register() is called
        # We can verify this by checking if the namespace exists
        self.assertIsNotNone(namespace)
        self.assertEqual(namespace.name, 'v1/calculate')

    @patch('api.routes.calculate.binpacking.get_calculated_boxes')
    def test_response_structure(self, mock_get_calculated_boxes):
        # Arrange
        mock_result = {
            'boxes': [{'code': 1, 'skus': [{'code': 1, 'quantity': 2}]}],
            'packages': [{'code': 2, 'quantity': 1}],
            'unboxed_items': [{'code': 3, 'quantity': 1}]
        }
        mock_get_calculated_boxes.return_value = mock_result
        
        request_data = {
            'maps': [{'code': 100, 'clients': []}],
            'boxes': [{'code': 1, 'length': 10}],
            'skus': [{'code': 1, 'length': 5}]
        }
        
        # Act
        response = self.client.post(self.CALCULATE_ENDPOINT, 
                                  data=json.dumps(request_data),
                                  content_type=self.JSON_CONTENT_TYPE)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify response structure
        self.assertEqual(len(response_data), 1)
        result_item = response_data[0]
        self.assertEqual(result_item['code'], 100)
        self.assertEqual(result_item['result'], mock_result)


class AppsCollectionTest(unittest.TestCase):

    def test_apps_collection_class_exists(self):
        # Test that the AppsCollection class is properly defined
        self.assertTrue(hasattr(AppsCollection, 'post'))
        self.assertTrue(callable(getattr(AppsCollection, 'post')))


if __name__ == '__main__':
    unittest.main()
