import unittest
from flask_restx import fields
from api import models


class ModelsTest(unittest.TestCase):

    def test_box_model_definition(self):
        # Test that box model has the correct fields
        self.assertIsNotNone(models.box)
        self.assertIn('code', models.box)
        self.assertIn('length', models.box)
        self.assertIn('height', models.box)
        self.assertIn('width', models.box)
        self.assertIn('box_slots', models.box)
        self.assertIn('box_slot_diameter', models.box)

    def test_sku_model_definition(self):
        # Test that sku model has the correct fields
        self.assertIsNotNone(models.sku)
        self.assertIn('code', models.sku)
        self.assertIn('length', models.sku)
        self.assertIn('height', models.sku)
        self.assertIn('width', models.sku)
        self.assertIn('units_in_boxes', models.sku)
        self.assertIn('is_bottle', models.sku)
        self.assertIn('gross_weight', models.sku)

    def test_client_sku_model_definition(self):
        # Test that client_sku model has the correct fields
        self.assertIsNotNone(models.client_sku)
        self.assertIn('code', models.client_sku)
        self.assertIn('quantity', models.client_sku)

    def test_client_model_definition(self):
        # Test that client model has the correct fields
        self.assertIsNotNone(models.client)
        self.assertIn('code', models.client)
        self.assertIn('skus', models.client)

    def test_input_map_model_definition(self):
        # Test that input_map model has the correct fields
        self.assertIsNotNone(models.input_map)
        self.assertIn('code', models.input_map)
        self.assertIn('clients', models.input_map)

    def test_boxing_input_model_definition(self):
        # Test that boxing_input model has the correct fields
        self.assertIsNotNone(models.boxing_input)
        self.assertIn('maps', models.boxing_input)
        self.assertIn('skus', models.boxing_input)
        self.assertIn('boxes', models.boxing_input)

    def test_output_item_model_definition(self):
        # Test that output_item model has the correct fields
        self.assertIsNotNone(models.output_item)
        self.assertIn('code', models.output_item)
        self.assertIn('skus', models.output_item)

    def test_boxing_output_map_model_definition(self):
        # Test that boxing_output_map model has the correct fields
        self.assertIsNotNone(models.boxing_output_map)
        self.assertIn('boxes', models.boxing_output_map)
        self.assertIn('packages', models.boxing_output_map)
        self.assertIn('unboxed_items', models.boxing_output_map)

    def test_boxing_output_model_definition(self):
        # Test that boxing_output model has the correct fields
        self.assertIsNotNone(models.boxing_output)
        self.assertIn('code', models.boxing_output)
        self.assertIn('result', models.boxing_output)

    def test_models_exist(self):
        # Test that all model variables are defined
        self.assertIsNotNone(models.box)
        self.assertIsNotNone(models.sku)
        self.assertIsNotNone(models.client_sku)
        self.assertIsNotNone(models.client)
        self.assertIsNotNone(models.input_map)
        self.assertIsNotNone(models.boxing_input)
        self.assertIsNotNone(models.output_item)
        self.assertIsNotNone(models.boxing_output_map)
        self.assertIsNotNone(models.boxing_output)

    def test_model_field_types(self):
        # Test that models have correct field types
        self.assertIsInstance(models.box['code'], fields.Integer)
        self.assertIsInstance(models.box['length'], fields.Fixed)
        self.assertIsInstance(models.sku['is_bottle'], fields.Boolean)
        self.assertIsInstance(models.client['skus'], fields.List)
        self.assertIsInstance(models.input_map['clients'], fields.List)
