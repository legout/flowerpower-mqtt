"""
Basic usage example for FlowerPower MQTT Plugin.

This example demonstrates simple synchronous usage where MQTT messages
trigger immediate pipeline execution.
"""

import asyncio
import logging
from flowerpower_mqtt import MQTTPlugin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Basic synchronous MQTT plugin usage."""
    
    # Create plugin instance
    mqtt = MQTTPlugin(
        broker="localhost",  # Change to your MQTT broker
        port=1883,
        base_dir=".",  # FlowerPower project directory
        client_id="flowerpower_basic_example"
    )
    
    try:
        # Connect to MQTT broker
        logger.info("Connecting to MQTT broker...")
        await mqtt.connect()
        
        # Subscribe to topics
        await mqtt.subscribe(
            topic="sensors/temperature", 
            pipeline_name="temperature_processor",
            qos=1
        )
        
        await mqtt.subscribe(
            topic="sensors/humidity",
            pipeline_name="humidity_processor", 
            qos=0
        )
        
        # Start listening for messages (blocks until Ctrl+C)
        logger.info("Starting MQTT listener. Press Ctrl+C to stop...")
        await mqtt.start_listener(background=False)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Clean shutdown
        logger.info("Stopping MQTT plugin...")
        await mqtt.disconnect()
        logger.info("MQTT plugin stopped")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())