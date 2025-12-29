from .routes import calculate, health
from . import bootstrap
from . import auth
from . import cors

def configure_api(flask_app):
    cors.configure_cors(flask_app)
    #auth.configure_auth(flask_app)
    bootstrap.configure_api(flask_app)
    calculate.register()
    health.register()
