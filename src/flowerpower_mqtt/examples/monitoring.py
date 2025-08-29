"""
Monitoring and statistics example for FlowerPower MQTT Plugin.

This example demonstrates how to monitor plugin performance,
track statistics, and manage subscriptions dynamically.
"""

import asyncio
import logging
import json
from datetime import datetime
from flowerpower_mqtt import MQTTPlugin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MQTTMonitor:
    """Helper class for monitoring MQTT plugin statistics."""
    
    def __init__(self, mqtt_plugin: MQTTPlugin, interval: int = 10):
        self.mqtt_plugin = mqtt_plugin
        self.interval = interval
        self.monitoring = False
        self.monitor_task = None
        self.stats_history = []
    
    async def start_monitoring(self):
        """Start background monitoring task."""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Started monitoring with {self.interval}s interval")
    
    async def stop_monitoring(self):
        """Stop background monitoring task."""
        if not self.monitoring:
            return
            
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped monitoring")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        try:
            while self.monitoring:
                await asyncio.sleep(self.interval)
                
                if not self.monitoring:
                    break
                    
                # Collect current statistics
                stats = self.mqtt_plugin.get_statistics()
                stats['timestamp'] = datetime.now().isoformat()
                
                # Store in history
                self.stats_history.append(stats)
                
                # Keep only last 100 entries
                if len(self.stats_history) > 100:
                    self.stats_history.pop(0)
                
                # Log current stats
                self._log_stats(stats)
                
        except asyncio.CancelledError:
            logger.info("Monitor loop cancelled")
    
    def _log_stats(self, stats):
        """Log current statistics."""
        logger.info("=== MQTT Plugin Statistics ===")
        logger.info(f"Connected: {stats.get('connected', False)}")
        logger.info(f"Broker: {stats.get('broker', 'N/A')}")
        logger.info(f"Running: {stats.get('running', False)}")
        logger.info(f"Runtime: {stats.get('runtime_seconds', 0):.1f}s")
        logger.info(f"Messages: {stats.get('message_count', 0)}")
        logger.info(f"Pipelines: {stats.get('pipeline_count', 0)}")
        logger.info(f"Errors: {stats.get('error_count', 0)}")
        logger.info(f"Subscriptions: {stats.get('subscriptions_count', 0)}")
        logger.info(f"Job Queue: {stats.get('job_queue_enabled', False)}")
        
        # Calculate rates if we have history
        if len(self.stats_history) >= 2:
            prev_stats = self.stats_history[-2]
            time_diff = (
                datetime.fromisoformat(stats['timestamp']) - 
                datetime.fromisoformat(prev_stats['timestamp'])
            ).total_seconds()
            
            if time_diff > 0:
                msg_rate = (
                    stats.get('message_count', 0) - 
                    prev_stats.get('message_count', 0)
                ) / time_diff
                
                pipe_rate = (
                    stats.get('pipeline_count', 0) - 
                    prev_stats.get('pipeline_count', 0)
                ) / time_diff
                
                logger.info(f"Message rate: {msg_rate:.2f} msg/s")
                logger.info(f"Pipeline rate: {pipe_rate:.2f} exec/s")
        
        logger.info("=" * 30)
    
    def get_summary(self):
        """Get monitoring summary."""
        if not self.stats_history:
            return {"message": "No statistics available"}
        
        latest = self.stats_history[-1]
        return {
            "monitoring_duration": len(self.stats_history) * self.interval,
            "total_messages": latest.get('message_count', 0),
            "total_pipelines": latest.get('pipeline_count', 0),
            "total_errors": latest.get('error_count', 0),
            "average_message_rate": latest.get('message_count', 0) / max(latest.get('runtime_seconds', 1), 1),
            "error_rate": latest.get('error_count', 0) / max(latest.get('message_count', 1), 1),
            "uptime": latest.get('runtime_seconds', 0)
        }


