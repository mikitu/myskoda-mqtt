"""
Home Assistant MQTT Discovery configuration builder.

This module creates MQTT Discovery payloads for Home Assistant entities.
All entities are automatically discovered and configured in Home Assistant.
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HADiscovery:
    """Home Assistant MQTT Discovery helper."""
    
    def __init__(
        self,
        device_info: Dict[str, Any],
        topic_prefix: str,
        discovery_prefix: str = "homeassistant"
    ):
        """
        Initialize HA Discovery helper.
        
        Args:
            device_info: Device information (name, manufacturer, model, identifiers)
            topic_prefix: MQTT topic prefix for state/command topics
            discovery_prefix: Home Assistant discovery prefix
        """
        self.device_info = device_info
        self.topic_prefix = topic_prefix.rstrip('/')
        self.discovery_prefix = discovery_prefix.rstrip('/')
        self.device_id = device_info['identifiers'][0]
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all discovery configurations.
        
        Returns:
            Dictionary mapping discovery topics to their config payloads
        """
        configs = {}
        
        # Add all entity configurations
        configs.update(self._get_sensor_configs())
        configs.update(self._get_binary_sensor_configs())
        configs.update(self._get_button_configs())
        
        return configs
    
    def _get_sensor_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get sensor entity configurations."""
        configs = {}
        
        # Battery SOC sensor
        configs[f"{self.discovery_prefix}/sensor/{self.device_id}/battery_soc/config"] = {
            "name": "Battery Level",
            "unique_id": f"{self.device_id}_battery_soc",
            "state_topic": f"{self.topic_prefix}/state",
            "value_template": "{{ value_json.battery.soc }}",
            "unit_of_measurement": "%",
            "device_class": "battery",
            "state_class": "measurement",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": self.device_info,
        }
        
        # Range sensor
        configs[f"{self.discovery_prefix}/sensor/{self.device_id}/range/config"] = {
            "name": "Range",
            "unique_id": f"{self.device_id}_range",
            "state_topic": f"{self.topic_prefix}/state",
            "value_template": "{{ value_json.battery.range_km }}",
            "unit_of_measurement": "km",
            "icon": "mdi:map-marker-distance",
            "state_class": "measurement",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": self.device_info,
        }
        
        return configs
    
    def _get_binary_sensor_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get binary sensor entity configurations."""
        configs = {}
        
        # Charging status binary sensor
        configs[f"{self.discovery_prefix}/binary_sensor/{self.device_id}/charging/config"] = {
            "name": "Charging",
            "unique_id": f"{self.device_id}_charging",
            "state_topic": f"{self.topic_prefix}/state",
            "value_template": "{{ value_json.battery.charging }}",
            "payload_on": True,
            "payload_off": False,
            "device_class": "battery_charging",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": self.device_info,
        }
        
        # Plugged in binary sensor
        configs[f"{self.discovery_prefix}/binary_sensor/{self.device_id}/plugged_in/config"] = {
            "name": "Plugged In",
            "unique_id": f"{self.device_id}_plugged_in",
            "state_topic": f"{self.topic_prefix}/state",
            "value_template": "{{ value_json.battery.plugged_in }}",
            "payload_on": True,
            "payload_off": False,
            "device_class": "plug",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": self.device_info,
        }
        
        return configs
    
    def _get_button_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get button entity configurations."""
        configs = {}
        
        # Start charging button
        configs[f"{self.discovery_prefix}/button/{self.device_id}/start_charging/config"] = {
            "name": "Start Charging",
            "unique_id": f"{self.device_id}_start_charging",
            "command_topic": f"{self.topic_prefix}/cmd/start_charging",
            "payload_press": "PRESS",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": self.device_info,
            "icon": "mdi:battery-charging",
        }
        
        # Stop charging button
        configs[f"{self.discovery_prefix}/button/{self.device_id}/stop_charging/config"] = {
            "name": "Stop Charging",
            "unique_id": f"{self.device_id}_stop_charging",
            "command_topic": f"{self.topic_prefix}/cmd/stop_charging",
            "payload_press": "PRESS",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": self.device_info,
            "icon": "mdi:battery-off",
        }

        # Lock button
        configs[f"{self.discovery_prefix}/button/{self.device_id}/lock/config"] = {
            "name": "Lock Vehicle",
            "unique_id": f"{self.device_id}_lock",
            "command_topic": f"{self.topic_prefix}/cmd/lock",
            "payload_press": "PRESS",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": self.device_info,
            "icon": "mdi:lock",
        }

        # Unlock button
        configs[f"{self.discovery_prefix}/button/{self.device_id}/unlock/config"] = {
            "name": "Unlock Vehicle",
            "unique_id": f"{self.device_id}_unlock",
            "command_topic": f"{self.topic_prefix}/cmd/unlock",
            "payload_press": "PRESS",
            "availability_topic": f"{self.topic_prefix}/availability",
            "device": self.device_info,
            "icon": "mdi:lock-open",
        }

        return configs

