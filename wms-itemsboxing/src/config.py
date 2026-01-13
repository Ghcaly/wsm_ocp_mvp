import os

# Flask settings
FLASK_SERVER_NAME = '0.0.0.0:8001'
FLASK_DEBUG = bool(os.getenv('FLASK_DEBUG', 'True'))  
FLASK_ENV = os.getenv('FLASK_ENV', 'Development')
ENDPOINT_PREFIX = os.getenv('ENDPOINT_PREFIX', '/api/items-boxing')

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# File upload related configurations
MAX_CONTENT_LENGTH = 32 * 1024 * 1024 #32 Mb

JWT_KEY = os.getenv('ITEMSBOXING_JWT_KEY', 'CF64C4AE-AE2E-4277-B20F-917B6740A22E')

def configure_app(flask_app):
    flask_app.config['FLASK_SERVER_NAME'] = FLASK_SERVER_NAME
    flask_app.config['FLASK_ENV'] = FLASK_ENV
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = RESTPLUS_ERROR_404_HELP
    flask_app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    flask_app.config['REVERSE_PROXY_PATH'] = ENDPOINT_PREFIX
