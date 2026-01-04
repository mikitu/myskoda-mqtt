# Quick Start Guide

Get your Skoda Enyaq connected to Home Assistant in 10 minutes!

## Prerequisites

- ✅ Home Assistant running (any installation method)
- ✅ Mosquitto MQTT broker installed and running
- ✅ Skoda Connect account with registered vehicle
- ✅ Linux system with systemd (Debian/Ubuntu recommended)
- ✅ Root/sudo access

## Step 1: Install (2 minutes)

```bash
# Clone the repository
cd /opt
sudo git clone https://github.com/mikitu/myskoda-mqtt.git
cd myskoda-mqtt

# Run installation script
sudo ./scripts/install.sh
```

The script will:
- Install Python dependencies
- Create directories
- Install systemd service
- Create example config file

## Step 2: Configure (3 minutes)

Edit the configuration file:

```bash
sudo nano /etc/myskoda-mqtt/config.json
```

**Minimum required settings:**

```json
{
  "skoda_username": "your-email@example.com",
  "skoda_password": "your-skoda-password",
  "skoda_vin": "TMBJJ7NE0N0123456",
  "mqtt_username": "your-mqtt-user",
  "mqtt_password": "your-mqtt-password"
}
```

**Where to find your VIN:**
- Skoda Connect mobile app
- Vehicle registration documents
- Dashboard (visible through windshield)
- Driver's side door frame

Save and exit (Ctrl+X, Y, Enter).

## Step 3: Start the Service (1 minute)

```bash
# Enable service to start on boot
sudo systemctl enable myskoda-mqtt.service

# Start the service
sudo systemctl start myskoda-mqtt.service

# Check status
sudo systemctl status myskoda-mqtt.service
```

You should see: `Active: active (running)`

## Step 4: Verify MQTT Messages (2 minutes)

Open a new terminal and subscribe to MQTT topics:

```bash
mosquitto_sub -h 127.0.0.1 -t 'skoda/#' -v -u your-mqtt-user -P your-mqtt-password
```

You should see messages like:
```
skoda/enyaq/availability online
skoda/enyaq/battery/soc 75
skoda/enyaq/battery/range 280
skoda/enyaq/battery/charging OFF
skoda/enyaq/battery/plugged_in ON
skoda/enyaq/doors/locked LOCKED
```

If you don't see messages, check the logs:
```bash
sudo journalctl -u myskoda-mqtt.service -f
```

## Step 5: Check Home Assistant (2 minutes)

If Home Assistant MQTT Discovery is enabled (default), entities should appear automatically.

1. Go to **Settings** → **Devices & Services**
2. Click on **MQTT** integration
3. You should see a **Skoda Enyaq** device
4. Click on it to see all entities:
   - Battery Level sensor
   - Range sensor
   - Charging binary sensor
   - Plugged In binary sensor
   - Door Lock

**If entities don't appear:**
- Make sure MQTT integration is configured in Home Assistant
- Check that `ha_discovery: true` in config.json
- Restart the bridge: `sudo systemctl restart myskoda-mqtt.service`

## Step 6: Test Commands (Optional)

Try sending a command:

```bash
# Lock the vehicle
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/command/lock' -m 'LOCK' -u your-mqtt-user -P your-mqtt-password

# Start charging (if plugged in)
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/command/start_charging' -m 'START' -u your-mqtt-user -P your-mqtt-password
```

Check the logs to see command execution:
```bash
sudo journalctl -u myskoda-mqtt.service -f
```

## You're Done! 🎉

Your Skoda Enyaq is now connected to Home Assistant via MQTT!

## Next Steps

### Create Automations

Example: Notify when charging completes

```yaml
automation:
  - alias: "Notify when Enyaq charging complete"
    trigger:
      - platform: state
        entity_id: binary_sensor.charging
        from: "on"
        to: "off"
    condition:
      - condition: state
        entity_id: binary_sensor.plugged_in
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Enyaq charging complete! Battery at {{ states('sensor.battery_level') }}%"
```

### Create Dashboard Cards

Example: Battery status card

```yaml
type: entities
title: Skoda Enyaq
entities:
  - entity: sensor.battery_level
    name: Battery
  - entity: sensor.range
    name: Range
  - entity: binary_sensor.charging
    name: Charging
  - entity: binary_sensor.plugged_in
    name: Plugged In
  - entity: lock.door_lock
    name: Doors
```

### Optimize Settings

Edit `/etc/myskoda-mqtt/config.json`:

- **Reduce polling**: Increase `poll_interval` to 600 (10 minutes) to reduce API calls
- **Adjust logging**: Set `log_level` to `WARNING` for less verbose logs
- **Customize topics**: Change `mqtt_topic_prefix` if you have multiple vehicles

After changes, restart:
```bash
sudo systemctl restart myskoda-mqtt.service
```

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u myskoda-mqtt.service -n 50
```
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions.

### No MQTT messages
- Check Mosquitto is running: `sudo systemctl status mosquitto`
- Verify MQTT credentials
- Check logs for errors

### Authentication failed
- Verify Skoda Connect credentials
- Try logging in to Skoda Connect app/website
- Check VIN is correct

## Useful Commands

```bash
# View logs
sudo journalctl -u myskoda-mqtt.service -f

# Restart service
sudo systemctl restart myskoda-mqtt.service

# Stop service
sudo systemctl stop myskoda-mqtt.service

# Check status
sudo systemctl status myskoda-mqtt.service

# Edit config
sudo nano /etc/myskoda-mqtt/config.json
```

## Getting Help

- 📖 [Full Documentation](../README.md)
- 🔧 [Troubleshooting Guide](TROUBLESHOOTING.md)
- 🔒 [Security Guide](SECURITY.md)
- 📡 [MQTT Topics Reference](MQTT_TOPICS.md)
- 🐛 [Report Issues](https://github.com/mikitu/myskoda-mqtt/issues)

## What's Next?

Now that your vehicle is connected, you can:

- Create automations based on battery level
- Get notifications when charging starts/stops
- Track charging costs with energy monitoring
- Create schedules for charging
- Monitor range and plan trips
- Integrate with other smart home devices

Enjoy your connected Skoda Enyaq! 🚗⚡

