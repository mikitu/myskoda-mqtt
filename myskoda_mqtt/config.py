"""
Configuration management for Skoda MQTT Bridge.
Loads settings from environment variables or config file.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration container for the Skoda MQTT Bridge."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration from environment variables or config file.
        
        Args:
            config_file: Path to JSON configuration file (optional)
        """
        # Load from file if provided
        file_config = {}
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                logger.info(f"Loaded configuration from {config_file}")
        
        # Skoda API credentials
        self.skoda_username = os.getenv('SKODA_USERNAME', file_config.get('skoda_username', ''))
        self.skoda_password = os.getenv('SKODA_PASSWORD', file_config.get('skoda_password', ''))
        self.skoda_vin = os.getenv('SKODA_VIN', file_config.get('skoda_vin', ''))
        
        # MQTT settings
        self.mqtt_broker = os.getenv('MQTT_BROKER', file_config.get('mqtt_broker', '127.0.0.1'))
        self.mqtt_port = int(os.getenv('MQTT_PORT', file_config.get('mqtt_port', 1883)))
        self.mqtt_username = os.getenv('MQTT_USERNAME', file_config.get('mqtt_username', ''))
        self.mqtt_password = os.getenv('MQTT_PASSWORD', file_config.get('mqtt_password', ''))
        self.mqtt_topic_prefix = os.getenv('MQTT_TOPIC_PREFIX', file_config.get('mqtt_topic_prefix', 'skoda/enyaq'))
        
        # Polling and rate limiting
        self.poll_interval = int(os.getenv('POLL_INTERVAL', file_config.get('poll_interval', 300)))  # 5 minutes default
        self.command_timeout = int(os.getenv('COMMAND_TIMEOUT', file_config.get('command_timeout', 30)))
        
        # Home Assistant Discovery
        self.ha_discovery = os.getenv('HA_DISCOVERY', file_config.get('ha_discovery', 'true')).lower() == 'true'
        self.ha_discovery_prefix = os.getenv('HA_DISCOVERY_PREFIX', file_config.get('ha_discovery_prefix', 'homeassistant'))
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', file_config.get('log_level', 'INFO')).upper()
        
        # Validate required fields
        self._validate()
    
    def _validate(self):
        """Validate that required configuration is present."""
        required_fields = {
            'skoda_username': self.skoda_username,
            'skoda_password': self.skoda_password,
            'skoda_vin': self.skoda_vin,
        }
        
        missing = [field for field, value in required_fields.items() if not value]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    def to_dict(self, include_secrets: bool = False) -> dict:
        """
        Convert configuration to dictionary.
        
        Args:
            include_secrets: Whether to include sensitive information
            
        Returns:
            Dictionary representation of configuration
        """
        config_dict = {
            'mqtt_broker': self.mqtt_broker,
            'mqtt_port': self.mqtt_port,
            'mqtt_topic_prefix': self.mqtt_topic_prefix,
            'poll_interval': self.poll_interval,
            'command_timeout': self.command_timeout,
            'ha_discovery': self.ha_discovery,
            'ha_discovery_prefix': self.ha_discovery_prefix,
            'log_level': self.log_level,
        }
        
        if include_secrets:
            config_dict.update({
                'skoda_username': self.skoda_username,
                'skoda_password': '***' if self.skoda_password else '',
                'skoda_vin': self.skoda_vin,
                'mqtt_username': self.mqtt_username,
                'mqtt_password': '***' if self.mqtt_password else '',
            })
        
        return config_dict

