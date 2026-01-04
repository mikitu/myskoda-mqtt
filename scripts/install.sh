#!/bin/bash
# Installation script for Skoda MQTT Bridge
# This script installs the bridge as a systemd service

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
SERVICE_FILE="systemd/myskoda-mqtt.service"
SERVICE_NAME="myskoda-mqtt.service"
USER="homeassistant"
GROUP="homeassistant"

echo -e "${GREEN}=== Skoda MQTT Bridge Installation ===${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Please run as root (use sudo)${NC}"
    exit 1
fi

# Check if user exists, create if not
if ! id "$USER" &>/dev/null; then
    echo -e "${YELLOW}Creating user $USER...${NC}"
    useradd -r -s /bin/false $USER
fi

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
echo -e "${YELLOW}Note: Using apt for externally-managed Python environment${NC}"

# Try apt first (Debian/Ubuntu with externally-managed Python)
if command -v apt &> /dev/null; then
    apt update
    apt install -y python3 python3-requests python3-paho-mqtt
else
    echo -e "${YELLOW}Warning: apt not found. You may need to install dependencies manually:${NC}"
    echo "  - python3-requests"
    echo "  - python3-paho-mqtt"
fi

# Create directories
echo -e "${GREEN}Creating directories...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"

# Copy application files
echo -e "${GREEN}Copying application files...${NC}"
cp -r myskoda_mqtt "$INSTALL_DIR/"

# Set permissions
echo -e "${GREEN}Setting permissions...${NC}"
chown -R $USER:$GROUP "$INSTALL_DIR"
chown -R $USER:$GROUP "$LOG_DIR"
chmod 755 "$INSTALL_DIR"

# Copy systemd service file
echo -e "${GREEN}Installing systemd service...${NC}"
cp "$SERVICE_FILE" /etc/systemd/system/
chmod 644 /etc/systemd/system/$SERVICE_NAME

# Create example config if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo -e "${GREEN}Creating example configuration...${NC}"
    cat > "$CONFIG_DIR/config.json" << 'EOF'
{
  "skoda_username": "your-email@example.com",
  "skoda_password": "your-password",
  "skoda_vin": "YOUR-VIN-HERE",
  "mqtt_broker": "127.0.0.1",
  "mqtt_port": 1883,
  "mqtt_username": "mqtt-user",
  "mqtt_password": "mqtt-password",
  "mqtt_topic_prefix": "skoda/enyaq",
  "poll_interval": 300,
  "ha_discovery": true,
  "ha_discovery_prefix": "homeassistant",
  "log_level": "INFO"
}
EOF
    chmod 600 "$CONFIG_DIR/config.json"
    chown $USER:$GROUP "$CONFIG_DIR/config.json"
    echo -e "${YELLOW}Configuration file created at $CONFIG_DIR/config.json${NC}"
    echo -e "${YELLOW}Please edit this file with your credentials before starting the service${NC}"
fi

# Reload systemd
echo -e "${GREEN}Reloading systemd...${NC}"
systemctl daemon-reload

echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit configuration: sudo nano $CONFIG_DIR/config.json"
echo "2. Enable service: sudo systemctl enable $SERVICE_NAME"
echo "3. Start service: sudo systemctl start $SERVICE_NAME"
echo "4. Check status: sudo systemctl status $SERVICE_NAME"
echo "5. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo -e "${GREEN}Installation successful!${NC}"

