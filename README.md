# Skoda Enyaq MQTT Bridge

A Python-based bridge that connects Skoda Enyaq vehicles to Home Assistant via MQTT. This service publishes vehicle state (battery level, charging status, range, etc.) and accepts commands (start/stop charging, lock/unlock) through MQTT topics.

## Why systemd instead of Docker?

This project intentionally uses **systemd** instead of Docker for the following reasons:

- **Home Assistant Supervised networking complexity**: When running Home Assistant in Supervised mode, Docker networking between external containers and Home Assistant add-ons (like Mosquitto) can be problematic
- **Local MQTT broker**: The MQTT broker runs locally (127.0.0.1) as a Home Assistant add-on
- **No external ports needed**: This is a simple bridge service with no HTTP endpoints or external access requirements
- **Simpler debugging**: Using `journalctl` is more straightforward than Docker logs in this context
- **No scaling requirements**: This is a single-instance service tied to one vehicle
- **More stable**: Avoids Docker networking issues in Home Assistant Supervised setups

If you're running Home Assistant in Container or Core mode, or have a different setup, Docker might work fine for you. But for Supervised mode with local Mosquitto, systemd is the recommended approach.

## Features

- ✅ Publishes vehicle state to MQTT topics
  - Battery state of charge (SOC)
  - Remaining range
  - Charging status
  - Plugged-in status
  - Door lock status
- ✅ Accepts commands via MQTT
  - Start/stop charging
  - Lock/unlock vehicle
- ✅ Home Assistant MQTT Discovery support
- ✅ Automatic token refresh
- ✅ Configurable polling interval with rate limiting
- ✅ Runs as systemd service for reliability
- ✅ Comprehensive logging via journald

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Skoda Connect  │ ◄─────► │  MQTT Bridge     │ ◄─────► │  MQTT Broker    │
│  API            │  HTTPS  │  (systemd)       │  MQTT   │  (Mosquitto)    │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                                                   │
                                                                   │ MQTT
                                                                   ▼
                                                          ┌─────────────────┐
                                                          │ Home Assistant  │
                                                          └─────────────────┘
```

The bridge:
1. Authenticates with Skoda Connect API
2. Polls vehicle status at configurable intervals (default: 5 minutes)
3. Publishes state to MQTT topics
4. Listens for commands on MQTT command topics
5. Executes commands via Skoda Connect API
6. Immediately updates state after command execution

## Requirements

- Python 3.10 or higher
- Home Assistant (any installation method)
- Mosquitto MQTT broker (or any MQTT broker)
- Skoda Connect account with registered vehicle
- Linux system with systemd (tested on Debian/Ubuntu)

## Installation

### 1. Clone the repository

```bash
cd /opt
sudo git clone https://github.com/mikitu/myskoda-mqtt.git
cd myskoda-mqtt
```

### 2. Run the installation script

```bash
sudo ./scripts/install.sh
```

This script will:
- Install Python dependencies using `apt` (for externally-managed Python environments)
- Create necessary directories
- Copy application files to `/opt/myskoda-mqtt`
- Install systemd service
- Create example configuration file

### 3. Configure the service

Edit the configuration file:

```bash
sudo nano /etc/myskoda-mqtt/config.json
```

Required settings:
```json
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
```

### 4. Start the service

```bash
# Enable service to start on boot
sudo systemctl enable myskoda-mqtt.service

# Start the service
sudo systemctl start myskoda-mqtt.service

# Check status
sudo systemctl status myskoda-mqtt.service

