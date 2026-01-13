import unittest
from unittest.mock import patch, Mock
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class WSGITest(unittest.TestCase):

    def test_wsgi_module_has_required_attributes(self):
        # Test that wsgi module has the expected attributes
        import wsgi
        self.assertTrue(hasattr(wsgi, 'app'))
        self.assertTrue(hasattr(wsgi, 'proxied'))

    def test_proxied_instance_type(self):
        # Test that proxied is the correct type
        import wsgi
        from util.flask_reverse_proxied import FlaskReverseProxied
        self.assertIsInstance(wsgi.proxied, FlaskReverseProxied)

    def test_app_is_configured(self):
        # Test that the app has been configured
        import wsgi
        self.assertIsNotNone(wsgi.app)
        # Check that the app has been wrapped with ReverseProxied
        from util.flask_reverse_proxied import ReverseProxied
        self.assertIsInstance(wsgi.app.wsgi_app, ReverseProxied)

    def test_wsgi_app_callable(self):
        # Test that the wsgi app is callable (basic WSGI interface)
        import wsgi
        self.assertTrue(callable(wsgi.app.wsgi_app))


if __name__ == '__main__':
    unittest.main()
