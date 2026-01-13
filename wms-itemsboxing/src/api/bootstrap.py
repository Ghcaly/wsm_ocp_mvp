from flask import Blueprint
from flask_restx import Api

api_schema = Api(version='1.0', title='Items Boxing API',
                 description='REST API to calculate boxing of items')

@api_schema.errorhandler
def default_error_handler(error):
    '''Default error handler'''
    return {'message': str(error)}, getattr(error, 'code', 500)


def configure_api(flask_app):
    url_prefix = flask_app.config['REVERSE_PROXY_PATH']
    blueprint = Blueprint('api', __name__, url_prefix=url_prefix)
    api_schema.init_app(blueprint)
    flask_app.register_blueprint(blueprint)
