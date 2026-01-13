class FlaskReverseProxied(object):

    def __init__(self, app=None):
        self.app = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.app.wsgi_app = ReverseProxied(self.app.wsgi_app)

        return self.app


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ.get('PATH_INFO', '')
            if path_info and path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        server = environ.get('HTTP_X_FORWARDED_SERVER_CUSTOM', 
                             environ.get('HTTP_X_FORWARDED_SERVER', ''))
        if server:
            environ['HTTP_HOST'] = server

        scheme = environ.get('HTTP_X_SCHEME', '')

        if scheme:
            environ['wsgi.url_scheme'] = scheme

        return self.app(environ, start_response)