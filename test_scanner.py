#!/usr/bin/env python3
"""
Test script for DarkMad Hidden Services Scanner
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from darkmad_hidden import Config, TelegramNotifier, HiddenServiceScanner


class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config_file = 'test_config.json'
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
    
    def test_default_config_creation(self):
        """Test that default config is created"""
        config = Config(self.test_config_file)
        self.assertTrue(os.path.exists(self.test_config_file))
        
        # Verify default values
        self.assertEqual(config.get('tor_proxy.enabled'), True)
        self.assertEqual(config.get('tor_proxy.port'), 9050)
        self.assertEqual(config.get('telegram.enabled'), False)
    
    def test_config_get(self):
        """Test configuration retrieval"""
        config = Config(self.test_config_file)
        
        # Test nested key access
        self.assertEqual(config.get('tor_proxy.host'), '127.0.0.1')
        self.assertEqual(config.get('reports.directory'), 'reports')
        
        # Test default value
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
    
    def test_config_save_and_load(self):
        """Test saving and loading configuration"""
        config1 = Config(self.test_config_file)
        config1.config['test_key'] = 'test_value'
        config1.save_config()
        
        config2 = Config(self.test_config_file)
        self.assertEqual(config2.config['test_key'], 'test_value')


class TestTelegramNotifier(unittest.TestCase):
    """Test Telegram notification functionality"""
    
    @patch('requests.post')
    def test_send_message_success(self, mock_post):
        """Test successful message sending"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        notifier = TelegramNotifier('test_token', 'test_chat_id')
        result = notifier.send_message('Test message')
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_message_failure(self, mock_post):
        """Test failed message sending"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Error'
        mock_post.return_value = mock_response
        
        notifier = TelegramNotifier('test_token', 'test_chat_id')
        result = notifier.send_message('Test message')
        
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_send_credential_report(self, mock_post):
        """Test credential report formatting"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        notifier = TelegramNotifier('test_token', 'test_chat_id')
        credentials = {
            'username': 'testuser',
            'password': 'testpass',
            'extra_field': 'extra_value'
        }
        
        result = notifier.send_credential_report('http://test.onion', credentials)
        
        self.assertTrue(result)
        # Verify the message contains the credentials
        call_args = mock_post.call_args
        message_text = call_args[1]['data']['text']
        self.assertIn('testuser', message_text)
        self.assertIn('testpass', message_text)
        self.assertIn('http://test.onion', message_text)


class TestHiddenServiceScanner(unittest.TestCase):
    """Test hidden service scanner"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config_file = 'test_config.json'
        self.config = Config(self.test_config_file)
        self.config.config['tor_proxy']['enabled'] = False
        self.config.config['telegram']['enabled'] = False
        self.config.save_config()
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        # Clean up test reports
        reports_dir = Path('reports')
        if reports_dir.exists():
            for f in reports_dir.glob('test_*.json'):
                f.unlink()
    
    def test_scanner_initialization(self):
        """Test scanner initialization"""
        scanner = HiddenServiceScanner(self.config)
        
        self.assertIsNotNone(scanner.session)
        self.assertTrue(scanner.reports_dir.exists())
        self.assertIsNone(scanner.telegram)
    
    def test_proxy_configuration(self):
        """Test proxy configuration"""
        self.config.config['tor_proxy']['enabled'] = True
        scanner = HiddenServiceScanner(self.config)
        
        proxies = scanner._get_proxies()
        self.assertIn('http', proxies)
        self.assertIn('https', proxies)
        self.assertIn('socks5://', proxies['http'])
    
    def test_extract_credentials(self):
        """Test credential extraction from HTML"""
        scanner = HiddenServiceScanner(self.config)
        
        # Test HTML with password field
        html_with_password = '<form><input type="password" name="pass"></form>'
        credentials = scanner._extract_credentials(html_with_password, 'http://test.onion')
        self.assertIsNotNone(credentials)
        self.assertTrue(credentials.get('has_password_field'))
        
        # Test HTML without password field
        html_without_password = '<div>No forms here</div>'
        credentials = scanner._extract_credentials(html_without_password, 'http://test.onion')
        self.assertIsNone(credentials)
    
    def test_save_report(self):
        """Test report saving"""
        scanner = HiddenServiceScanner(self.config)
        
        test_data = {
            'url': 'http://test.onion',
            'credentials': {'username': 'test', 'password': 'test123'},
            'timestamp': '2024-01-01T00:00:00'
        }
        
        filepath = scanner.save_report(test_data, 'http://test.onion')
        
        self.assertIsNotNone(filepath)
        self.assertTrue(filepath.exists())
        
        # Verify report content
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['url'], test_data['url'])
        self.assertEqual(saved_data['credentials']['username'], 'test')
    
    @patch('darkmad_hidden.HiddenServiceScanner.scan_hidden_service')
    def test_scan_all_targets(self, mock_scan):
        """Test scanning all configured targets"""
        mock_scan.return_value = {
            'url': 'http://test.onion',
            'status': 'scanned',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        self.config.config['targets']['hidden_services'] = [
            'http://test1.onion',
            'http://test2.onion'
        ]
        
        scanner = HiddenServiceScanner(self.config)
        results = scanner.scan_all_targets()
        
        self.assertEqual(len(results), 2)
        self.assertEqual(mock_scan.call_count, 2)


def run_tests():
    """Run all tests"""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramNotifier))
    suite.addTests(loader.loadTestsFromTestCase(TestHiddenServiceScanner))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
