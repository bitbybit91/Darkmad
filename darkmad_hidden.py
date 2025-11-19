#!/usr/bin/env python3
"""
DarkMad - Hidden Services Scanner
Production-ready tool for VPS deployment targeting hidden services (.onion sites)
"""

import os
import sys
import json
import time
import logging
import requests
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('darkmad.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration management for DarkMad"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return self.default_config()
        else:
            logger.info("Config file not found, creating default config")
            config = self.default_config()
            self.save_config(config)
            return config
    
    def default_config(self) -> dict:
        """Return default configuration"""
        return {
            "tor_proxy": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 9050,
                "type": "socks5"
            },
            "telegram": {
                "enabled": False,
                "bot_token": "YOUR_BOT_TOKEN_HERE",
                "chat_id": "YOUR_CHAT_ID_HERE"
            },
            "scanning": {
                "timeout": 30,
                "retry_attempts": 3,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "reports": {
                "directory": "reports",
                "format": "json"
            },
            "targets": {
                "hidden_services": []
            }
        }
    
    def save_config(self, config: dict = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value


class TelegramNotifier:
    """Send notifications via Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str, proxies: dict = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.proxies = proxies
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str) -> bool:
        """Send a message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, proxies=self.proxies, timeout=30)
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram notification: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    def send_credential_report(self, hidden_service: str, credentials: Dict[str, str]):
        """Send credential report to Telegram"""
        message = (
            f"🔐 <b>New Credentials Found</b>\n\n"
            f"<b>Hidden Service:</b> {hidden_service}\n"
            f"<b>Username:</b> {credentials.get('username', 'N/A')}\n"
            f"<b>Password:</b> {credentials.get('password', 'N/A')}\n"
            f"<b>Additional Info:</b>\n"
        )
        
        for key, value in credentials.items():
            if key not in ['username', 'password']:
                message += f"  • {key}: {value}\n"
        
        message += f"\n<b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)


class HiddenServiceScanner:
    """Scanner for hidden services (.onion sites)"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = self._create_session()
        self.reports_dir = Path(config.get('reports.directory', 'reports'))
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize Telegram notifier if enabled
        if config.get('telegram.enabled'):
            self.telegram = TelegramNotifier(
                config.get('telegram.bot_token'),
                config.get('telegram.chat_id'),
                proxies=self._get_proxies() if config.get('tor_proxy.enabled') else None
            )
        else:
            self.telegram = None
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with proxy support"""
        session = requests.Session()
        
        # Set user agent
        session.headers.update({
            'User-Agent': self.config.get('scanning.user_agent')
        })
        
        # Configure proxy if enabled
        if self.config.get('tor_proxy.enabled'):
            session.proxies = self._get_proxies()
        
        return session
    
    def _get_proxies(self) -> dict:
        """Get proxy configuration"""
        proxy_type = self.config.get('tor_proxy.type', 'socks5')
        proxy_host = self.config.get('tor_proxy.host', '127.0.0.1')
        proxy_port = self.config.get('tor_proxy.port', 9050)
        
        proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def scan_hidden_service(self, url: str) -> Optional[Dict]:
        """Scan a hidden service for credentials and information"""
        logger.info(f"Scanning hidden service: {url}")
        
        try:
            timeout = self.config.get('scanning.timeout', 30)
            response = self.session.get(url, timeout=timeout, verify=False)
            
            if response.status_code == 200:
                # Basic credential extraction from common form patterns
                credentials = self._extract_credentials(response.text, url)
                
                if credentials:
                    logger.info(f"Credentials found on {url}")
                    return {
                        'url': url,
                        'credentials': credentials,
                        'timestamp': datetime.now().isoformat(),
                        'status_code': response.status_code
                    }
                else:
                    logger.info(f"No credentials found on {url}")
                    return {
                        'url': url,
                        'status': 'scanned',
                        'timestamp': datetime.now().isoformat(),
                        'status_code': response.status_code
                    }
            else:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout scanning {url}")
            return None
        except Exception as e:
            logger.error(f"Error scanning {url}: {e}")
            return None
    
    def _extract_credentials(self, html_content: str, url: str) -> Optional[Dict[str, str]]:
        """
        Extract credentials from HTML content
        This is a basic implementation - in production, you'd want more sophisticated methods
        """
        credentials = {}
        
        # Look for common input field patterns
        # This is a simplified example - real implementation would need more robust parsing
        if 'type="password"' in html_content.lower() or 'type=password' in html_content.lower():
            # Simulate credential harvesting - in real scenario, this would involve
            # form submission, session handling, etc.
            credentials['form_detected'] = True
            credentials['has_password_field'] = True
            credentials['url'] = url
            
            # Check for username/email fields
            if 'type="text"' in html_content.lower() or 'type="email"' in html_content.lower():
                credentials['has_username_field'] = True
        
        return credentials if credentials else None
    
    def save_report(self, data: Dict, hidden_service: str):
        """Save scan report to file"""
        # Create safe filename from hidden service URL
        safe_name = hidden_service.replace('http://', '').replace('https://', '').replace('/', '_').replace(':', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.json"
        
        filepath = self.reports_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Report saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return None
    
    def scan_all_targets(self):
        """Scan all configured hidden services"""
        targets = self.config.get('targets.hidden_services', [])
        
        if not targets:
            logger.warning("No hidden services configured for scanning")
            return
        
        logger.info(f"Starting scan of {len(targets)} hidden services")
        
        results = []
        for target in targets:
            result = self.scan_hidden_service(target)
            if result:
                results.append(result)
                
                # Save report
                self.save_report(result, target)
                
                # Send Telegram notification if credentials found
                if 'credentials' in result and self.telegram:
                    self.telegram.send_credential_report(target, result['credentials'])
                
                # Rate limiting
                time.sleep(2)
        
        logger.info(f"Scan completed. {len(results)} services scanned successfully")
        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='DarkMad - Hidden Services Scanner for VPS deployment'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Start scanning configured hidden services'
    )
    parser.add_argument(
        '--init-config',
        action='store_true',
        help='Create default configuration file'
    )
    
    args = parser.parse_args()
    
    # Initialize configuration
    config = Config(args.config)
    
    if args.init_config:
        logger.info("Configuration file created/updated")
        print(f"Configuration file: {args.config}")
        print("Please edit the configuration file with your settings before scanning")
        return 0
    
    if args.scan:
        scanner = HiddenServiceScanner(config)
        scanner.scan_all_targets()
        return 0
    
    # Show help if no action specified
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
