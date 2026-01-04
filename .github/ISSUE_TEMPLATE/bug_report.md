---
name: Bug Report
about: Report a bug or issue
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Go to '...'
2. Run command '...'
3. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Logs

```
Paste relevant logs here (from: sudo journalctl -u myskoda-mqtt.service -n 100)
```

## Configuration

```json
{
  "mqtt_broker": "127.0.0.1",
  "poll_interval": 300,
  "log_level": "INFO"
  // Redact sensitive information (passwords, VIN, etc.)
}
```

## Environment

- **OS**: [e.g., Ubuntu 22.04]
- **Python Version**: [e.g., 3.10.6]
- **Home Assistant Version**: [e.g., 2024.1.0]
- **Installation Method**: [systemd / manual / other]
- **MQTT Broker**: [Mosquitto / other]

## Additional Context

Add any other context about the problem here.

