# MQTT Topics Reference

This document describes all MQTT topics used by the Skoda MQTT Bridge.

## Topic Prefix

All topics are prefixed with a configurable prefix (default: `skoda/enyaq`). This document uses the default prefix in examples.

## State Topic

The bridge publishes all vehicle state as a **single JSON payload** to one topic. This simplifies the MQTT structure and makes it easier to consume the data.

### `skoda/enyaq/state`

- **Description**: Complete vehicle state as JSON
- **Type**: JSON object
- **Retain**: `true` (last value always available)
- **Update frequency**: Every poll interval (default: 5 minutes), immediately after commands

#### JSON Structure

```json
{
  "battery": {
    "soc": 75,
    "range_km": 280,
    "charging": false,
    "plugged_in": true
  },
  "doors": {
    "locked": true
  },
  "last_updated": "2026-01-04T10:30:45.123456"
}
```

#### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `battery.soc` | Integer | Battery state of charge (%) | `75` |
| `battery.range_km` | Integer | Estimated range in kilometers | `280` |
| `battery.charging` | Boolean | Whether vehicle is charging | `false` |
| `battery.plugged_in` | Boolean | Whether charging cable is connected | `true` |
| `doors.locked` | Boolean | Whether doors are locked | `true` |
| `last_updated` | String | ISO 8601 timestamp of last update | `"2026-01-04T10:30:45.123456"` |

### `skoda/enyaq/availability`

- **Description**: Bridge availability status
- **Type**: String
- **Values**: `online` or `offline`
- **Retain**: `true`
- **Update frequency**: On connect/disconnect
- **Note**: Set as Last Will and Testament (LWT) in MQTT

## Command Topics

These topics are subscribed to by the bridge to receive commands. The bridge listens on `skoda/enyaq/cmd/#`.

All command topics use the `cmd/` prefix to clearly distinguish them from state topics.

### `skoda/enyaq/cmd/start_charging`

- **Description**: Start vehicle charging
- **Payload**: `PRESS` (or any value, payload is ignored)
- **Retain**: `false`
- **Response**: Immediate state update published to `skoda/enyaq/state`
- **Note**: Only works when vehicle is plugged in

### `skoda/enyaq/cmd/stop_charging`

- **Description**: Stop vehicle charging
- **Payload**: `PRESS` (or any value, payload is ignored)
- **Retain**: `false`
- **Response**: Immediate state update published to `skoda/enyaq/state`
- **Note**: Only works when vehicle is currently charging

### `skoda/enyaq/cmd/lock`

- **Description**: Lock the vehicle
- **Payload**: `PRESS` (or any value, payload is ignored)
- **Retain**: `false`
- **Response**: Immediate state update published to `skoda/enyaq/state`

### `skoda/enyaq/cmd/unlock`

- **Description**: Unlock the vehicle
- **Payload**: `PRESS` (or any value, payload is ignored)
- **Retain**: `false`
- **Response**: Immediate state update published to `skoda/enyaq/state`

## Home Assistant MQTT Discovery

When `ha_discovery` is enabled in the configuration, the bridge automatically publishes discovery messages to Home Assistant. **No manual sensor configuration is needed** - all entities appear automatically in Home Assistant.

Discovery messages are published once on startup to the Home Assistant discovery prefix (default: `homeassistant`).

### Discovery Topic Pattern

```
homeassistant/{component}/{device_id}/{entity_id}/config
```

### Automatically Created Entities

The following entities are automatically created in Home Assistant:

#### Sensors

1. **Battery Level**
   - Entity ID: `sensor.skoda_enyaq_battery_level`
   - Device class: `battery`
   - Unit: `%`
   - State class: `measurement`
   - Value template: `{{ value_json.battery.soc }}`

2. **Range**
   - Entity ID: `sensor.skoda_enyaq_range`
   - Icon: `mdi:map-marker-distance`
   - Unit: `km`
   - State class: `measurement`
   - Value template: `{{ value_json.battery.range_km }}`

#### Binary Sensors

3. **Charging**
   - Entity ID: `binary_sensor.skoda_enyaq_charging`
   - Device class: `battery_charging`
   - Value template: `{{ value_json.battery.charging }}`

4. **Plugged In**
   - Entity ID: `binary_sensor.skoda_enyaq_plugged_in`
   - Device class: `plug`
   - Value template: `{{ value_json.battery.plugged_in }}`

#### Buttons

5. **Start Charging**
   - Entity ID: `button.skoda_enyaq_start_charging`
   - Icon: `mdi:battery-charging`
   - Command topic: `skoda/enyaq/cmd/start_charging`

6. **Stop Charging**
   - Entity ID: `button.skoda_enyaq_stop_charging`
   - Icon: `mdi:battery-off`
   - Command topic: `skoda/enyaq/cmd/stop_charging`

