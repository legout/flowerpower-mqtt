"""
Asynchronous processing example with RQ job queue.

This example demonstrates how to use the plugin with RQ for background
pipeline execution, allowing for scalable message processing.
"""

import asyncio
import logging
from flowerpower_mqtt import MQTTPlugin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Asynchronous MQTT plugin usage with RQ job queue."""
    
    # Create plugin with job queue enabled
    mqtt = MQTTPlugin(
        broker="localhost",  # Change to your MQTT broker
        port=1883,
        base_dir=".",  # FlowerPower project directory
        use_job_queue=True,
        redis_url="redis://localhost:6379",
        client_id="flowerpower_async_example"
    )
    
    try:
        # Connect to MQTT broker
        logger.info("Connecting to MQTT broker with job queue enabled...")
        await mqtt.connect()
        
        # Subscribe with different execution modes
        
        # High-volume data: process asynchronously
        await mqtt.subscribe(
            topic="sensors/+/data", 
            pipeline_name="sensor_data_processor",
            qos=1,
            execution_mode="async"
        )
        
        # Critical alerts: process synchronously
        await mqtt.subscribe(
            topic="alerts/critical", 
            pipeline_name="critical_alert_handler",
            qos=2,
            execution_mode="sync"
        )
        
        # Mixed mode: QoS-based routing
        await mqtt.subscribe(
            topic="mixed/topic",
            pipeline_name="mixed_processor",
            qos=1,
            execution_mode="mixed"
        )
        
        # Bulk subscription example
        bulk_subscriptions = [
            {
                "topic": "factory/+/temperature",
                "pipeline": "factory_temp_monitor",
                "qos": 1,
                "execution_mode": "async"
            },
            {
                "topic": "factory/+/pressure",
                "pipeline": "factory_pressure_monitor", 
                "qos": 1,
                "execution_mode": "async"
            }
        ]
        
        await mqtt.subscribe_bulk(bulk_subscriptions)
        
        # Start listener in background
        logger.info("Starting MQTT listener in background...")
        await mqtt.start_listener(background=True)
        
        # Monitor statistics
        logger.info("Monitoring for 60 seconds. Press Ctrl+C to stop early...")
        for i in range(60):
            await asyncio.sleep(1)
            
            if i % 10 == 0:  # Print stats every 10 seconds
                stats = mqtt.get_statistics()
                logger.info(
                    f"Stats - Messages: {stats.get('message_count', 0)}, "
                    f"Pipelines: {stats.get('pipeline_count', 0)}, "
                    f"Errors: {stats.get('error_count', 0)}"
                )
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Clean shutdown
        logger.info("Stopping MQTT plugin...")
        await mqtt.stop_listener(timeout=5.0)
        await mqtt.disconnect()
        logger.info("MQTT plugin stopped")


if __name__ == "__main__":
    # Note: Make sure to start an RQ worker in a separate terminal:
    # rq worker mqtt_pipelines --url redis://localhost:6379
    
    print("Make sure to start an RQ worker before running this example:")
    print("rq worker mqtt_pipelines --url redis://localhost:6379")
    print()
    
    # Run the example
    asyncio.run(main())