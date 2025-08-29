"""
Multiple QoS levels example for FlowerPower MQTT Plugin.

This example demonstrates how to use different QoS levels
for different types of messages and use cases.
"""

import asyncio
import logging
from flowerpower_mqtt import MQTTPlugin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Example showing different QoS levels and their use cases."""
    
    # Create plugin instance
    mqtt = MQTTPlugin(
        broker="localhost",  # Change to your MQTT broker
        port=1883,
        base_dir=".",  # FlowerPower project directory
        use_job_queue=True,  # Enable for better performance with high volume
        redis_url="redis://localhost:6379",
        client_id="flowerpower_qos_example"
    )
    
    try:
        # Connect to MQTT broker
        logger.info("Connecting to MQTT broker...")
        await mqtt.connect()
        
        # QoS 0: Fire-and-forget (best for high-volume, non-critical data)
        # Use for: Debug logs, non-critical telemetry, high-frequency sensor data
        await mqtt.subscribe(
            topic="logs/debug/+",
            pipeline_name="debug_log_processor",
            qos=0,  # At most once delivery
            execution_mode="async"  # Process in background
        )
        
        await mqtt.subscribe(
            topic="telemetry/+/heartbeat",
            pipeline_name="heartbeat_processor", 
            qos=0,  # Fire-and-forget for frequent heartbeats
            execution_mode="async"
        )
        
        # QoS 1: At-least-once delivery (good for important events)
        # Use for: Business events, important sensor readings, user actions
        await mqtt.subscribe(
            topic="sensors/+/temperature",
            pipeline_name="temperature_processor",
            qos=1,  # At least once delivery
            execution_mode="async"
        )
        
        await mqtt.subscribe(
            topic="events/user/+/login", 
            pipeline_name="user_login_processor",
            qos=1,  # Important user events
            execution_mode="async" 
        )
        
        await mqtt.subscribe(
            topic="orders/+/created",
            pipeline_name="order_created_processor",
            qos=1,  # Business-critical events
            execution_mode="async"
        )
        
        # QoS 2: Exactly-once delivery (critical business processes)
        # Use for: Financial transactions, critical alerts, regulatory data
        await mqtt.subscribe(
            topic="payments/+/completed",
            pipeline_name="payment_completion_processor",
            qos=2,  # Exactly once for financial data
            execution_mode="sync"  # Process immediately
        )
        
        await mqtt.subscribe(
            topic="alerts/critical/+",
            pipeline_name="critical_alert_handler",
            qos=2,  # Critical alerts must be processed
            execution_mode="sync"  # Immediate processing
        )
        
        await mqtt.subscribe(
            topic="compliance/audit/+",
            pipeline_name="audit_log_processor",
            qos=2,  # Regulatory compliance data
            execution_mode="sync"
        )
        
        # Mixed mode: Let QoS level determine execution mode
        # QoS 2 -> sync, QoS 0/1 -> async
        await mqtt.subscribe(
            topic="mixed/data/+",
            pipeline_name="mixed_data_processor",
            qos=1,  # Will be processed async due to mixed mode
            execution_mode="mixed"
        )
        
        # Display subscription summary
        subscriptions = mqtt.get_subscriptions()
        logger.info(f"Configured {len(subscriptions)} subscriptions with different QoS levels:")
        
        qos_counts = {0: 0, 1: 0, 2: 0}
        for sub in subscriptions:
            qos_counts[sub['qos']] += 1
            logger.info(
                f"  - {sub['topic']} -> {sub['pipeline']} "
                f"(QoS {sub['qos']}, {sub['execution_mode']} mode)"
            )
        
        logger.info(f"QoS distribution: QoS 0: {qos_counts[0]}, QoS 1: {qos_counts[1]}, QoS 2: {qos_counts[2]}")
        
        # Start listener
        logger.info("Starting MQTT listener. Press Ctrl+C to stop...")
        await mqtt.start_listener(background=True)
        
        # Monitor and display statistics periodically
        logger.info("Monitoring message processing. Statistics will be shown every 15 seconds...")
        
        for i in range(300):  # Run for 5 minutes
            await asyncio.sleep(1)
            
            if i % 15 == 0:  # Show stats every 15 seconds
                stats = mqtt.get_statistics()
                logger.info(
                    f"=== Statistics (after {i}s) ==="
                )
                logger.info(
                    f"Messages processed: {stats.get('message_count', 0)}"
                )
                logger.info(
                    f"Pipeline executions: {stats.get('pipeline_count', 0)}"
                )
                logger.info(
                    f"Errors: {stats.get('error_count', 0)}"
                )
                logger.info(
                    f"Job queue enabled: {stats.get('job_queue_enabled', False)}"
                )
                
                # Show individual subscription stats
                current_subs = mqtt.get_subscriptions()
                for sub in current_subs:
                    if sub.get('message_count', 0) > 0:
                        logger.info(
                            f"  {sub['topic']}: {sub.get('message_count', 0)} messages "
                            f"(QoS {sub['qos']})"
                        )
                
                logger.info("=" * 40)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Clean shutdown
        logger.info("Stopping MQTT plugin...")
        await mqtt.stop_listener(timeout=10.0)
        await mqtt.disconnect()
        
        # Show final statistics
        try:
            stats = mqtt.get_statistics()
            logger.info("=== Final Statistics ===")
            logger.info(f"Total messages processed: {stats.get('message_count', 0)}")
            logger.info(f"Total pipeline executions: {stats.get('pipeline_count', 0)}")
            logger.info(f"Total errors: {stats.get('error_count', 0)}")
            logger.info("========================")
        except:
            pass
        
        logger.info("MQTT plugin stopped")


if __name__ == "__main__":
    print("QoS Level Guide:")
    print("QoS 0: Fire-and-forget - Fast, no delivery guarantee")
    print("QoS 1: At-least-once - Reliable, may get duplicates") 
    print("QoS 2: Exactly-once - Reliable, no duplicates (slower)")
    print()
    
    # Run the example
    asyncio.run(main())