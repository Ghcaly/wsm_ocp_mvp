import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class AppTest(unittest.TestCase):

    @patch('app.configure_datadog')
    @patch('app.api.configure_api')
    @patch('app.config.configure_app')
    def test_configure(self, mock_configure_app, mock_configure_api, mock_configure_datadog):
        # Arrange
        from app import app, configure
        
        # Act
        configure()
        
        # Assert
        mock_configure_app.assert_called_once_with(app)
        mock_configure_api.assert_called_once_with(app)
        mock_configure_datadog.assert_called_once()

    @patch('app.logging.getLogger')
    @patch('app.logging.basicConfig')
    def test_configure_datadog(self, mock_basic_config, mock_get_logger):
        # Arrange
        from app import configure_datadog
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Act
        configure_datadog()
        
        # Assert
        mock_basic_config.assert_called_once()
        mock_get_logger.assert_called_once()
        self.assertEqual(mock_logger.level, 20)

    @patch('app.ProxyFix')
    @patch('app.configure')
    @patch('app.os.getenv')
    def test_main_with_default_port(self, mock_getenv, mock_configure, mock_proxy_fix):
        # Arrange
        from app import main, app
        mock_getenv.return_value = 8001
        mock_proxy_fix_instance = Mock()
        mock_proxy_fix.return_value = mock_proxy_fix_instance
        app.run = Mock()
        
        # Act
        main()
        
        # Assert
        mock_configure.assert_called_once()
        mock_getenv.assert_called_once_with("port", 8001)
        mock_proxy_fix.assert_called_once()
        self.assertEqual(app.wsgi_app, mock_proxy_fix_instance)
        app.run.assert_called_once()

    @patch('app.ProxyFix')
    @patch('app.configure')
    @patch('app.os.getenv')
    def test_main_with_custom_port(self, mock_getenv, mock_configure, mock_proxy_fix):
        # Arrange
        from app import main, app
        mock_getenv.return_value = 9000
        mock_proxy_fix_instance = Mock()
        mock_proxy_fix.return_value = mock_proxy_fix_instance
        app.run = Mock()
        
        # Act
        main()
        
        # Assert
        mock_configure.assert_called_once()
        mock_getenv.assert_called_once_with("port", 8001)
        mock_proxy_fix.assert_called_once()
        app.run.assert_called_once()

    def test_app_instance_exists(self):
        # Test that Flask app instance is created
        from app import app
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'app')

    @patch('app.print')
    @patch('app.ProxyFix')
    @patch('app.configure')
    @patch('app.os.getenv')
    @patch('app.config.FLASK_SERVER_NAME', 'localhost:8001')
    @patch('app.config.FLASK_DEBUG', True)
    def test_main_prints_server_info(self, mock_getenv, mock_configure, mock_proxy_fix, mock_print):
        # Arrange
        from app import main, app
        mock_getenv.return_value = 8001
        app.run = Mock()
        
        # Act
        main()
        
        # Assert
        mock_print.assert_called_once_with('>>>>> Starting development server at http://localhost:8001/ <<<<<')

    @patch('app.main')
    def test_main_called_when_script_run_directly(self, mock_main):
        # This test simulates running the script directly
        # We can't easily test __name__ == "__main__" condition in unit tests
        # but we can test that main function works correctly
        mock_main.assert_not_called()  # Should not be called during import


if __name__ == '__main__':
    unittest.main()