# View logs
sudo journalctl -u myskoda-mqtt.service -f
```

## Configuration Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `skoda_username` | Skoda Connect email | - | Yes |
| `skoda_password` | Skoda Connect password | - | Yes |
| `skoda_vin` | Vehicle Identification Number | - | Yes |
| `mqtt_broker` | MQTT broker address | `127.0.0.1` | No |
| `mqtt_port` | MQTT broker port | `1883` | No |
| `mqtt_username` | MQTT username | - | No |
| `mqtt_password` | MQTT password | - | No |
| `mqtt_topic_prefix` | Prefix for all MQTT topics | `skoda/enyaq` | No |
| `poll_interval` | Polling interval in seconds | `300` (5 min) | No |
| `command_timeout` | Command timeout in seconds | `30` | No |
| `ha_discovery` | Enable HA MQTT Discovery | `true` | No |
| `ha_discovery_prefix` | HA discovery prefix | `homeassistant` | No |
| `device_name` | Device name in Home Assistant | `Skoda Enyaq` | No |
| `device_manufacturer` | Device manufacturer | `Skoda` | No |
| `device_model` | Device model | `Enyaq iV` | No |
| `log_level` | Logging level | `INFO` | No |

## Home Assistant Integration

### Automatic MQTT Discovery

This bridge uses **Home Assistant MQTT Discovery** to automatically create all entities. **No manual configuration is required** - just start the service and the entities will appear in Home Assistant.

### Entities Created Automatically

When the bridge starts, it automatically creates the following entities in Home Assistant:

**Sensors:**
- `sensor.skoda_enyaq_battery_level` - Battery state of charge (%)
- `sensor.skoda_enyaq_range` - Estimated range (km)

**Binary Sensors:**
- `binary_sensor.skoda_enyaq_charging` - Charging status
- `binary_sensor.skoda_enyaq_plugged_in` - Plugged in status

**Buttons:**
- `button.skoda_enyaq_start_charging` - Start charging
- `button.skoda_enyaq_stop_charging` - Stop charging
- `button.skoda_enyaq_lock_vehicle` - Lock vehicle
- `button.skoda_enyaq_unlock_vehicle` - Unlock vehicle

All entities will appear under **Settings → Devices & Services → MQTT → Devices → Skoda Enyaq** in Home Assistant.

### How It Works

1. The bridge publishes vehicle state as a single JSON payload to `skoda/enyaq/state`
2. Home Assistant MQTT Discovery configurations are published on startup
3. Home Assistant automatically creates entities based on these configurations
4. Entities use JSON templates to extract values from the state payload
5. All entities show as "Unavailable" when the bridge is offline

## MQTT Topics

See [MQTT_TOPICS.md](docs/MQTT_TOPICS.md) for detailed topic documentation.

### State Topic

- `skoda/enyaq/state` - Complete vehicle state as JSON (retained)
- `skoda/enyaq/availability` - Bridge availability (online/offline)

### Command Topics

- `skoda/enyaq/cmd/start_charging` - Start charging
- `skoda/enyaq/cmd/stop_charging` - Stop charging
- `skoda/enyaq/cmd/lock` - Lock vehicle
- `skoda/enyaq/cmd/unlock` - Unlock vehicle

## Security Considerations

See [SECURITY.md](docs/SECURITY.md) for detailed security information.

**Important security notes:**

1. **Credentials**: Store configuration file with restricted permissions (600)
2. **Rate limiting**: Default 5-minute polling interval to avoid API rate limits
3. **Token management**: Tokens are automatically refreshed and stored in memory only
4. **MQTT security**: Use MQTT authentication and consider TLS for production
5. **Network**: Keep MQTT broker on local network, do not expose to internet
6. **Risks**: This bridge can control your vehicle - secure your Home Assistant instance

## Troubleshooting

### Service won't start

```bash
# Check service status
sudo systemctl status myskoda-mqtt.service

# View detailed logs
sudo journalctl -u myskoda-mqtt.service -n 50
```

### MQTT connection issues

- Verify MQTT broker is running: `sudo systemctl status mosquitto`
- Check MQTT credentials in config
- Test MQTT connection: `mosquitto_sub -h 127.0.0.1 -t 'skoda/#' -u username -P password`

### API authentication failures

- Verify Skoda Connect credentials
- Check if VIN is correct
- Ensure account has access to the vehicle

### Python dependency issues

If you encounter `externally-managed-environment` errors:

```bash
# Use apt to install dependencies
sudo apt install python3-requests python3-paho-mqtt
```

## Uninstallation

```bash
cd /opt/myskoda-mqtt
sudo ./scripts/uninstall.sh
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Skoda Auto or Volkswagen Group. Use at your own risk. The authors are not responsible for any damage to your vehicle or account.

## Acknowledgments

- Home Assistant community
- Skoda Connect API reverse engineering efforts

