#!/bin/bash
# Uninstallation script for Skoda MQTT Bridge

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/myskoda-mqtt"
CONFIG_DIR="/etc/myskoda-mqtt"
LOG_DIR="/var/log/myskoda-mqtt"
SERVICE_NAME="myskoda-mqtt.service"

echo -e "${GREEN}=== Skoda MQTT Bridge Uninstallation ===${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Please run as root (use sudo)${NC}"
    exit 1
fi

# Stop and disable service
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}Stopping service...${NC}"
    systemctl stop $SERVICE_NAME
fi

if systemctl is-enabled --quiet $SERVICE_NAME; then
    echo -e "${GREEN}Disabling service...${NC}"
    systemctl disable $SERVICE_NAME
fi

# Remove systemd service file
if [ -f "/etc/systemd/system/$SERVICE_NAME" ]; then
    echo -e "${GREEN}Removing systemd service file...${NC}"
    rm /etc/systemd/system/$SERVICE_NAME
    systemctl daemon-reload
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${GREEN}Removing installation directory...${NC}"
    rm -rf "$INSTALL_DIR"
fi

# Ask about config and logs
read -p "Remove configuration directory ($CONFIG_DIR)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$CONFIG_DIR"
    echo -e "${GREEN}Configuration removed${NC}"
fi

read -p "Remove log directory ($LOG_DIR)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$LOG_DIR"
    echo -e "${GREEN}Logs removed${NC}"
fi

echo -e "${GREEN}=== Uninstallation Complete ===${NC}"

