import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Multiple QoS Levels Example

        This notebook demonstrates how to use different QoS (Quality of Service) levels for different types of messages and use cases with the FlowerPower MQTT Plugin.

        ## Overview

        This example shows how to:
        - Configure different QoS levels (0, 1, 2) for various message types
        - Choose appropriate execution modes for different QoS levels
        - Monitor message processing statistics by QoS level
        - Understand when to use each QoS level

        ## QoS Levels Explained

        - **QoS 0 (At most once)**: Fire-and-forget delivery, fastest but no guarantee
        - **QoS 1 (At least once)**: Guaranteed delivery, may receive duplicates
        - **QoS 2 (Exactly once)**: Guaranteed delivery with no duplicates, slowest

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

        Import the necessary libraries for MQTT functionality with different QoS levels.
        """
    )
    return


@app.cell
def _():
    import asyncio
    import logging
    from flowerpower_mqtt import MQTTPlugin

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return MQTTPlugin, asyncio, logger, logging


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 2: Create MQTT Plugin Instance

        Create an MQTTPlugin instance with job queue enabled for better performance.
        """
    )
    return


@app.cell
def _(MQTTPlugin):
    # Create plugin instance with job queue
    mqtt = MQTTPlugin(
        broker="localhost",  # Change to your MQTT broker
        port=1883,
        base_dir=".",  # FlowerPower project directory
        use_job_queue=True,  # Enable for better performance with high volume
        redis_url="redis://localhost:6379",
        client_id="flowerpower_qos_example"
    )

    print("MQTT Plugin created with job queue support!")
    return (mqtt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 3: Connect to MQTT Broker

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
        ## Step 4: QoS 0 - Fire-and-Forget Subscriptions

        Subscribe to topics that use QoS 0 for high-volume, non-critical data.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # QoS 0: Fire-and-forget (best for high-volume, non-critical data)
    # Use for: Debug logs, non-critical telemetry, high-frequency sensor data

    await mqtt.subscribe(
        topic="logs/debug/+",
        pipeline_name="debug_log_processor",
        qos=0,  # At most once delivery
        execution_mode="async"  # Process in background
    )
    logger.info("Subscribed to debug logs (QoS 0)")

    await mqtt.subscribe(
        topic="telemetry/+/heartbeat",
        pipeline_name="heartbeat_processor", 
        qos=0,  # Fire-and-forget for frequent heartbeats
        execution_mode="async"
    )
    logger.info("Subscribed to heartbeat telemetry (QoS 0)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 5: QoS 1 - At-Least-Once Subscriptions

        Subscribe to topics that require reliable delivery but can handle occasional duplicates.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # QoS 1: At-least-once delivery (good for important events)
    # Use for: Business events, important sensor readings, user actions

    await mqtt.subscribe(
        topic="sensors/+/temperature",
        pipeline_name="temperature_processor",
        qos=1,  # At least once delivery
        execution_mode="async"
    )
    logger.info("Subscribed to temperature sensors (QoS 1)")

    await mqtt.subscribe(
        topic="events/user/+/login", 
        pipeline_name="user_login_processor",
        qos=1,  # Important user events
        execution_mode="async" 
    )
    logger.info("Subscribed to user login events (QoS 1)")

    await mqtt.subscribe(
        topic="orders/+/created",
        pipeline_name="order_created_processor",
        qos=1,  # Business-critical events
        execution_mode="async"
    )
    logger.info("Subscribed to order creation events (QoS 1)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 6: QoS 2 - Exactly-Once Subscriptions

        Subscribe to topics that require guaranteed delivery with no duplicates.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # QoS 2: Exactly-once delivery (critical business processes)
    # Use for: Financial transactions, critical alerts, regulatory data

    await mqtt.subscribe(
        topic="payments/+/completed",
        pipeline_name="payment_completion_processor",
        qos=2,  # Exactly once for financial data
        execution_mode="sync"  # Process immediately
    )
    logger.info("Subscribed to payment completions (QoS 2)")

    await mqtt.subscribe(
        topic="alerts/critical/+",
        pipeline_name="critical_alert_handler",
        qos=2,  # Critical alerts must be processed
        execution_mode="sync"  # Immediate processing
    )
    logger.info("Subscribed to critical alerts (QoS 2)")

    await mqtt.subscribe(
        topic="compliance/audit/+",
        pipeline_name="audit_log_processor",
        qos=2,  # Regulatory compliance data
        execution_mode="sync"
    )
    logger.info("Subscribed to audit logs (QoS 2)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 7: Mixed Mode Subscription

        Demonstrate mixed execution mode where QoS level determines processing strategy.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Mixed mode: Let QoS level determine execution mode
    # QoS 2 -> sync, QoS 0/1 -> async
    await mqtt.subscribe(
        topic="mixed/data/+",
        pipeline_name="mixed_data_processor",
        qos=1,  # Will be processed async due to mixed mode
        execution_mode="mixed"
    )
    logger.info("Subscribed to mixed data (QoS 1, mixed mode)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 8: Display Subscription Summary

        Show the configured subscriptions and their QoS distribution.
        """
    )
    return


@app.cell
def _(logger, mqtt):
    subscriptions = mqtt.get_subscriptions()
    logger.info(f'Configured {len(subscriptions)} subscriptions with different QoS levels:')
    qos_counts = {0: 0, 1: 0, 2: 0}
    for _sub in subscriptions:
        qos_counts[_sub['qos']] = qos_counts[_sub['qos']] + 1
        logger.info(f"  - {_sub['topic']} -> {_sub['pipeline']} (QoS {_sub['qos']}, {_sub['execution_mode']} mode)")
    logger.info(f'QoS distribution: QoS 0: {qos_counts[0]}, QoS 1: {qos_counts[1]}, QoS 2: {qos_counts[2]}')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 9: Start MQTT Listener

        Start the MQTT listener to begin processing messages with different QoS levels.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Start listener
    logger.info("Starting MQTT listener. Press Ctrl+C to stop...")
    await mqtt.start_listener(background=True)
    logger.info("Background listener started!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 10: Monitor Processing Statistics

        Monitor message processing and display statistics periodically.
        """
    )
    return


@app.cell
async def _(asyncio, logger, mqtt):
    logger.info('Monitoring message processing. Statistics will be shown every 15 seconds...')
    for i in range(300):
        await asyncio.sleep(1)
        if i % 15 == 0:
            _stats = mqtt.get_statistics()
            logger.info(f'=== Statistics (after {i}s) ===')
            logger.info(f"Messages processed: {_stats.get('message_count', 0)}")
            logger.info(f"Pipeline executions: {_stats.get('pipeline_count', 0)}")
            logger.info(f"Errors: {_stats.get('error_count', 0)}")
            logger.info(f"Job queue enabled: {_stats.get('job_queue_enabled', False)}")
            current_subs = mqtt.get_subscriptions()
            for _sub in current_subs:
                if _sub.get('message_count', 0) > 0:
                    logger.info(f"  {_sub['topic']}: {_sub.get('message_count', 0)} messages (QoS {_sub['qos']})")
            logger.info('=' * 40)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 11: Clean Shutdown

        Properly stop the listener and disconnect from the broker.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    logger.info('Stopping MQTT plugin...')
    await mqtt.stop_listener(timeout=10.0)
    await mqtt.disconnect()
    logger.info('MQTT plugin stopped')
    try:
        _stats = mqtt.get_statistics()
        logger.info('=== Final Statistics ===')
        logger.info(f"Total messages processed: {_stats.get('message_count', 0)}")
        logger.info(f"Total pipeline executions: {_stats.get('pipeline_count', 0)}")
        logger.info(f"Total errors: {_stats.get('error_count', 0)}")
        logger.info('========================')
    except:
        pass
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Complete Example

        Here's the complete QoS example in a single executable cell:
        """
    )
    return


@app.cell
def _(MQTTPlugin, asyncio, logging):
    logging.basicConfig(level=logging.INFO)
    logger_1 = logging.getLogger(__name__)

    async def main():
        """Example showing different QoS levels and their use cases."""
        mqtt = MQTTPlugin(broker='localhost', port=1883, base_dir='.', use_job_queue=True, redis_url='redis://localhost:6379', client_id='flowerpower_qos_example')
        try:
            logger_1.info('Connecting to MQTT broker...')
            await mqtt.connect()
            await mqtt.subscribe(topic='logs/debug/+', pipeline_name='debug_log_processor', qos=0, execution_mode='async')
            await mqtt.subscribe(topic='telemetry/+/heartbeat', pipeline_name='heartbeat_processor', qos=0, execution_mode='async')
            await mqtt.subscribe(topic='sensors/+/temperature', pipeline_name='temperature_processor', qos=1, execution_mode='async')
            await mqtt.subscribe(topic='events/user/+/login', pipeline_name='user_login_processor', qos=1, execution_mode='async')
            await mqtt.subscribe(topic='orders/+/created', pipeline_name='order_created_processor', qos=1, execution_mode='async')
            await mqtt.subscribe(topic='payments/+/completed', pipeline_name='payment_completion_processor', qos=2, execution_mode='sync')
            await mqtt.subscribe(topic='alerts/critical/+', pipeline_name='critical_alert_handler', qos=2, execution_mode='sync')
            await mqtt.subscribe(topic='compliance/audit/+', pipeline_name='audit_log_processor', qos=2, execution_mode='sync')
            await mqtt.subscribe(topic='mixed/data/+', pipeline_name='mixed_data_processor', qos=1, execution_mode='mixed')
            subscriptions = mqtt.get_subscriptions()
            logger_1.info(f'Configured {len(subscriptions)} subscriptions with different QoS levels:')
            qos_counts = {0: 0, 1: 0, 2: 0}
            for _sub in subscriptions:
                qos_counts[_sub['qos']] = qos_counts[_sub['qos']] + 1
                logger_1.info(f"  - {_sub['topic']} -> {_sub['pipeline']} (QoS {_sub['qos']}, {_sub['execution_mode']} mode)")
            logger_1.info(f'QoS distribution: QoS 0: {qos_counts[0]}, QoS 1: {qos_counts[1]}, QoS 2: {qos_counts[2]}')
            logger_1.info('Starting MQTT listener. Press Ctrl+C to stop...')
            await mqtt.start_listener(background=True)
            logger_1.info('Monitoring message processing. Statistics will be shown every 15 seconds...')
            for i in range(300):
                await asyncio.sleep(1)
                if i % 15 == 0:
                    _stats = mqtt.get_statistics()
                    logger_1.info(f'=== Statistics (after {i}s) ===')
                    logger_1.info(f"Messages processed: {_stats.get('message_count', 0)}")
                    logger_1.info(f"Pipeline executions: {_stats.get('pipeline_count', 0)}")
                    logger_1.info(f"Errors: {_stats.get('error_count', 0)}")
                    logger_1.info(f"Job queue enabled: {_stats.get('job_queue_enabled', False)}")
                    current_subs = mqtt.get_subscriptions()
                    for _sub in current_subs:
                        if _sub.get('message_count', 0) > 0:
                            logger_1.info(f"  {_sub['topic']}: {_sub.get('message_count', 0)} messages (QoS {_sub['qos']})")
                    logger_1.info('=' * 40)
        except KeyboardInterrupt:
            logger_1.info('Received keyboard interrupt')
        except Exception as e:
            logger_1.error(f'Error: {e}')
        finally:
            logger_1.info('Stopping MQTT plugin...')
            await mqtt.stop_listener(timeout=10.0)
            await mqtt.disconnect()
            try:
                _stats = mqtt.get_statistics()
                logger_1.info('=== Final Statistics ===')
                logger_1.info(f"Total messages processed: {_stats.get('message_count', 0)}")
                logger_1.info(f"Total pipeline executions: {_stats.get('pipeline_count', 0)}")
                logger_1.info(f"Total errors: {_stats.get('error_count', 0)}")
                logger_1.info('========================')
            except:
                pass
            logger_1.info('MQTT plugin stopped')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## QoS Level Summary

        ### QoS 0 (At most once)
        - **Use case**: High-volume, non-critical data
        - **Examples**: Debug logs, telemetry, heartbeats
        - **Advantages**: Fastest, lowest overhead
        - **Trade-offs**: No delivery guarantee, messages may be lost

        ### QoS 1 (At least once)
        - **Use case**: Important events that can handle duplicates
        - **Examples**: Sensor readings, user actions, business events
        - **Advantages**: Reliable delivery
        - **Trade-offs**: May receive duplicate messages

        ### QoS 2 (Exactly once)
        - **Use case**: Critical business processes
        - **Examples**: Financial transactions, critical alerts, regulatory data
        - **Advantages**: Guaranteed delivery with no duplicates
        - **Trade-offs**: Slower, higher overhead

        ## Best Practices

        - Use QoS 0 for high-frequency, low-importance data
        - Use QoS 1 for most business applications
        - Reserve QoS 2 for mission-critical operations
        - Consider execution mode: sync for QoS 2, async for QoS 0/1
        - Monitor performance to ensure QoS levels meet requirements
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
