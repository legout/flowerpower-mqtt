"""
Configuration-based example for FlowerPower MQTT Plugin.

This example demonstrates how to use YAML configuration files
for managing complex MQTT setups.
"""

import asyncio
import logging
from pathlib import Path
from flowerpower_mqtt import MQTTPlugin, FlowerPowerMQTTConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_example_config():
    """Create an example configuration file."""
    
    config = FlowerPowerMQTTConfig()
    
    # MQTT broker settings
    config.mqtt.broker = "localhost"
    config.mqtt.port = 1883
    config.mqtt.keepalive = 60
    config.mqtt.client_id = "flowerpower_config_example"
    
    # Job queue settings
    config.job_queue.enabled = True
    config.job_queue.redis_url = "redis://localhost:6379"
    config.job_queue.queue_name = "mqtt_pipelines"
    config.job_queue.worker_count = 4
    
    # Base directory
    config.base_dir = "."
    config.log_level = "INFO"
    
    # Predefined subscriptions
    from flowerpower_mqtt.config import SubscriptionConfig
    
    config.subscriptions = [
        SubscriptionConfig(
            topic="sensors/+/temperature",
            pipeline="temperature_processor",
            qos=1,
            execution_mode="async"
        ),
        SubscriptionConfig(
            topic="sensors/+/humidity", 
            pipeline="humidity_processor",
            qos=1,
            execution_mode="async"
        ),
        SubscriptionConfig(
            topic="alerts/critical",
            pipeline="critical_alert_handler",
            qos=2,
            execution_mode="sync"
        ),
        SubscriptionConfig(
            topic="logs/+/error",
            pipeline="error_log_processor", 
            qos=0,
            execution_mode="async"
        )
    ]
    
    # Save configuration
    config_file = Path("example_mqtt_config.yml")
    config.to_yaml(config_file)
    logger.info(f"Created example configuration: {config_file}")
    
    return config_file


async def main():
    """Configuration-based MQTT plugin usage."""
    
    # Create example configuration file
    config_file = create_example_config()
    
    try:
        # Load plugin from configuration
        logger.info(f"Loading plugin from configuration: {config_file}")
        mqtt = MQTTPlugin.from_config(config_file)
        
        # Connect to MQTT broker
        logger.info("Connecting to MQTT broker...")
        await mqtt.connect()
        
        # Display loaded subscriptions
        subscriptions = mqtt.get_subscriptions()
        logger.info(f"Loaded {len(subscriptions)} subscriptions from config:")
        for sub in subscriptions:
            logger.info(
                f"  - {sub['topic']} -> {sub['pipeline']} "
                f"(QoS {sub['qos']}, {sub['execution_mode']} mode)"
            )
        
        # You can still add more subscriptions programmatically
        await mqtt.subscribe(
            topic="runtime/+/data",
            pipeline_name="runtime_processor",
            qos=1,
            execution_mode="async"
        )
        
        # Start listener
        logger.info("Starting MQTT listener. Press Ctrl+C to stop...")
        await mqtt.start_listener(background=False)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Clean shutdown
        logger.info("Stopping MQTT plugin...")
        if 'mqtt' in locals():
            await mqtt.disconnect()
            
            # Save final configuration (including runtime additions)
            final_config_file = Path("final_mqtt_config.yml") 
            mqtt.save_config(final_config_file)
            logger.info(f"Saved final configuration: {final_config_file}")
        
        # Cleanup example config file
        if config_file.exists():
            config_file.unlink()
            logger.info(f"Cleaned up example config: {config_file}")
            
        logger.info("MQTT plugin stopped")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())