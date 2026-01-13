from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import api
import config
import os
# from ddtrace import patch_all; patch_all(logging=True)
import logging

app = Flask(__name__)


def configure():
    config.configure_app(app)
    api.configure_api(app)
    configure_datadog()


def configure_datadog():
    FORMAT = '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger()
    logger.level = logging.INFO


def main():
    configure()
    port = os.getenv("port", 8001)
    print('>>>>> Starting development server at http://{}/ <<<<<'.format(config.FLASK_SERVER_NAME))
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(debug=config.FLASK_DEBUG, host='0.0.0.0', port=port)


if __name__ == "__main__":
    main()
