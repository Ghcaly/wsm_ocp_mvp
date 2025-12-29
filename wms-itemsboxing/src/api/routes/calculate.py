from flask import request
from flask_restx import Resource
from ..bootstrap import api_schema
from ..utils import HttpStatus
from ..models import boxing_input, boxing_output
from core.services import binpacking
from core.converters.errors import InputConversionError
from werkzeug.exceptions import BadRequest, InternalServerError


namespace = api_schema.namespace('v1/calculate', description='Calculate')


@api_schema.response(HttpStatus.OK.code, HttpStatus.OK.description)
@api_schema.response(HttpStatus.BadRequest.code, HttpStatus.BadRequest.description)
@namespace.route('/')
class AppsCollection(Resource):

    @api_schema.marshal_with(boxing_output)
    @api_schema.doc(body=boxing_input)
    def post(self):
        """Get a list of calculated boxes"""
        try:
            body = request.json

            result_data = []
            for map in body['maps']:
                
                binpack_data = {
                    'maps': [map],
                    'boxes': body['boxes'],
                    'skus': body['skus'],
                    'family_groups': body['family_groups'] if 'family_groups' in body else None,
                }

                calculated_boxes = binpacking.get_calculated_boxes(binpack_data)

                result_data.append({
                    'code': map['code'],
                    'result': calculated_boxes
                })

            return result_data, HttpStatus.OK.code
        except InputConversionError as e:
            raise BadRequest(str(e))
        except Exception as e:
            raise InternalServerError(str(e))


def register():
    api_schema.add_namespace(namespace)
