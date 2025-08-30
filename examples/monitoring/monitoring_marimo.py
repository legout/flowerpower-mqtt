import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Monitoring and Statistics Example

        This notebook demonstrates comprehensive monitoring capabilities for the FlowerPower MQTT Plugin, including real-time statistics tracking, performance metrics, and dynamic subscription management.

        ## Overview

        This example shows how to:
        - Create a custom monitoring class
        - Track real-time statistics and performance metrics
        - Monitor message processing rates and error rates
        - Manage subscriptions dynamically
        - Generate monitoring reports and summaries

        ## Prerequisites

        Make sure you have:
        - MQTT broker running
        - Redis server running (for job queue)
        - RQ worker running: `rq worker mqtt_pipelines --url redis://localhost:6379`
        - FlowerPower project set up
        - Required Python packages installed
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 1: Import Required Libraries

        Import the necessary libraries for monitoring and MQTT functionality.
        """
    )
    return


@app.cell
def _():
    import asyncio
    import logging
    import json
    from datetime import datetime
    from flowerpower_mqtt import MQTTPlugin

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return MQTTPlugin, asyncio, datetime, json, logger, logging


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 2: Create MQTT Monitor Class

        Define a comprehensive monitoring class that tracks MQTT plugin statistics.
        """
    )
    return


@app.cell
def _(MQTTPlugin, asyncio, datetime, logger):
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

    print("MQTTMonitor class defined!")
    return (MQTTMonitor,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 3: Create MQTT Plugin and Monitor

        Initialize the MQTT plugin with monitoring capabilities.
        """
    )
    return


@app.cell
def _(MQTTMonitor, MQTTPlugin):
    # Create plugin with monitoring-friendly configuration
    mqtt = MQTTPlugin(
        broker="localhost",
        port=1883,
        base_dir=".",
        use_job_queue=True,
        redis_url="redis://localhost:6379",
        client_id="flowerpower_monitoring_example"
    )

    # Create monitor instance
    monitor = MQTTMonitor(mqtt, interval=5)  # Monitor every 5 seconds

    print("MQTT Plugin and Monitor created!")
    return monitor, mqtt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 4: Connect to MQTT Broker

        Establish connection to the MQTT broker.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Connect to MQTT broker
    logger.info("Connecting to MQTT broker...")
    await mqtt.connect()
    logger.info("Connected successfully!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 5: Set Up Test Subscriptions

        Create various subscriptions to test monitoring with different QoS levels and execution modes.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
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
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 6: Start Monitoring

        Begin the background monitoring process.
        """
    )
    return


