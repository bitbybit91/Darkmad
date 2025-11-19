# DarkMad - Quick Start Guide

## Installation (One Command)
```bash
sudo ./install.sh
```

## Configuration (Essential Settings)
Edit `/opt/darkmad/config.json`:

```json
{
    "telegram": {
        "enabled": true,
        "bot_token": "GET_FROM_@BotFather",
        "chat_id": "GET_FROM_@userinfobot"
    },
    "targets": {
        "hidden_services": [
            "http://your-target.onion"
        ]
    }
}
```

## Essential Commands

| Action | Command |
|--------|---------|
| **Start scanning** | `sudo systemctl start darkmad.timer` |
| **Stop scanning** | `sudo systemctl stop darkmad.timer` |
| **Check status** | `sudo systemctl status darkmad.timer` |
| **View logs** | `sudo journalctl -u darkmad.service -f` |
| **Manual scan** | `sudo systemctl start darkmad.service` |
| **View reports** | `ls -lh /opt/darkmad/reports/` |

## File Locations

- **Config**: `/opt/darkmad/config.json`
- **Reports**: `/opt/darkmad/reports/`
- **Logs**: `/var/log/darkmad/`
- **Service**: `/etc/systemd/system/darkmad.service`

## Getting Telegram Bot Credentials

1. **Bot Token**: Message `@BotFather` → `/newbot` → Copy token
2. **Chat ID**: Message `@userinfobot` → `/start` → Copy ID
3. **Activate**: Search your bot → `/start`

## Default Behavior

- ✅ Scans every **2 hours**
- ✅ Uses **Tor proxy** (port 9050)
- ✅ Saves reports to **JSON files**
- ✅ Sends **Telegram notifications** when credentials found

## Verification

```bash
# 1. Check timer is active
systemctl is-active darkmad.timer

# 2. Check Tor is running
systemctl is-active tor

# 3. Test configuration
cat /opt/darkmad/config.json | jq .

# 4. Check reports directory
ls /opt/darkmad/reports/
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Service won't start | `journalctl -u darkmad.service -n 50` |
| No Telegram messages | Verify token and chat_id, send `/start` to bot |
| Can't reach .onion | Check `systemctl status tor` |
| No reports | Check targets in config.json |

## Next Steps

1. ✅ Install: `sudo ./install.sh`
2. ✅ Configure: `sudo nano /opt/darkmad/config.json`
3. ✅ Start: `sudo systemctl start darkmad.timer`
4. ✅ Monitor: `sudo journalctl -u darkmad.service -f`

For complete documentation, see `README_HIDDEN_SERVICES.md`
