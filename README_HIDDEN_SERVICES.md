# DarkMad - Hidden Services Scanner

Production-ready scanner for VPS deployment specifically designed for hidden services (.onion sites) with system hardening bypass capabilities, automatic reporting, and Telegram notifications.

## Features

- ✅ **VPS Optimized**: Designed for deployment on Virtual Private Servers
- ✅ **Hidden Services Support**: Specifically targets .onion domains via Tor
- ✅ **Automated Scanning**: Systemd service with 2-hour interval timer
- ✅ **Local Report Storage**: All findings stored in organized JSON reports
- ✅ **Telegram Integration**: Real-time notifications with credentials and service info
- ✅ **System Hardening Aware**: Works with security-hardened systems
- ✅ **Production Ready**: Full error handling, logging, and monitoring
- ✅ **Secure by Design**: Runs as unprivileged user with systemd security features

## System Requirements

- **OS**: Linux (Debian/Ubuntu/CentOS/RHEL recommended)
- **Python**: 3.8 or higher
- **Tor**: Required for .onion access
- **Memory**: Minimum 512MB RAM
- **Disk**: 1GB free space for reports and logs
- **Network**: Internet connectivity and Tor daemon access

## Installation

### Quick Install (Recommended)

Run the automated installation script as root:

```bash
sudo ./install.sh
```

This will:
- Install Python dependencies
- Create service user and directories
- Set up systemd service and timer
- Configure permissions and security

### Manual Installation

1. **Install Dependencies**:
   ```bash
   apt-get update
   apt-get install -y python3 python3-pip tor
   pip3 install -r requirements.txt
   ```

2. **Install Tor** (if not already installed):
   ```bash
   # Debian/Ubuntu
   apt-get install tor
   systemctl enable tor
   systemctl start tor
   
   # CentOS/RHEL
   yum install tor
   systemctl enable tor
   systemctl start tor
   ```

3. **Create Service User**:
   ```bash
   useradd -r -s /bin/false -d /opt/darkmad darkmad
   ```

4. **Set Up Directories**:
   ```bash
   mkdir -p /opt/darkmad/reports
   mkdir -p /var/log/darkmad
   cp darkmad_hidden.py /opt/darkmad/
   chmod +x /opt/darkmad/darkmad_hidden.py
   ```

5. **Create Configuration**:
   ```bash
   cd /opt/darkmad
   python3 darkmad_hidden.py --init-config
   ```

6. **Install Systemd Service**:
   ```bash
   cp darkmad.service /etc/systemd/system/
   cp darkmad.timer /etc/systemd/system/
   systemctl daemon-reload
   systemctl enable darkmad.timer
   systemctl start darkmad.timer
   ```

## Configuration

Edit `/opt/darkmad/config.json` to configure the scanner:

### Tor Proxy Settings

```json
{
  "tor_proxy": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 9050,
    "type": "socks5"
  }
}
```

### Telegram Notifications

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Get your chat ID (use [@userinfobot](https://t.me/userinfobot))
4. Configure in config.json:

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHAT_ID_HERE"
  }
}
```

### Target Hidden Services

Add hidden services to scan:

```json
{
  "targets": {
    "hidden_services": [
      "http://example1.onion",
      "http://example2.onion",
      "http://example3.onion"
    ]
  }
}
```

### Full Configuration Example

```json
{
  "tor_proxy": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 9050,
    "type": "socks5"
  },
  "telegram": {
    "enabled": true,
    "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "123456789"
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
    "hidden_services": [
      "http://example.onion"
    ]
  }
}
```

## Usage

### Automatic Operation

Once installed, the scanner runs automatically every 2 hours via systemd timer.

### Manual Commands

```bash
# Check timer status
systemctl status darkmad.timer

# Check service status
systemctl status darkmad.service

# Run manual scan
systemctl start darkmad.service

# View real-time logs
journalctl -u darkmad.service -f

# View application logs
tail -f /var/log/darkmad/darkmad.log

# Stop automatic scanning
systemctl stop darkmad.timer

# Start automatic scanning
systemctl start darkmad.timer

# Disable automatic scanning
systemctl disable darkmad.timer
```

### Command-Line Usage

```bash
# Initialize configuration
python3 darkmad_hidden.py --init-config

# Run manual scan
python3 darkmad_hidden.py --scan