@app.cell
async def _(logger, monitor):
    # Start monitoring
    await monitor.start_monitoring()
    logger.info("Monitoring started!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 7: Start MQTT Listener

        Start the MQTT listener in background mode.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Start MQTT listener in background
    logger.info("Starting MQTT listener...")
    await mqtt.start_listener(background=True)
    logger.info("Background listener started!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 8: Demonstrate Dynamic Subscription Management

        Show how to add and remove subscriptions dynamically while monitoring.
        """
    )
    return


@app.cell
async def _(asyncio, logger, mqtt):
    # Simulate dynamic subscription management
    logger.info("Running monitoring example for 60 seconds...")

    for i in range(60):
        await asyncio.sleep(1)
    
        # Add subscription dynamically at 20 seconds
        if i == 20:
            logger.info("Adding dynamic subscription...")
            await mqtt.subscribe(
                "dynamic/test/+", 
                "dynamic_processor", 
                qos=1, 
                execution_mode="async"
            )
    
        # Remove subscription at 40 seconds
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
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 9: Generate Monitoring Summary

        Stop monitoring and generate a comprehensive summary report.
        """
    )
    return


@app.cell
async def _(logger, monitor):
    # Stop monitoring and generate summary
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
    return (summary,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 10: Save Monitoring Data

        Save the monitoring data to a JSON file for further analysis.
        """
    )
    return


@app.cell
def _(datetime, json, logger, monitor, summary):
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
    else:
        logger.info("No monitoring data to save")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 11: Clean Shutdown

        Properly stop the MQTT plugin and disconnect.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Clean shutdown
    logger.info("Stopping MQTT plugin...")
    await mqtt.stop_listener(timeout=5.0)
    await mqtt.disconnect()
    logger.info("MQTT plugin stopped")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Complete Example

        Here's the complete monitoring example in a single executable cell:
        """
    )
    return


@app.cell
def _(MQTTPlugin, asyncio, datetime, json, logging):
    logging.basicConfig(level=logging.INFO)
    logger_1 = logging.getLogger(__name__)

    class MQTTMonitor_1:
        """Helper class for monitoring MQTT plugin statistics."""

        def __init__(self, mqtt_plugin: MQTTPlugin, interval: int=10):
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
            logger_1.info(f'Started monitoring with {self.interval}s interval')

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
            logger_1.info('Stopped monitoring')

        async def _monitor_loop(self):
            """Main monitoring loop."""
            try:
                while self.monitoring:
                    await asyncio.sleep(self.interval)
                    if not self.monitoring:
                        break
                    stats = self.mqtt_plugin.get_statistics()
                    stats['timestamp'] = datetime.now().isoformat()
                    self.stats_history.append(stats)
                    if len(self.stats_history) > 100:
                        self.stats_history.pop(0)
                    self._log_stats(stats)
            except asyncio.CancelledError:
                logger_1.info('Monitor loop cancelled')

        def _log_stats(self, stats):
            """Log current statistics."""
            logger_1.info('=== MQTT Plugin Statistics ===')
            logger_1.info(f"Connected: {stats.get('connected', False)}")
            logger_1.info(f"Broker: {stats.get('broker', 'N/A')}")
            logger_1.info(f"Running: {stats.get('running', False)}")
            logger_1.info(f"Runtime: {stats.get('runtime_seconds', 0):.1f}s")
            logger_1.info(f"Messages: {stats.get('message_count', 0)}")
            logger_1.info(f"Pipelines: {stats.get('pipeline_count', 0)}")
            logger_1.info(f"Errors: {stats.get('error_count', 0)}")
            logger_1.info(f"Subscriptions: {stats.get('subscriptions_count', 0)}")
            logger_1.info(f"Job Queue: {stats.get('job_queue_enabled', False)}")
            if len(self.stats_history) >= 2:
                prev_stats = self.stats_history[-2]
                time_diff = (datetime.fromisoformat(stats['timestamp']) - datetime.fromisoformat(prev_stats['timestamp'])).total_seconds()
                if time_diff > 0:
                    msg_rate = (stats.get('message_count', 0) - prev_stats.get('message_count', 0)) / time_diff
                    pipe_rate = (stats.get('pipeline_count', 0) - prev_stats.get('pipeline_count', 0)) / time_diff
                    logger_1.info(f'Message rate: {msg_rate:.2f} msg/s')
                    logger_1.info(f'Pipeline rate: {pipe_rate:.2f} exec/s')
            logger_1.info('=' * 30)

        def get_summary(self):
            """Get monitoring summary."""
            if not self.stats_history:
                return {'message': 'No statistics available'}
            latest = self.stats_history[-1]
            return {'monitoring_duration': len(self.stats_history) * self.interval, 'total_messages': latest.get('message_count', 0), 'total_pipelines': latest.get('pipeline_count', 0), 'total_errors': latest.get('error_count', 0), 'average_message_rate': latest.get('message_count', 0) / max(latest.get('runtime_seconds', 1), 1), 'error_rate': latest.get('error_count', 0) / max(latest.get('message_count', 1), 1), 'uptime': latest.get('runtime_seconds', 0)}

    async def main():
        """Monitoring and statistics example."""
        mqtt = MQTTPlugin(broker='localhost', port=1883, base_dir='.', use_job_queue=True, redis_url='redis://localhost:6379', client_id='flowerpower_monitoring_example')
        monitor = MQTTMonitor_1(mqtt, interval=5)
        try:
            logger_1.info('Connecting to MQTT broker...')
            await mqtt.connect()
            subscriptions = [('test/messages/+', 'test_processor', 0, 'async'), ('sensors/+/data', 'sensor_processor', 1, 'async'), ('alerts/+', 'alert_processor', 2, 'sync'), ('logs/+/info', 'log_processor', 0, 'async'), ('events/+/user', 'user_event_processor', 1, 'mixed')]
            for topic, pipeline, qos, mode in subscriptions:
                await mqtt.subscribe(topic, pipeline, qos, mode)
                logger_1.info(f'Subscribed: {topic} -> {pipeline} (QoS {qos}, {mode})')
            subs = mqtt.get_subscriptions()
            logger_1.info(f'Total subscriptions: {len(subs)}')
            await monitor.start_monitoring()
            logger_1.info('Starting MQTT listener...')
            await mqtt.start_listener(background=True)
            logger_1.info('Running monitoring example for 60 seconds...')
            for i in range(60):
                await asyncio.sleep(1)
                if i == 20:
                    logger_1.info('Adding dynamic subscription...')
                    await mqtt.subscribe('dynamic/test/+', 'dynamic_processor', qos=1, execution_mode='async')
                elif i == 40:
                    logger_1.info('Removing dynamic subscription...')
                    await mqtt.unsubscribe('dynamic/test/+')
                if i % 15 == 0 and i > 0:
                    logger_1.info('=== Subscription Details ===')
                    current_subs = mqtt.get_subscriptions()
                    for sub in current_subs:
                        logger_1.info(f"  {sub['topic']}: {sub.get('message_count', 0)} messages, {sub.get('error_count', 0)} errors, QoS {sub['qos']}, {sub['execution_mode']} mode")
                    logger_1.info('=' * 28)
        except KeyboardInterrupt:
            logger_1.info('Received keyboard interrupt')
        except Exception as e:
            logger_1.error(f'Error: {e}')
        finally:
            logger_1.info('Stopping monitoring and MQTT plugin...')
            await monitor.stop_monitoring()
            summary = monitor.get_summary()
            logger_1.info('=== Monitoring Summary ===')
            logger_1.info(f"Monitoring duration: {summary.get('monitoring_duration', 0)}s")
            logger_1.info(f"Total messages: {summary.get('total_messages', 0)}")
            logger_1.info(f"Total pipeline executions: {summary.get('total_pipelines', 0)}")
            logger_1.info(f"Total errors: {summary.get('total_errors', 0)}")
            logger_1.info(f"Average message rate: {summary.get('average_message_rate', 0):.2f} msg/s")
            logger_1.info(f"Error rate: {summary.get('error_rate', 0):.4f}")
            logger_1.info(f"Total uptime: {summary.get('uptime', 0):.1f}s")
            logger_1.info('=' * 26)
            await mqtt.stop_listener(timeout=5.0)
            await mqtt.disconnect()
            if monitor.stats_history:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'mqtt_stats_{timestamp}.json'
                with open(filename, 'w') as f:
                    json.dump({'summary': summary, 'stats_history': monitor.stats_history}, f, indent=2)
                logger_1.info(f'Monitoring data saved to: {filename}')
            logger_1.info('MQTT plugin stopped')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Key Features Demonstrated

        - **Real-time Monitoring**: Continuous tracking of MQTT plugin statistics
        - **Performance Metrics**: Message rates, error rates, and processing times
        - **Dynamic Management**: Adding and removing subscriptions at runtime
        - **Historical Data**: Storing and analyzing monitoring history
        - **Comprehensive Reporting**: Detailed summaries and JSON export
        - **Background Processing**: Non-blocking monitoring with asyncio tasks

        ## Notes

        - Make sure Redis is running and an RQ worker is started
        - The monitoring interval can be adjusted for different use cases
        - Statistics are kept in memory (last 100 entries) to prevent memory issues
        - The monitoring data is automatically saved to a timestamped JSON file
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
