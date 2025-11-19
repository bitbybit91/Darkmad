# DarkMad Deployment Checklist

Use this checklist to ensure proper deployment of DarkMad Hidden Services Scanner on your VPS.

## Pre-Deployment

### System Requirements
- [ ] Linux VPS (Debian/Ubuntu/CentOS/RHEL)
- [ ] Root or sudo access
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Minimum 512MB RAM
- [ ] 1GB free disk space
- [ ] Internet connectivity

### Dependencies Check
```bash
# Check Python
python3 --version

# Check pip
pip3 --version

# Check systemd
systemctl --version
```

## Installation

### Step 1: Download and Prepare
- [ ] Clone or download repository
- [ ] Navigate to project directory
- [ ] Make install script executable: `chmod +x install.sh`

### Step 2: Install Tor (if needed)
```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y tor

# CentOS/RHEL
sudo yum install -y tor

# Start and enable Tor
sudo systemctl enable tor
sudo systemctl start tor
```

- [ ] Tor installed
- [ ] Tor service running: `systemctl status tor`
- [ ] Verify Tor SOCKS proxy: `curl --socks5 127.0.0.1:9050 https://check.torproject.org`

### Step 3: Run Installation
```bash
sudo ./install.sh
```

- [ ] Installation completed without errors
- [ ] Service user created
- [ ] Directories created: `/opt/darkmad`, `/var/log/darkmad`
- [ ] Systemd service installed
- [ ] Python dependencies installed

## Configuration

### Step 4: Telegram Setup
- [ ] Create bot via @BotFather
  - Send `/newbot` to @BotFather
  - Follow prompts
  - **Save bot token**: `____________________`
  
- [ ] Get chat ID via @userinfobot
  - Send `/start` to @userinfobot
  - **Save chat ID**: `____________________`
  
- [ ] Start your bot
  - Search for your bot in Telegram
  - Send `/start` to activate

### Step 5: Edit Configuration
```bash
sudo nano /opt/darkmad/config.json
```

Update these fields:
- [ ] `telegram.bot_token`: Insert your bot token
- [ ] `telegram.chat_id`: Insert your chat ID
- [ ] `telegram.enabled`: Set to `true`
- [ ] `targets.hidden_services`: Add .onion URLs to scan

**Example configuration:**
```json
{
    "telegram": {
        "enabled": true,
        "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
        "chat_id": "123456789"
    },
    "targets": {
        "hidden_services": [
            "http://target1.onion",
            "http://target2.onion"
        ]
    }
}
```

- [ ] Configuration saved
- [ ] Configuration syntax valid: `cat /opt/darkmad/config.json | jq .`

### Step 6: Verify Permissions
```bash
# Check ownership
ls -la /opt/darkmad
ls -la /var/log/darkmad

# Should show: drwxr-x--- darkmad darkmad
```

- [ ] Correct ownership (darkmad:darkmad)
- [ ] Correct permissions (750 for directories)
- [ ] Config file readable by service user

## Testing

### Step 7: Manual Test
```bash
# Run single scan
sudo systemctl start darkmad.service

# Check status
systemctl status darkmad.service

# View logs
journalctl -u darkmad.service -n 50
```

- [ ] Service starts without errors
- [ ] Logs show scanning activity
- [ ] Reports generated in `/opt/darkmad/reports/`
- [ ] Telegram message received (if credentials found)

### Step 8: Verify Report Generation
```bash
# Check reports directory
ls -lh /opt/darkmad/reports/

# View latest report
cat $(ls -t /opt/darkmad/reports/*.json 2>/dev/null | head -1) | jq .
```

- [ ] Reports directory exists
- [ ] Reports are being generated
- [ ] Reports contain expected data

## Activation

### Step 9: Enable Automatic Scanning
```bash
# Enable timer
sudo systemctl enable darkmad.timer

# Start timer
sudo systemctl start darkmad.timer

# Verify timer is active
systemctl status darkmad.timer
```

- [ ] Timer enabled
- [ ] Timer active and running
- [ ] Next execution time displayed

### Step 10: Verify Timer Schedule
```bash
# List all timers
systemctl list-timers --all | grep darkmad
```

- [ ] Timer shows in list
- [ ] "Next" time is displayed (within 2 hours)
- [ ] "Left" shows time until next run

## Monitoring

### Step 11: Set Up Monitoring
```bash
# Create monitoring script (optional)
cat > /usr/local/bin/check_darkmad.sh << 'EOF'
#!/bin/bash
echo "=== DarkMad Status ==="
systemctl status darkmad.timer | grep Active
echo ""
echo "=== Last 5 Reports ==="
ls -lht /opt/darkmad/reports/ | head -6
echo ""
echo "=== Recent Logs ==="
journalctl -u darkmad.service --since "1 hour ago" --no-pager | tail -10
EOF

chmod +x /usr/local/bin/check_darkmad.sh
```