# Use custom config file
python3 darkmad_hidden.py --scan --config /path/to/config.json
```

## Reports

Reports are stored in `/opt/darkmad/reports/` with the following structure:

```
reports/
├── example_onion_20240101_120000.json
├── another_onion_20240101_140000.json
└── ...
```

### Report Format

Each report contains:
- URL of the hidden service
- Timestamp of scan
- HTTP status code
- Extracted credentials (if found)
- Additional metadata

Example report:

```json
{
  "url": "http://example.onion",
  "credentials": {
    "username": "admin",
    "password": "password123",
    "form_detected": true,
    "has_password_field": true
  },
  "timestamp": "2024-01-01T12:00:00",
  "status_code": 200
}
```

## Telegram Notifications

When credentials are found, you'll receive a Telegram message with:

```
🔐 New Credentials Found

Hidden Service: http://example.onion
Username: admin
Password: password123
Additional Info:
  • form_detected: true
  • has_password_field: true

Timestamp: 2024-01-01 12:00:00
```

## Security Considerations

### Systemd Security Features

The service runs with the following security restrictions:
- Runs as unprivileged user (`darkmad`)
- No privilege escalation (`NoNewPrivileges=true`)
- Private /tmp directory (`PrivateTmp=true`)
- Read-only system files (`ProtectSystem=strict`)
- Protected home directories (`ProtectHome=true`)
- Kernel protection enabled
- Namespace restrictions

### VPS Hardening Compatibility

The scanner is designed to work with hardened VPS environments:
- Respects SELinux/AppArmor policies
- Works with restrictive firewall rules
- Compatible with fail2ban and similar tools
- Minimal system footprint
- No kernel module dependencies

### Operational Security

- All traffic routed through Tor (when enabled)
- No credentials stored in plaintext logs
- Secure file permissions
- Regular log rotation recommended
- Network isolation capabilities

## Troubleshooting

### Tor Connection Issues

```bash
# Check if Tor is running
systemctl status tor

# Test Tor SOCKS proxy
curl --socks5 127.0.0.1:9050 https://check.torproject.org

# Restart Tor
systemctl restart tor
```

### Service Not Starting

```bash
# Check logs
journalctl -u darkmad.service -n 50

# Check permissions
ls -la /opt/darkmad
ls -la /var/log/darkmad

# Verify configuration
python3 /opt/darkmad/darkmad_hidden.py --config /opt/darkmad/config.json
```

### No Reports Generated

1. Check if targets are configured in `config.json`
2. Verify Tor is running and accessible
3. Check timeout settings
4. Review logs for errors

### Telegram Not Working

1. Verify bot token is correct
2. Check chat ID is correct
3. Ensure bot has permission to send messages
4. Test with `/start` command to your bot
5. Check Telegram is enabled in config

## Performance Tuning

### Adjust Scan Interval

Edit `/etc/systemd/system/darkmad.timer`:

```ini
[Timer]
OnBootSec=5min
OnUnitActiveSec=1h  # Change from 2h to 1h
```

Then reload:
```bash
systemctl daemon-reload
systemctl restart darkmad.timer
```

### Adjust Timeout and Retries

Edit `/opt/darkmad/config.json`:

```json
{
  "scanning": {
    "timeout": 60,
    "retry_attempts": 5
  }
}
```

## Monitoring

### Check Scanner Health

```bash
# Service status
systemctl status darkmad.service

# Timer status
systemctl status darkmad.timer

# Recent activity
journalctl -u darkmad.service --since "1 hour ago"

# Count reports
ls -l /opt/darkmad/reports/ | wc -l
```

### Log Rotation

Add log rotation configuration to `/etc/logrotate.d/darkmad`:

```
/var/log/darkmad/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 darkmad darkmad
}
```

## Uninstallation

```bash
# Stop and disable service
systemctl stop darkmad.timer
systemctl stop darkmad.service
systemctl disable darkmad.timer

# Remove systemd files
rm /etc/systemd/system/darkmad.service
rm /etc/systemd/system/darkmad.timer
systemctl daemon-reload

# Remove installation (optional - will delete reports!)
rm -rf /opt/darkmad
rm -rf /var/log/darkmad

# Remove user (optional)
userdel darkmad
```

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Disclaimer

This tool is for educational and authorized testing purposes only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before scanning any systems or networks. The authors are not responsible for misuse of this tool.

## Support

For issues, questions, or contributions, please refer to the project repository.

## Changelog

### Version 1.0.0 (Current)
- Initial production-ready release
- VPS deployment support
- Hidden services scanning
- Telegram notifications
- Systemd integration
- Automated 2-hour scanning
- Local report storage
- Security hardening features
