"""
Main application entry point for Skoda MQTT Bridge.
"""

import sys
import time
import signal
import logging
import argparse
from pathlib import Path
from typing import Optional

from .config import Config
from .skoda_api import SkodaAPI, SkodaAPIError
from .mqtt_client import MQTTClient

logger = logging.getLogger(__name__)


class SkodaMQTTBridge:
    """Main application class for Skoda MQTT Bridge."""
    
    def __init__(self, config: Config):
        """
        Initialize the bridge.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.running = False
        self.skoda_api: Optional[SkodaAPI] = None
        self.mqtt_client: Optional[MQTTClient] = None
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self):
        """Start the bridge."""
        logger.info("Starting Skoda MQTT Bridge...")
        logger.info(f"Configuration: {self.config.to_dict(include_secrets=False)}")
        
        self._setup_signal_handlers()
        
        try:
            # Initialize Skoda API
            self.skoda_api = SkodaAPI(
                username=self.config.skoda_username,
                password=self.config.skoda_password,
                vin=self.config.skoda_vin
            )
            
            # Authenticate
            self.skoda_api.authenticate()
            
            # Initialize MQTT client
            self.mqtt_client = MQTTClient(
                broker=self.config.mqtt_broker,
                port=self.config.mqtt_port,
                username=self.config.mqtt_username,
                password=self.config.mqtt_password,
                topic_prefix=self.config.mqtt_topic_prefix
            )
            
            # Register command callbacks
            self._register_command_handlers()
            
            # Connect to MQTT broker
            self.mqtt_client.connect()
            
            # Wait for MQTT connection
            time.sleep(2)
            
            # Publish Home Assistant discovery if enabled
            if self.config.ha_discovery:
                self._publish_ha_discovery()
            
            # Start main loop
            self.running = True
            self._main_loop()
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bridge."""
        if not self.running:
            return
        
        logger.info("Stopping Skoda MQTT Bridge...")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.publish_availability(False)
            self.mqtt_client.disconnect()
        
        logger.info("Skoda MQTT Bridge stopped")
    
    def _main_loop(self):
        """Main polling loop."""
        logger.info(f"Starting main loop (poll interval: {self.config.poll_interval}s)...")
        
        while self.running:
            try:
                # Fetch vehicle status
                logger.debug("Fetching vehicle status...")
                status = self.skoda_api.get_vehicle_status()
                
                # Publish to MQTT
                self.mqtt_client.publish_state(status)
                
                # Wait for next poll
                time.sleep(self.config.poll_interval)
                
            except SkodaAPIError as e:
                logger.error(f"API error: {e}")
                time.sleep(60)  # Wait before retrying
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                time.sleep(60)

    def _register_command_handlers(self):
        """Register MQTT command handlers."""
        logger.info("Registering command handlers...")

        def handle_start_charging(payload):
            try:
                logger.info("Handling start charging command")
                self.skoda_api.start_charging()
                # Immediately update state
                status = self.skoda_api.get_vehicle_status()
                self.mqtt_client.publish_state(status)
            except Exception as e:
                logger.error(f"Failed to start charging: {e}")

        def handle_stop_charging(payload):
            try:
                logger.info("Handling stop charging command")
                self.skoda_api.stop_charging()
                # Immediately update state
                status = self.skoda_api.get_vehicle_status()
                self.mqtt_client.publish_state(status)
            except Exception as e:
                logger.error(f"Failed to stop charging: {e}")

        def handle_lock(payload):
            try:
                logger.info("Handling lock command")
                self.skoda_api.lock_vehicle()
                # Immediately update state
                status = self.skoda_api.get_vehicle_status()
                self.mqtt_client.publish_state(status)
            except Exception as e:
                logger.error(f"Failed to lock vehicle: {e}")

        def handle_unlock(payload):
            try:
                logger.info("Handling unlock command")
                self.skoda_api.unlock_vehicle()
                # Immediately update state
                status = self.skoda_api.get_vehicle_status()
                self.mqtt_client.publish_state(status)
            except Exception as e:
                logger.error(f"Failed to unlock vehicle: {e}")

        self.mqtt_client.register_command_callback("start_charging", handle_start_charging)
        self.mqtt_client.register_command_callback("stop_charging", handle_stop_charging)
        self.mqtt_client.register_command_callback("lock", handle_lock)
        self.mqtt_client.register_command_callback("unlock", handle_unlock)

    def _publish_ha_discovery(self):
        """Publish Home Assistant discovery messages."""
        device_info = {
            "identifiers": [f"skoda_{self.config.skoda_vin}"],
            "name": getattr(self.config, 'device_name', "Skoda Enyaq"),
            "manufacturer": getattr(self.config, 'device_manufacturer', "Skoda"),
            "model": getattr(self.config, 'device_model', "Enyaq iV"),
            "sw_version": "1.0.0",
        }

        self.mqtt_client.publish_ha_discovery(
            device_info=device_info,
            discovery_prefix=self.config.ha_discovery_prefix
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Skoda MQTT Bridge")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (JSON format)"
    )
    args = parser.parse_args()

    try:
        # Load configuration
        config = Config(config_file=args.config)

        # Create and start bridge
        bridge = SkodaMQTTBridge(config)
        bridge.start()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

