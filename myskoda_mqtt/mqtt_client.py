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

            # Subscribe to command topics (new structure: cmd/*)
            command_topic = f"{self.topic_prefix}/cmd/#"
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

            # Extract command from topic (new structure: cmd/*)
            if topic.startswith(f"{self.topic_prefix}/cmd/"):
                command = topic.replace(f"{self.topic_prefix}/cmd/", "")

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
        Publish vehicle state to MQTT as a single JSON payload.

        Args:
            state_data: Dictionary containing vehicle state
        """
        if not self.connected:
            logger.warning("Not connected to MQTT broker, skipping state publish")
            return

        # Publish entire state as JSON to single topic
        state_json = json.dumps(state_data)
        self.client.publish(f"{self.topic_prefix}/state", state_json, retain=True)

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

        # Import discovery module
        from .discovery import HADiscovery

        # Create discovery helper
        discovery = HADiscovery(
            device_info=device_info,
            topic_prefix=self.topic_prefix,
            discovery_prefix=discovery_prefix
        )

        # Get all discovery configurations
        configs = discovery.get_all_configs()

        # Publish each configuration
        for topic, config in configs.items():
            self.client.publish(topic, json.dumps(config), retain=True)
            logger.debug(f"Published discovery config to {topic}")

        logger.info(f"Published {len(configs)} Home Assistant discovery configurations")

