# MQTT Topics Reference

This document describes all MQTT topics used by the Skoda MQTT Bridge.

## Topic Prefix

All topics are prefixed with a configurable prefix (default: `skoda/enyaq`). This document uses the default prefix in examples.

## State Topics

These topics are published by the bridge to report vehicle state. All state topics use `retain=true` so the last value is always available.

### Battery Topics

#### `skoda/enyaq/battery/soc`
- **Description**: Battery state of charge
- **Type**: Integer
- **Unit**: Percentage (%)
- **Range**: 0-100
- **Example**: `75`
- **Update frequency**: Every poll interval (default: 5 minutes)

#### `skoda/enyaq/battery/range`
- **Description**: Estimated remaining range
- **Type**: Integer
- **Unit**: Kilometers (km)
- **Example**: `280`
- **Update frequency**: Every poll interval

#### `skoda/enyaq/battery/charging`
- **Description**: Whether the vehicle is currently charging
- **Type**: String
- **Values**: `ON` or `OFF`
- **Example**: `OFF`
- **Update frequency**: Every poll interval, immediately after charging commands

#### `skoda/enyaq/battery/plugged_in`
- **Description**: Whether the charging cable is plugged in
- **Type**: String
- **Values**: `ON` or `OFF`
- **Example**: `ON`
- **Update frequency**: Every poll interval

### Door Topics

#### `skoda/enyaq/doors/locked`
- **Description**: Door lock status
- **Type**: String
- **Values**: `LOCKED` or `UNLOCKED`
- **Example**: `LOCKED`
- **Update frequency**: Every poll interval, immediately after lock commands

### System Topics

#### `skoda/enyaq/availability`
- **Description**: Bridge availability status
- **Type**: String
- **Values**: `online` or `offline`
- **Example**: `online`
- **Update frequency**: On connect/disconnect
- **Note**: Set as Last Will and Testament (LWT) in MQTT

#### `skoda/enyaq/last_updated`
- **Description**: ISO 8601 timestamp of last successful update
- **Type**: String (ISO 8601 format)
- **Example**: `2026-01-04T10:30:45.123456`
- **Update frequency**: Every poll interval

## Command Topics

These topics are subscribed to by the bridge to receive commands. The bridge listens on `skoda/enyaq/command/#`.

### Charging Commands

#### `skoda/enyaq/command/start_charging`
- **Description**: Start vehicle charging
- **Payload**: Any (payload is ignored)
- **Example**: `START` or empty payload
- **Response**: Immediate state update on all battery topics
- **Note**: Only works when vehicle is plugged in

#### `skoda/enyaq/command/stop_charging`
- **Description**: Stop vehicle charging
- **Payload**: Any (payload is ignored)
- **Example**: `STOP` or empty payload
- **Response**: Immediate state update on all battery topics
- **Note**: Only works when vehicle is currently charging

### Lock Commands

#### `skoda/enyaq/command/lock`
- **Description**: Lock or unlock the vehicle
- **Payload**: `LOCK` or `UNLOCK`
- **Example**: `LOCK`
- **Response**: Immediate state update on `skoda/enyaq/doors/locked`
- **Note**: Case-insensitive

## Home Assistant MQTT Discovery

When `ha_discovery` is enabled, the bridge publishes discovery messages to Home Assistant. These are published once on startup.

### Discovery Topic Pattern

```
homeassistant/{component}/{device_id}/{entity_id}/config
```

### Published Entities

1. **Battery Level Sensor**
   - Topic: `homeassistant/sensor/skoda_VIN/battery_soc/config`
   - Device class: `battery`
   - Unit: `%`

2. **Range Sensor**
   - Topic: `homeassistant/sensor/skoda_VIN/range/config`
   - Icon: `mdi:map-marker-distance`
   - Unit: `km`

3. **Charging Binary Sensor**
   - Topic: `homeassistant/binary_sensor/skoda_VIN/charging/config`
   - Device class: `battery_charging`

4. **Plugged In Binary Sensor**
   - Topic: `homeassistant/binary_sensor/skoda_VIN/plugged_in/config`
   - Device class: `plug`

5. **Door Lock**
   - Topic: `homeassistant/lock/skoda_VIN/door_lock/config`
   - Supports lock/unlock commands

All entities include:
- Availability topic: `skoda/enyaq/availability`
- Device information (manufacturer, model, identifiers)

## Example MQTT Messages

### Publishing a command (using mosquitto_pub)

```bash
# Start charging
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/command/start_charging' -m 'START'

# Stop charging
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/command/stop_charging' -m 'STOP'

# Lock vehicle
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/command/lock' -m 'LOCK'

# Unlock vehicle
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/command/lock' -m 'UNLOCK'
```

### Subscribing to all topics (using mosquitto_sub)

```bash
# Subscribe to all Skoda topics
mosquitto_sub -h 127.0.0.1 -t 'skoda/#' -v

# Subscribe to battery topics only
mosquitto_sub -h 127.0.0.1 -t 'skoda/enyaq/battery/#' -v

# Subscribe to command topics
mosquitto_sub -h 127.0.0.1 -t 'skoda/enyaq/command/#' -v
```

## Topic Customization

You can customize the topic prefix in the configuration file:

```json
{
  "mqtt_topic_prefix": "vehicles/skoda/enyaq"
}
```

This would change all topics to use `vehicles/skoda/enyaq` as the prefix instead of `skoda/enyaq`.

## Rate Limiting Considerations

- **Polling interval**: Default 5 minutes to avoid API rate limits
- **Command execution**: Commands trigger immediate state updates
- **Avoid rapid commands**: Wait at least 30 seconds between commands
- **API limits**: Skoda Connect API may have undocumented rate limits

## QoS Levels

- **State topics**: QoS 0 (at most once) with retain flag
- **Command topics**: QoS 1 (at least once) without retain
- **Availability topic**: QoS 1 with retain flag (LWT)

