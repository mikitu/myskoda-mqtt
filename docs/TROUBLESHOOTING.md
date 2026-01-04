# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Skoda MQTT Bridge.

## Quick Diagnostics

### Check Service Status

```bash
# Check if service is running
sudo systemctl status myskoda-mqtt.service

# View recent logs
sudo journalctl -u myskoda-mqtt.service -n 50

# Follow logs in real-time
sudo journalctl -u myskoda-mqtt.service -f
```

### Check MQTT Broker

```bash
# Check if Mosquitto is running
sudo systemctl status mosquitto

# Test MQTT connection
mosquitto_sub -h 127.0.0.1 -t 'skoda/#' -v -u username -P password
```

### Check Configuration

```bash
# Verify config file exists and has correct permissions
ls -la /etc/myskoda-mqtt/config.json

# Should show: -rw------- 1 homeassistant homeassistant
```

## Common Issues

### Service Won't Start

**Symptom**: `systemctl start myskoda-mqtt.service` fails

**Diagnosis**:
```bash
sudo journalctl -u myskoda-mqtt.service -n 50
```

**Common causes**:

1. **Missing configuration file**
   ```
   Error: [Errno 2] No such file or directory: '/etc/myskoda-mqtt/config.json'
   ```
   **Solution**: Create config file from example
   ```bash
   sudo cp config.example.json /etc/myskoda-mqtt/config.json
   sudo nano /etc/myskoda-mqtt/config.json
   sudo chmod 600 /etc/myskoda-mqtt/config.json
   sudo chown homeassistant:homeassistant /etc/myskoda-mqtt/config.json
   ```

2. **Invalid JSON in config**
   ```
   Error: Expecting property name enclosed in double quotes
   ```
   **Solution**: Validate JSON syntax
   ```bash
   python3 -m json.tool /etc/myskoda-mqtt/config.json
   ```

3. **Missing required fields**
   ```
   ValueError: Missing required configuration: skoda_username, skoda_password
   ```
   **Solution**: Add all required fields to config.json

4. **Python dependencies missing**
   ```
   ModuleNotFoundError: No module named 'paho'
   ```
   **Solution**: Install dependencies
   ```bash
   sudo apt install python3-requests python3-paho-mqtt
   ```

### MQTT Connection Fails

**Symptom**: Logs show "Failed to connect to MQTT broker"

**Diagnosis**:
```bash
# Check if Mosquitto is running
sudo systemctl status mosquitto

# Check Mosquitto logs
sudo journalctl -u mosquitto -n 50

# Test connection manually
mosquitto_pub -h 127.0.0.1 -t 'test' -m 'hello' -u username -P password
```

**Common causes**:

1. **Mosquitto not running**
   ```bash
   sudo systemctl start mosquitto
   sudo systemctl enable mosquitto
   ```

2. **Wrong broker address**
   - Check `mqtt_broker` in config.json
   - For Home Assistant add-on: use `127.0.0.1` or `localhost`

3. **Authentication failure**
   ```
   Connection refused: not authorised
   ```
   **Solution**: Verify MQTT credentials
   ```bash
   # Test with credentials
   mosquitto_pub -h 127.0.0.1 -t 'test' -m 'hello' -u your-user -P your-pass
   ```

4. **Port already in use**
   ```bash
   # Check what's using port 1883
   sudo netstat -tlnp | grep 1883
   ```

### Skoda API Authentication Fails

**Symptom**: Logs show "Authentication failed" or "Failed to authenticate"

**Common causes**:

1. **Wrong credentials**
   - Verify username/password in config.json
   - Try logging in to Skoda Connect website/app

2. **Account locked**
   - Too many failed login attempts
   - Wait 30 minutes and try again

3. **VIN incorrect**
   - Check VIN in config.json
   - Find VIN in Skoda Connect app or vehicle registration

4. **API endpoint changed**
   - Skoda may have updated their API
   - Check for project updates

### No Data Published to MQTT

**Symptom**: Service running but no MQTT messages

**Diagnosis**:
```bash
# Subscribe to all topics
mosquitto_sub -h 127.0.0.1 -t 'skoda/#' -v -u username -P password

# Check service logs
sudo journalctl -u myskoda-mqtt.service -f
```

**Common causes**:

1. **Not connected to MQTT**
   - Check logs for "Connected to MQTT broker successfully"
   - See "MQTT Connection Fails" section above

2. **API errors**
   - Check logs for "Failed to get vehicle status"
   - May be temporary API issue - wait and retry

3. **Wrong topic prefix**
   - Check `mqtt_topic_prefix` in config.json
   - Subscribe to correct prefix

### Commands Not Working

**Symptom**: Publishing to command topics has no effect

