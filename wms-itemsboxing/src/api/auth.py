import jwt
import config
from flask import request
from .utils import HttpStatus

swagger_endpoints = ['api.doc', 'api.specs', 'restplus_doc.static']


def is_swagger(request):
    return request.endpoint in swagger_endpoints or '/swaggerui/' in request.url


def is_authorized(request):
    if 'Authorization' not in request.headers:
        return False
    token = request.headers['Authorization']
    try:
        jwt.decode(token, config.JWT_KEY, algorithms=['HS256'])
        return True
    except Exception:
        return False


def configure_auth(app):
    @app.before_request
    def before_request():
        if not is_authorized(request) and not is_swagger(request) and request.method != 'OPTIONS':
            return '', HttpStatus.Unauthorized.code