7. **Lock Vehicle**
   - Entity ID: `button.skoda_enyaq_lock_vehicle`
   - Icon: `mdi:lock`
   - Command topic: `skoda/enyaq/cmd/lock`

8. **Unlock Vehicle**
   - Entity ID: `button.skoda_enyaq_unlock_vehicle`
   - Icon: `mdi:lock-open`
   - Command topic: `skoda/enyaq/cmd/unlock`

### Device Information

All entities are grouped under a single device in Home Assistant with the following information:

- **Name**: Configurable (default: "Skoda Enyaq")
- **Manufacturer**: Configurable (default: "Skoda")
- **Model**: Configurable (default: "Enyaq iV")
- **Identifiers**: `skoda_{VIN}`

### Availability

All entities include an availability topic (`skoda/enyaq/availability`) that shows whether the bridge is online or offline. When the bridge is offline, all entities will show as "Unavailable" in Home Assistant.

## Example MQTT Messages

### Subscribing to topics (using mosquitto_sub)

```bash
# Subscribe to all Skoda topics
mosquitto_sub -h 127.0.0.1 -t 'skoda/#' -v

# Subscribe to state topic only
mosquitto_sub -h 127.0.0.1 -t 'skoda/enyaq/state' -v

# Subscribe to command topics
mosquitto_sub -h 127.0.0.1 -t 'skoda/enyaq/cmd/#' -v
```

### Publishing commands (using mosquitto_pub)

```bash
# Start charging
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/cmd/start_charging' -m 'PRESS'

# Stop charging
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/cmd/stop_charging' -m 'PRESS'

# Lock vehicle
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/cmd/lock' -m 'PRESS'

# Unlock vehicle
mosquitto_pub -h 127.0.0.1 -t 'skoda/enyaq/cmd/unlock' -m 'PRESS'
```

### Example state payload

When you subscribe to `skoda/enyaq/state`, you'll receive JSON payloads like this:

```json
{
  "battery": {
    "soc": 75,
    "range_km": 280,
    "charging": false,
    "plugged_in": true
  },
  "doors": {
    "locked": true
  },
  "last_updated": "2026-01-04T10:30:45.123456"
}
```

## Topic Customization

You can customize the topic prefix in the configuration file:

```json
{
  "mqtt_topic_prefix": "vehicles/skoda/enyaq"
}
```

This would change all topics to use `vehicles/skoda/enyaq` as the prefix instead of `skoda/enyaq`.

Example with custom prefix:
- State topic: `vehicles/skoda/enyaq/state`
- Command topics: `vehicles/skoda/enyaq/cmd/*`
- Availability: `vehicles/skoda/enyaq/availability`

## Rate Limiting and Safety

### Polling Interval

- **Minimum**: 300 seconds (5 minutes) - enforced by configuration
- **Default**: 300 seconds (5 minutes)
- **Recommended**: 300-600 seconds to avoid API rate limits
- **Why**: Skoda Connect API has rate limits; excessive polling may result in temporary bans

### Command Execution

- Commands trigger **immediate state updates** after execution
- Wait at least 30 seconds between commands
- The bridge does not queue commands - one command at a time
- Failed commands are logged but do not crash the service

### Error Handling

- Temporary API failures are logged and retried on next poll
- The bridge continues running even if the Skoda API is temporarily unavailable
- MQTT availability topic reflects bridge status, not API status

## QoS Levels

- **State topic**: QoS 0 (at most once) with `retain=true`
- **Command topics**: QoS 0 (at most once) with `retain=false`
- **Availability topic**: QoS 1 (at least once) with `retain=true` (Last Will and Testament)
- **Discovery topics**: QoS 0 with `retain=true`

## Integration with Home Assistant

### No Manual Configuration Required

When MQTT Discovery is enabled (default), you don't need to add anything to your Home Assistant configuration. The entities will appear automatically under:

**Settings → Devices & Services → MQTT → Devices → Skoda Enyaq**

### Using the Entities

Once discovered, you can:
- View battery level and range in dashboards
- See charging status in real-time
- Create automations based on battery level or charging state
- Control charging and locks via buttons or automations

### Example Automation

```yaml
automation:
  - alias: "Notify when charging complete"
    trigger:
      - platform: state
        entity_id: binary_sensor.skoda_enyaq_charging
        from: "on"
        to: "off"
    condition:
      - condition: numeric_state
        entity_id: sensor.skoda_enyaq_battery_level
        above: 80
    action:
      - service: notify.mobile_app
        data:
          message: "Skoda Enyaq charging complete ({{ states('sensor.skoda_enyaq_battery_level') }}%)"
```