**Diagnosis**:
```bash
# Check if bridge is subscribed
mosquitto_sub -h 127.0.0.1 -t 'skoda/enyaq/command/#' -v

# Publish test command
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/command/start_charging' -m 'START'

# Watch logs
sudo journalctl -u myskoda-mqtt.service -f
```

**Common causes**:

1. **Not subscribed to command topics**
   - Check logs for "Subscribed to skoda/enyaq/command/#"
   - Restart service if missing

2. **Wrong topic**
   - Verify topic prefix matches config
   - Check MQTT_TOPICS.md for correct topics

3. **Invalid payload**
   - For lock command, use "LOCK" or "UNLOCK"
   - Case-insensitive but must be correct word

4. **API command failed**
   - Check logs for error messages
   - Vehicle may not support command in current state

### Home Assistant Not Discovering Entities

**Symptom**: No Skoda entities appear in Home Assistant

**Diagnosis**:
```bash
# Check if discovery is enabled
grep ha_discovery /etc/myskoda-mqtt/config.json

# Check discovery messages
mosquitto_sub -h 127.0.0.1 -t 'homeassistant/#' -v
```

**Common causes**:

1. **Discovery disabled**
   ```json
   {
     "ha_discovery": true
   }
   ```

2. **Wrong discovery prefix**
   - Default is "homeassistant"
   - Check Home Assistant MQTT integration settings

3. **MQTT integration not configured in HA**
   - Go to Settings → Devices & Services
   - Add MQTT integration if missing

4. **Discovery messages not retained**
   - Restart the bridge to republish
   ```bash
   sudo systemctl restart myskoda-mqtt.service
   ```

### High CPU Usage

**Symptom**: Service using excessive CPU

**Common causes**:

1. **Poll interval too short**
   - Increase `poll_interval` in config.json
   - Recommended: 300 seconds (5 minutes) or more

2. **Rapid reconnection loop**
   - Check logs for repeated connection attempts
   - May indicate MQTT or API issues

### Service Crashes or Restarts

**Symptom**: Service keeps restarting

**Diagnosis**:
```bash
# Check crash logs
sudo journalctl -u myskoda-mqtt.service -n 200

# Check system logs
sudo dmesg | tail -50
```

**Common causes**:

1. **Unhandled exception**
   - Check logs for Python tracebacks
   - Report as bug if reproducible

2. **Out of memory**
   - Check system memory: `free -h`
   - Unlikely with this service

3. **API rate limiting**
   - Increase poll interval
   - Check for error messages about rate limits

## Advanced Debugging

### Enable Debug Logging

Edit config.json:
```json
{
  "log_level": "DEBUG"
}
```

Restart service:
```bash
sudo systemctl restart myskoda-mqtt.service
```

### Manual Testing

Run the bridge manually for debugging:

```bash
# Stop the service
sudo systemctl stop myskoda-mqtt.service

# Run manually as homeassistant user
sudo -u homeassistant python3 -m myskoda_mqtt.main --config /etc/myskoda-mqtt/config.json
```

This shows all output directly in the terminal.

### MQTT Debugging

Monitor all MQTT traffic:

```bash
# Subscribe to everything
mosquitto_sub -h 127.0.0.1 -t '#' -v -u username -P password
```

### Network Debugging

Check network connectivity:

```bash
# Test DNS resolution
nslookup api.connect.skoda-auto.cz

# Test HTTPS connectivity
curl -I https://api.connect.skoda-auto.cz

# Check firewall
sudo iptables -L -n
```

## Getting Help

If you're still stuck:

1. **Check existing issues**: https://github.com/mikitu/myskoda-mqtt/issues
2. **Gather information**:
   - Service logs: `sudo journalctl -u myskoda-mqtt.service -n 200`
   - Config (redact secrets): `cat /etc/myskoda-mqtt/config.json`
   - System info: `uname -a`, `python3 --version`
3. **Open an issue** with all relevant information

## Useful Commands Reference

```bash
# Service management
sudo systemctl start myskoda-mqtt.service
sudo systemctl stop myskoda-mqtt.service
sudo systemctl restart myskoda-mqtt.service
sudo systemctl status myskoda-mqtt.service
sudo systemctl enable myskoda-mqtt.service
sudo systemctl disable myskoda-mqtt.service

# Logs
sudo journalctl -u myskoda-mqtt.service -f          # Follow logs
sudo journalctl -u myskoda-mqtt.service -n 100      # Last 100 lines
sudo journalctl -u myskoda-mqtt.service --since today  # Today's logs

# MQTT testing
mosquitto_sub -h 127.0.0.1 -t 'skoda/#' -v
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/command/start_charging' -m 'START'

# Configuration
sudo nano /etc/myskoda-mqtt/config.json
python3 -m json.tool /etc/myskoda-mqtt/config.json  # Validate JSON
```

