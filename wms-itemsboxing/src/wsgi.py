from app import configure, app
from util.flask_reverse_proxied import FlaskReverseProxied
configure()
proxied = FlaskReverseProxied()
proxied.init_app(app)