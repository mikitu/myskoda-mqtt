"""
MQTT client for publishing vehicle state and handling commands.
"""

import json
import logging
from typing import Callable, Dict, Any, Optional
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT client wrapper for Skoda vehicle integration."""
    
    def __init__(
        self,
        broker: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        topic_prefix: str = "skoda/enyaq",
        client_id: str = "myskoda-mqtt"
    ):
        """
        Initialize MQTT client.
        
        Args:
            broker: MQTT broker address
            port: MQTT broker port
            username: MQTT username (optional)
            password: MQTT password (optional)
            topic_prefix: Prefix for all MQTT topics
            client_id: MQTT client identifier
        """
        self.broker = broker
        self.port = port
        self.topic_prefix = topic_prefix.rstrip('/')
        self.command_callbacks: Dict[str, Callable] = {}
        
        # Create MQTT client
        self.client = mqtt.Client(client_id=client_id)
        
        # Set authentication if provided
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Connection state
        self.connected = False
    
    def connect(self):
        """Connect to MQTT broker."""
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        logger.info("Disconnecting from MQTT broker...")
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.connected = True
            
            # Subscribe to command topics
            command_topic = f"{self.topic_prefix}/command/#"
            self.client.subscribe(command_topic)
            logger.info(f"Subscribed to {command_topic}")
            
            # Publish availability
            self.publish_availability(True)
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker, return code: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logger.debug(f"Received message on {topic}: {payload}")
            
            # Extract command from topic
            if topic.startswith(f"{self.topic_prefix}/command/"):
                command = topic.replace(f"{self.topic_prefix}/command/", "")
                
                # Call registered callback if exists
                if command in self.command_callbacks:
                    self.command_callbacks[command](payload)
                else:
                    logger.warning(f"No handler registered for command: {command}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def register_command_callback(self, command: str, callback: Callable):
        """
        Register a callback for a specific command.
        
        Args:
            command: Command name (e.g., 'start_charging')
            callback: Function to call when command received
        """
        self.command_callbacks[command] = callback
        logger.info(f"Registered callback for command: {command}")
    
    def publish_state(self, state_data: Dict[str, Any]):
        """
        Publish vehicle state to MQTT.
        
        Args:
            state_data: Dictionary containing vehicle state
        """
        if not self.connected:
            logger.warning("Not connected to MQTT broker, skipping state publish")
            return
        
        # Publish battery state
        if 'battery' in state_data:
            battery = state_data['battery']
            self.client.publish(f"{self.topic_prefix}/battery/soc", battery.get('soc', 0), retain=True)
            self.client.publish(f"{self.topic_prefix}/battery/range", battery.get('range_km', 0), retain=True)
            self.client.publish(f"{self.topic_prefix}/battery/charging", 
                              'ON' if battery.get('charging', False) else 'OFF', retain=True)
            self.client.publish(f"{self.topic_prefix}/battery/plugged_in", 
                              'ON' if battery.get('plugged_in', False) else 'OFF', retain=True)
        
        # Publish door lock state
        if 'doors' in state_data:
            doors = state_data['doors']
            self.client.publish(f"{self.topic_prefix}/doors/locked", 
                              'LOCKED' if doors.get('locked', False) else 'UNLOCKED', retain=True)
        
        # Publish last updated timestamp
        if 'last_updated' in state_data:
            self.client.publish(f"{self.topic_prefix}/last_updated", state_data['last_updated'], retain=True)
        
        logger.debug("Published vehicle state to MQTT")

    def publish_availability(self, available: bool):
        """
        Publish availability status.

        Args:
            available: Whether the bridge is available
        """
        status = "online" if available else "offline"
        self.client.publish(f"{self.topic_prefix}/availability", status, retain=True)
        logger.info(f"Published availability: {status}")

    def publish_ha_discovery(self, device_info: Dict[str, Any], discovery_prefix: str = "homeassistant"):
        """
        Publish Home Assistant MQTT discovery messages.

        Args:
            device_info: Device information for Home Assistant
            discovery_prefix: Home Assistant discovery prefix
        """
        if not self.connected:
            logger.warning("Not connected to MQTT broker, skipping HA discovery")
            return

        logger.info("Publishing Home Assistant discovery messages...")

        # Battery SOC sensor
        soc_config = {
            "name": "Battery Level",
            "unique_id": f"{device_info['identifiers'][0]}_battery_soc",
            "state_topic": f"{self.topic_prefix}/battery/soc",
            "unit_of_measurement": "%",
            "device_class": "battery",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": device_info,
        }
        self.client.publish(
            f"{discovery_prefix}/sensor/{device_info['identifiers'][0]}/battery_soc/config",
            json.dumps(soc_config),
            retain=True
        )

        # Range sensor
        range_config = {
            "name": "Range",
            "unique_id": f"{device_info['identifiers'][0]}_range",
            "state_topic": f"{self.topic_prefix}/battery/range",
            "unit_of_measurement": "km",
            "icon": "mdi:map-marker-distance",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": device_info,
        }
        self.client.publish(
            f"{discovery_prefix}/sensor/{device_info['identifiers'][0]}/range/config",
            json.dumps(range_config),
            retain=True
        )

        # Charging status binary sensor
        charging_config = {
            "name": "Charging",
            "unique_id": f"{device_info['identifiers'][0]}_charging",
            "state_topic": f"{self.topic_prefix}/battery/charging",
            "payload_on": "ON",
            "payload_off": "OFF",
            "device_class": "battery_charging",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": device_info,
        }
        self.client.publish(
            f"{discovery_prefix}/binary_sensor/{device_info['identifiers'][0]}/charging/config",
            json.dumps(charging_config),
            retain=True
        )

        # Plugged in binary sensor
        plugged_config = {
            "name": "Plugged In",
            "unique_id": f"{device_info['identifiers'][0]}_plugged_in",
            "state_topic": f"{self.topic_prefix}/battery/plugged_in",
            "payload_on": "ON",
            "payload_off": "OFF",
            "device_class": "plug",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": device_info,
        }
        self.client.publish(
            f"{discovery_prefix}/binary_sensor/{device_info['identifiers'][0]}/plugged_in/config",
            json.dumps(plugged_config),
            retain=True
        )

        # Door lock sensor
        lock_config = {
            "name": "Door Lock",
            "unique_id": f"{device_info['identifiers'][0]}_door_lock",
            "state_topic": f"{self.topic_prefix}/doors/locked",
            "payload_lock": "LOCKED",
            "payload_unlock": "UNLOCKED",
            "command_topic": f"{self.topic_prefix}/command/lock",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": device_info,
        }
        self.client.publish(
            f"{discovery_prefix}/lock/{device_info['identifiers'][0]}/door_lock/config",
            json.dumps(lock_config),
            retain=True
        )

        logger.info("Home Assistant discovery messages published")

