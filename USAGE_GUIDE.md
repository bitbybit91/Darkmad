# DarkMad Hidden Services Scanner - Quick Usage Guide

## Quick Start (3 Steps)

### 1. Install
```bash
# As root
sudo ./install.sh
```

### 2. Configure
```bash
# Edit configuration
sudo nano /opt/darkmad/config.json
```

Add your settings:
- **Tor proxy**: Usually works with defaults if Tor is installed
- **Telegram bot**: Get token from @BotFather, chat ID from @userinfobot
- **Targets**: Add .onion URLs to scan

### 3. Start
```bash
# Enable automatic scanning (every 2 hours)
sudo systemctl start darkmad.timer

# Or run one-time manual scan
sudo systemctl start darkmad.service
```

## Configuration Template

Copy this into `/opt/darkmad/config.json`:

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
        "bot_token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
    },
    "targets": {
        "hidden_services": [
            "http://your-target.onion"
        ]
    }
}
```

## Getting Telegram Credentials

### Step 1: Create Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow prompts to create your bot
4. Copy the bot token (format: `1234567890:ABCdef...`)

### Step 2: Get Chat ID
1. Search for `@userinfobot` in Telegram
2. Send `/start`
3. Copy your user ID (the chat_id)

### Step 3: Start Your Bot
1. Search for your bot in Telegram
2. Send `/start` to activate it

## Common Commands

```bash
# Check if service is running
systemctl status darkmad.timer
systemctl status darkmad.service

# View live logs
journalctl -u darkmad.service -f

# View application log
tail -f /var/log/darkmad/darkmad.log

# Manual scan
systemctl start darkmad.service

# Stop automatic scanning
systemctl stop darkmad.timer

# Restart service
systemctl restart darkmad.service
```

## Checking Reports

Reports are saved in `/opt/darkmad/reports/`:

```bash
# List all reports
ls -lh /opt/darkmad/reports/

# View latest report
cat $(ls -t /opt/darkmad/reports/*.json | head -1) | jq .

# Count reports
ls /opt/darkmad/reports/*.json | wc -l
```

## Troubleshooting

### Issue: Service won't start
```bash
# Check logs
journalctl -u darkmad.service -n 50

# Verify Tor is running
systemctl status tor
```

### Issue: No Telegram notifications
```bash
# Test bot token
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Verify config
cat /opt/darkmad/config.json | jq .telegram
```

### Issue: Tor connection fails
```bash
# Check Tor service
systemctl status tor

# Test Tor proxy
curl --socks5 127.0.0.1:9050 https://check.torproject.org

# Restart Tor
systemctl restart tor
```

### Issue: No targets being scanned
```bash
# Check configuration
cat /opt/darkmad/config.json | jq .targets

# Ensure targets array is not empty
```

## Security Notes

1. **Keep config secure**: Contains sensitive tokens
   ```bash
   chmod 640 /opt/darkmad/config.json
   chown darkmad:darkmad /opt/darkmad/config.json
   ```

2. **Protect reports**: May contain credentials
   ```bash
   chmod 750 /opt/darkmad/reports
   chown -R darkmad:darkmad /opt/darkmad/reports
   ```

3. **Regular cleanup**: Remove old reports
   ```bash
   # Delete reports older than 30 days
   find /opt/darkmad/reports -name "*.json" -mtime +30 -delete
   ```

## Changing Scan Interval

Default is 2 hours. To change:

```bash
# Edit timer
sudo nano /etc/systemd/system/darkmad.timer
```

Change `OnUnitActiveSec=2h` to desired interval:
- `1h` = hourly
- `30m` = every 30 minutes
- `4h` = every 4 hours

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart darkmad.timer
```

## Uninstallation

```bash
# Stop service
sudo systemctl stop darkmad.timer
sudo systemctl disable darkmad.timer

# Remove files
sudo rm -rf /opt/darkmad
sudo rm -rf /var/log/darkmad
sudo rm /etc/systemd/system/darkmad.service
sudo rm /etc/systemd/system/darkmad.timer
sudo systemctl daemon-reload

# Remove user (optional)
sudo userdel darkmad
```

## Advanced Configuration

### Custom Timeout
Increase for slow .onion sites:
```json
{
    "scanning": {
        "timeout": 60,
        "retry_attempts": 5
    }
}
```

### Multiple Scanners
Run multiple instances with different configs:
```bash
# Copy and modify service files
cp /etc/systemd/system/darkmad.service /etc/systemd/system/darkmad2.service
# Edit to use different config path
# Enable both services
```

### Log Rotation
Create `/etc/logrotate.d/darkmad`:
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

## Support & Resources

- Full documentation: See `README_HIDDEN_SERVICES.md`
- Tor Project: https://www.torproject.org/
- Telegram Bots: https://core.telegram.org/bots

## Legal Notice

This tool is for authorized security testing only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before scanning any systems.
