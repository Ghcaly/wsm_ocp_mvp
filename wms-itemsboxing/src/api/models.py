from flask_restx import fields
from api.bootstrap import api_schema

box = api_schema.model('box', {
    'code': fields.Integer(description='box code'),
    'length': fields.Fixed(description='length of the box'),
    'height': fields.Fixed(description='height of the box'),
    'width': fields.Fixed(description='width of the box'),
    'box_slots': fields.Integer(description='how many slots are in the box'),
    'box_slot_diameter': fields.Fixed(description='diameter of each slot in the box'),
})

sku = api_schema.model('sku', {
    'code': fields.Integer(description='sku code'),
    'length': fields.Fixed(description='length of the sku'),
    'height': fields.Fixed(description='height of the sku'),
    'width': fields.Fixed(description='width of the sku'),
    'units_in_boxes': fields.Integer(description='default number of boxed items that comes from the factory'),
    'is_bottle': fields.Boolean(description='defines if the item can be put in a cellar or in a hive'),
    'gross_weight': fields.Fixed(description='gross weight of the sku'),
})

client_sku = api_schema.model('client_sku', {
    'code': fields.Integer(description='sku code'),
    'quantity': fields.Integer(description='number of items')
})

client = api_schema.model('client', {
    'code': fields.Integer(description='client code'),
    'skus': fields.List(fields.Nested(client_sku))
})

input_map = api_schema.model('map', {
    'code': fields.Integer(description='map code'),
    'clients': fields.List(fields.Nested(client))
})

boxing_input = api_schema.model('input', {
    'maps': fields.List(fields.Nested(input_map)),
    'skus': fields.List(fields.Nested(sku)),
    'boxes': fields.List(fields.Nested(box)),
})

output_item = api_schema.model('item', {
    'code': fields.Integer(description='item code'),
    'skus': fields.List(fields.Nested(client_sku))
})

boxing_output_map = api_schema.model('output_map', {
    'boxes': fields.List(fields.Nested(output_item)),
    'packages': fields.List(fields.Nested(client_sku)),
    'unboxed_items': fields.List(fields.Nested(client_sku))
})

boxing_output = api_schema.model('output', {
    'code': fields.Integer(description='map code'),
    'result': fields.Nested(boxing_output_map)
})