async def main():
    """Monitoring and statistics example."""
    
    # Create plugin with monitoring-friendly configuration
    mqtt = MQTTPlugin(
        broker="localhost",
        port=1883,
        base_dir=".",
        use_job_queue=True,
        redis_url="redis://localhost:6379",
        client_id="flowerpower_monitoring_example"
    )
    
    # Create monitor
    monitor = MQTTMonitor(mqtt, interval=5)  # Monitor every 5 seconds
    
    try:
        # Connect to MQTT broker
        logger.info("Connecting to MQTT broker...")
        await mqtt.connect()
        
        # Set up various subscriptions for testing
        subscriptions = [
            ("test/messages/+", "test_processor", 0, "async"),
            ("sensors/+/data", "sensor_processor", 1, "async"), 
            ("alerts/+", "alert_processor", 2, "sync"),
            ("logs/+/info", "log_processor", 0, "async"),
            ("events/+/user", "user_event_processor", 1, "mixed")
        ]
        
        for topic, pipeline, qos, mode in subscriptions:
            await mqtt.subscribe(topic, pipeline, qos, mode)
            logger.info(f"Subscribed: {topic} -> {pipeline} (QoS {qos}, {mode})")
        
        # Display initial subscription information
        subs = mqtt.get_subscriptions()
        logger.info(f"Total subscriptions: {len(subs)}")
        
        # Start monitoring
        await monitor.start_monitoring()
        
        # Start MQTT listener in background
        logger.info("Starting MQTT listener...")
        await mqtt.start_listener(background=True)
        
        # Simulate some dynamic subscription management
        logger.info("Running monitoring example for 60 seconds...")
        
        for i in range(60):
            await asyncio.sleep(1)
            
            # Add/remove subscriptions dynamically for testing
            if i == 20:
                logger.info("Adding dynamic subscription...")
                await mqtt.subscribe(
                    "dynamic/test/+", 
                    "dynamic_processor", 
                    qos=1, 
                    execution_mode="async"
                )
            
            elif i == 40:
                logger.info("Removing dynamic subscription...")
                await mqtt.unsubscribe("dynamic/test/+")
            
            # Show detailed subscription stats every 15 seconds
            if i % 15 == 0 and i > 0:
                logger.info("=== Subscription Details ===")
                current_subs = mqtt.get_subscriptions()
                for sub in current_subs:
                    logger.info(
                        f"  {sub['topic']}: "
                        f"{sub.get('message_count', 0)} messages, "
                        f"{sub.get('error_count', 0)} errors, "
                        f"QoS {sub['qos']}, "
                        f"{sub['execution_mode']} mode"
                    )
                logger.info("=" * 28)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Clean shutdown with detailed final statistics
        logger.info("Stopping monitoring and MQTT plugin...")
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        # Show monitoring summary
        summary = monitor.get_summary()
        logger.info("=== Monitoring Summary ===")
        logger.info(f"Monitoring duration: {summary.get('monitoring_duration', 0)}s")
        logger.info(f"Total messages: {summary.get('total_messages', 0)}")
        logger.info(f"Total pipeline executions: {summary.get('total_pipelines', 0)}")
        logger.info(f"Total errors: {summary.get('total_errors', 0)}")
        logger.info(f"Average message rate: {summary.get('average_message_rate', 0):.2f} msg/s")
        logger.info(f"Error rate: {summary.get('error_rate', 0):.4f}")
        logger.info(f"Total uptime: {summary.get('uptime', 0):.1f}s")
        logger.info("=" * 26)
        
        # Stop MQTT plugin
        await mqtt.stop_listener(timeout=5.0)
        await mqtt.disconnect()
        
        # Save monitoring data to file
        if monitor.stats_history:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mqtt_stats_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump({
                    'summary': summary,
                    'stats_history': monitor.stats_history
                }, f, indent=2)
            
            logger.info(f"Monitoring data saved to: {filename}")
        
        logger.info("MQTT plugin stopped")


if __name__ == "__main__":
    print("This example demonstrates monitoring and statistics collection.")
    print("It will show real-time statistics every 5 seconds and detailed")
    print("subscription information every 15 seconds.")
    print()
    
    # Run the example
    asyncio.run(main())