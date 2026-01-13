from flask import request, make_response
from flask_restx import Resource
from ..bootstrap import api_schema
from ..utils import HttpStatus
from werkzeug.exceptions import BadRequest, InternalServerError

namespace = api_schema.namespace('health', description='Health check')

@namespace.route('/')
class AppsCollection(Resource):

    def get(self):
        """Get health status"""
        
        response = make_response("Healthy", 200)
        response.mimetype = "text/plain"
        return response

def register():
    api_schema.add_namespace(namespace)
