# Security Considerations

This document outlines important security considerations when using the Skoda MQTT Bridge.

## Overview

The Skoda MQTT Bridge has access to your vehicle through the Skoda Connect API and can execute commands like starting/stopping charging and locking/unlocking doors. **Treat this service with the same security level as your physical car keys.**

## Credential Security

### Configuration File Protection

The configuration file contains sensitive credentials:
- Skoda Connect username and password
- MQTT broker credentials
- Vehicle VIN

**Required security measures:**

```bash
# Set restrictive permissions (owner read/write only)
sudo chmod 600 /etc/myskoda-mqtt/config.json

# Ensure correct ownership
sudo chown homeassistant:homeassistant /etc/myskoda-mqtt/config.json
```

### Environment Variables Alternative

For enhanced security, you can use environment variables instead of a config file:

```bash
# Create systemd override
sudo systemctl edit myskoda-mqtt.service
```

Add environment variables:

```ini
[Service]
Environment="SKODA_USERNAME=your-email@example.com"
Environment="SKODA_PASSWORD=your-password"
Environment="SKODA_VIN=YOUR-VIN"
Environment="MQTT_USERNAME=mqtt-user"
Environment="MQTT_PASSWORD=mqtt-password"
```

This keeps credentials out of config files, but they're still visible in systemd configuration.

### Secrets Management (Advanced)

For production deployments, consider:
- **systemd credentials**: Use `LoadCredential` in systemd (systemd 250+)
- **HashiCorp Vault**: Store secrets in Vault and retrieve at runtime
- **Encrypted config**: Encrypt the config file and decrypt at service start

## MQTT Security

### Authentication

**Always use MQTT authentication:**

```json
{
  "mqtt_username": "skoda-bridge",
  "mqtt_password": "strong-random-password"
}
```

Create a dedicated MQTT user with minimal permissions:

```bash
# In Mosquitto
mosquitto_passwd -b /etc/mosquitto/passwd skoda-bridge strong-random-password
```

### Authorization (ACL)

Configure Mosquitto ACL to restrict the bridge's access:

```
# /etc/mosquitto/acl
user skoda-bridge
topic write skoda/#
topic read skoda/enyaq/command/#
topic write homeassistant/#
```

This ensures the bridge can only:
- Publish to `skoda/*` topics
- Subscribe to `skoda/enyaq/command/*` topics
- Publish Home Assistant discovery messages

### TLS/SSL

For production or remote access, enable MQTT over TLS:

```json
{
  "mqtt_broker": "127.0.0.1",
  "mqtt_port": 8883,
  "mqtt_use_tls": true,
  "mqtt_ca_cert": "/etc/ssl/certs/ca.crt"
}
```

**Note**: Current implementation doesn't include TLS support. This would need to be added to `mqtt_client.py`.

### Network Isolation

- **Keep MQTT broker local**: Use `127.0.0.1` when possible
- **Firewall rules**: Block external access to MQTT port (1883/8883)
- **VPN only**: If remote access needed, use VPN instead of exposing MQTT

## API Security

### Rate Limiting

The bridge implements rate limiting to avoid API abuse:

- **Default poll interval**: 5 minutes (300 seconds)
- **Minimum recommended**: 3 minutes (180 seconds)
- **Command cooldown**: 30 seconds between commands

**Why this matters:**
- Skoda Connect API may have undocumented rate limits
- Excessive requests could result in account suspension
- Frequent polling drains vehicle's 12V battery

### Token Management

- **Tokens stored in memory only**: Never written to disk
- **Automatic refresh**: Tokens refreshed before expiration
- **No token logging**: Tokens never appear in logs

### API Endpoint Security

The bridge connects to official Skoda Connect API endpoints over HTTPS. However:

