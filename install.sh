#!/bin/bash
#
# DarkMad Installation Script for VPS
# This script installs DarkMad as a systemd service for automatic scanning
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/darkmad"
LOG_DIR="/var/log/darkmad"
SERVICE_USER="darkmad"
SERVICE_GROUP="darkmad"

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}DarkMad Installation Script${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root${NC}"
   exit 1
fi

# Check for required commands
echo -e "${YELLOW}Checking system requirements...${NC}"
for cmd in python3 pip3 systemctl; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}Error: $cmd is not installed${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ System requirements met${NC}"

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip3 install requests[socks] urllib3 --quiet
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo -e "${YELLOW}Creating service user: $SERVICE_USER${NC}"
    useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
    echo -e "${GREEN}✓ Service user created${NC}"
else
    echo -e "${GREEN}✓ Service user already exists${NC}"
fi

# Create installation directory
echo -e "${YELLOW}Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/reports"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ Directories created${NC}"

# Copy files
echo -e "${YELLOW}Copying files...${NC}"
cp darkmad_hidden.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/darkmad_hidden.py"

# Create or update config
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo -e "${YELLOW}Creating default configuration...${NC}"
    python3 "$INSTALL_DIR/darkmad_hidden.py" --init-config --config "$INSTALL_DIR/config.json"
    echo -e "${GREEN}✓ Configuration created${NC}"
else
    echo -e "${GREEN}✓ Configuration already exists (not overwriting)${NC}"
fi

# Set permissions
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"
chmod 750 "$INSTALL_DIR"
chmod 640 "$INSTALL_DIR/config.json"
chmod 750 "$LOG_DIR"
echo -e "${GREEN}✓ Permissions set${NC}"

# Install systemd service
echo -e "${YELLOW}Installing systemd service...${NC}"
cp darkmad.service /etc/systemd/system/
cp darkmad.timer /etc/systemd/system/
systemctl daemon-reload
echo -e "${GREEN}✓ Systemd service installed${NC}"

# Enable and start timer
echo -e "${YELLOW}Enabling and starting timer...${NC}"
systemctl enable darkmad.timer
systemctl start darkmad.timer
echo -e "${GREEN}✓ Timer enabled and started${NC}"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Installation directory: ${YELLOW}$INSTALL_DIR${NC}"
echo -e "Log directory: ${YELLOW}$LOG_DIR${NC}"
echo -e "Reports directory: ${YELLOW}$INSTALL_DIR/reports${NC}"
echo -e "Configuration file: ${YELLOW}$INSTALL_DIR/config.json${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Edit configuration: ${GREEN}nano $INSTALL_DIR/config.json${NC}"
echo -e "   - Configure Tor proxy settings (if using Tor)"
echo -e "   - Add your Telegram bot token and chat ID"
echo -e "   - Add hidden service URLs to scan"
echo ""
echo -e "2. Check timer status: ${GREEN}systemctl status darkmad.timer${NC}"
echo -e "3. View logs: ${GREEN}journalctl -u darkmad.service -f${NC}"
echo -e "4. Manual scan: ${GREEN}systemctl start darkmad.service${NC}"
echo ""
echo -e "${YELLOW}The scanner will run automatically every 2 hours${NC}"
echo ""

# Check if Tor is installed
if ! command -v tor &> /dev/null; then
    echo -e "${YELLOW}Warning: Tor is not installed${NC}"
    echo -e "To scan .onion sites, install Tor:"
    echo -e "  ${GREEN}apt-get install tor${NC}  (Debian/Ubuntu)"
    echo -e "  ${GREEN}yum install tor${NC}      (CentOS/RHEL)"
    echo -e "Then start it: ${GREEN}systemctl start tor${NC}"
    echo ""
fi

exit 0