- [ ] Monitoring script created
- [ ] Test monitoring: `/usr/local/bin/check_darkmad.sh`

### Step 12: Configure Log Rotation
```bash
# Create logrotate config
sudo tee /etc/logrotate.d/darkmad << 'EOF'
/var/log/darkmad/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 darkmad darkmad
}
EOF
```

- [ ] Log rotation configured
- [ ] Test logrotate: `sudo logrotate -d /etc/logrotate.d/darkmad`

## Security Hardening

### Step 13: Additional Security (Optional)
```bash
# Restrict directory access
sudo chmod 750 /opt/darkmad
sudo chmod 640 /opt/darkmad/config.json

# Set up firewall (if using UFW)
sudo ufw allow from 127.0.0.1 to any port 9050 # Tor SOCKS

# Enable fail2ban for SSH (if not already)
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

- [ ] Directory permissions restricted
- [ ] Config file protected (640)
- [ ] Firewall configured (if applicable)
- [ ] Fail2ban enabled (optional)

### Step 14: Backup Configuration
```bash
# Create backup
sudo cp /opt/darkmad/config.json /opt/darkmad/config.json.backup
sudo chmod 600 /opt/darkmad/config.json.backup
```

- [ ] Configuration backed up
- [ ] Backup secured

## Post-Deployment

### Step 15: Document Your Deployment
Record the following information in a secure location:

- **VPS IP**: `____________________`
- **Installation Date**: `____________________`
- **Telegram Bot Name**: `____________________`
- **Telegram Bot Token**: `____________________` (keep secure!)
- **Telegram Chat ID**: `____________________`
- **Number of Targets**: `____________________`
- **Scan Interval**: `2 hours (default)`

### Step 16: Set Up Alerts
```bash
# Create daily summary script (optional)
cat > /opt/darkmad/daily_summary.sh << 'EOF'
#!/bin/bash
COUNT=$(find /opt/darkmad/reports -name "*.json" -mtime -1 | wc -l)
echo "DarkMad Daily Summary: $COUNT reports generated in last 24 hours"
EOF

chmod +x /opt/darkmad/daily_summary.sh

# Add to crontab for daily email
# sudo crontab -e
# 0 9 * * * /opt/darkmad/daily_summary.sh | mail -s "DarkMad Daily Report" admin@example.com
```

- [ ] Summary script created (optional)
- [ ] Email alerts configured (optional)

### Step 17: Final Verification
```bash
# Run complete check
echo "1. Service Status"
systemctl is-active darkmad.timer

echo "2. Tor Status"
systemctl is-active tor

echo "3. Recent Activity"
journalctl -u darkmad.service --since "1 hour ago" --no-pager | tail -5

echo "4. Reports Count"
ls /opt/darkmad/reports/*.json 2>/dev/null | wc -l

echo "5. Next Scan"
systemctl list-timers | grep darkmad
```

- [ ] All services active
- [ ] Reports being generated
- [ ] Telegram notifications working
- [ ] Logs showing normal activity

## Maintenance Schedule

### Daily
- [ ] Check Telegram for alerts
- [ ] Verify scanner is running: `systemctl status darkmad.timer`

### Weekly
- [ ] Review logs: `journalctl -u darkmad.service --since "1 week ago"`
- [ ] Check disk space: `df -h /opt/darkmad`
- [ ] Review report count: `ls /opt/darkmad/reports/ | wc -l`

### Monthly
- [ ] Update Python packages: `pip3 install --upgrade requests urllib3`
- [ ] Review and clean old reports
- [ ] Update targets list if needed
- [ ] Verify Tor is up to date: `apt-get upgrade tor`

## Troubleshooting Reference

### Service Won't Start
```bash
journalctl -u darkmad.service -n 50
sudo systemctl restart darkmad.service
```

### No Telegram Messages
```bash
# Test bot
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# Verify config
cat /opt/darkmad/config.json | jq .telegram
```

### Tor Connection Issues
```bash
systemctl restart tor
curl --socks5 127.0.0.1:9050 https://check.torproject.org
```

### Check Disk Space
```bash
df -h /opt/darkmad
du -sh /opt/darkmad/reports
```

## Emergency Procedures

### Stop Scanning Immediately
```bash
sudo systemctl stop darkmad.timer
sudo systemctl stop darkmad.service
```

### Backup and Remove
```bash
# Backup reports
sudo tar -czf darkmad-reports-$(date +%Y%m%d).tar.gz /opt/darkmad/reports/

# Stop and disable
sudo systemctl stop darkmad.timer
sudo systemctl disable darkmad.timer

# Remove (careful!)
# sudo rm -rf /opt/darkmad
# sudo rm /etc/systemd/system/darkmad.*
# sudo systemctl daemon-reload
```

## Deployment Complete! ✅

Date: _______________
Deployed by: _______________
Verified by: _______________

**Notes:**
_______________________________________
_______________________________________
_______________________________________