- **Man-in-the-middle risk**: Ensure system CA certificates are up to date
- **DNS security**: Use trusted DNS servers
- **Certificate validation**: Always enabled (don't disable SSL verification)

## Home Assistant Security

### Secure Your Home Assistant Instance

Since the bridge integrates with Home Assistant:

1. **Enable authentication**: Never run Home Assistant without authentication
2. **Use HTTPS**: Enable SSL for Home Assistant web interface
3. **Strong passwords**: Use strong, unique passwords
4. **2FA**: Enable two-factor authentication if available
5. **Regular updates**: Keep Home Assistant updated
6. **Network isolation**: Don't expose Home Assistant directly to internet

### MQTT Discovery Security

Home Assistant MQTT Discovery is convenient but:

- **Automatic entity creation**: Entities are created automatically
- **Trust implications**: Only enable if you trust the MQTT broker
- **Disable if not needed**: Set `ha_discovery: false` if you prefer manual configuration

## System Security

### Service Hardening

The systemd service includes security hardening:

```ini
[Service]
# Prevent privilege escalation
NoNewPrivileges=true

# Isolate /tmp
PrivateTmp=true

# Protect system files
ProtectSystem=strict

# Protect home directories
ProtectHome=true

# Limit write access
ReadWritePaths=/var/log/myskoda-mqtt
```

### User Isolation

The service runs as a dedicated user (`homeassistant`) with minimal privileges:

```bash
# Check user permissions
id homeassistant
```

**Never run as root.**

### Log Security

Logs may contain sensitive information:

```bash
# Restrict log access
sudo chmod 750 /var/log/myskoda-mqtt
sudo chown homeassistant:homeassistant /var/log/myskoda-mqtt
```

Logs are also sent to journald:

```bash
# View logs (requires sudo)
sudo journalctl -u myskoda-mqtt.service
```

## Risks and Limitations

### What This Bridge Can Do

- ✅ Read vehicle status (battery, range, lock status)
- ✅ Start/stop charging
- ✅ Lock/unlock vehicle
- ❌ Start the vehicle remotely (not supported by API)
- ❌ Track vehicle location (not implemented)
- ❌ Access vehicle cameras (not supported by API)

### Potential Attack Vectors

1. **Compromised Home Assistant**: Attacker could send MQTT commands
2. **MQTT broker compromise**: Attacker could intercept or send commands
3. **Stolen credentials**: Attacker could access Skoda Connect account
4. **Local system compromise**: Attacker could read config file or memory

### Mitigation Strategies

1. **Defense in depth**: Secure every layer (HA, MQTT, system, network)
2. **Monitoring**: Monitor logs for suspicious activity
3. **Alerts**: Set up alerts for unexpected commands
4. **Regular audits**: Review access logs and configurations
5. **Principle of least privilege**: Only grant necessary permissions

## Incident Response

### If You Suspect Compromise

1. **Immediately stop the service**:
   ```bash
   sudo systemctl stop myskoda-mqtt.service
   ```

2. **Change Skoda Connect password**:
   - Log in to Skoda Connect website
   - Change password immediately
   - Review account activity

3. **Change MQTT credentials**:
   ```bash
   mosquitto_passwd -b /etc/mosquitto/passwd skoda-bridge new-password
   sudo systemctl restart mosquitto
   ```

4. **Review logs**:
   ```bash
   sudo journalctl -u myskoda-mqtt.service -n 1000
   ```

5. **Check for unauthorized commands**:
   - Review MQTT logs
   - Check Home Assistant history
   - Verify vehicle status

### Reporting Security Issues

If you discover a security vulnerability in this project:

1. **Do not** open a public GitHub issue
2. Email the maintainer directly (see GitHub profile)
3. Include detailed description and reproduction steps
4. Allow reasonable time for fix before public disclosure

## Best Practices Summary

✅ **DO:**
- Use strong, unique passwords
- Enable MQTT authentication
- Restrict file permissions (600 for config)
- Run as non-root user
- Keep software updated
- Monitor logs regularly
- Use local MQTT broker when possible
- Set reasonable poll intervals (5+ minutes)

❌ **DON'T:**
- Expose MQTT broker to internet
- Run service as root
- Share credentials
- Disable SSL certificate validation
- Use default passwords
- Poll API too frequently
- Store credentials in version control
- Ignore security updates

## Compliance and Legal

### Data Privacy

This bridge processes:
- Vehicle location data (if implemented)
- Vehicle status information
- User credentials

**Your responsibilities:**
- Comply with local data protection laws (GDPR, etc.)
- Inform users if sharing data
- Secure personal information appropriately

### Terms of Service

Using this bridge may be subject to:
- Skoda Connect Terms of Service
- Volkswagen Group API usage policies

**Note**: This is an unofficial integration. Use at your own risk.

## Disclaimer

The authors of this software are not responsible for:
- Unauthorized access to your vehicle
- Damage resulting from security breaches
- Violations of Skoda Connect Terms of Service
- Any other damages or losses

**Use this software at your own risk. You are responsible for securing your installation.**

