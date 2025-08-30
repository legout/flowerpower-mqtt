import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Asynchronous Processing with RQ Job Queue

        This notebook demonstrates how to use the FlowerPower MQTT Plugin with RQ (Redis Queue) for background pipeline execution, enabling scalable message processing.

        ## Overview

        This example shows how to:
        - Enable RQ job queue for background processing
        - Use different execution modes (sync, async, mixed)
        - Subscribe to topics with various QoS levels
        - Monitor processing statistics
        - Handle bulk subscriptions

        ## Prerequisites

        Make sure you have:
        - MQTT broker running
        - Redis server running
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

        Import the necessary libraries for MQTT plugin with job queue support.
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
        ## Step 2: Create MQTT Plugin with Job Queue

        Create an MQTTPlugin instance with RQ job queue enabled for background processing.
        """
    )
    return


@app.cell
def _(MQTTPlugin):
    # Create plugin with job queue enabled
    mqtt = MQTTPlugin(
        broker="localhost",  # Change to your MQTT broker
        port=1883,
        base_dir=".",  # FlowerPower project directory
        use_job_queue=True,  # Enable background processing
        redis_url="redis://localhost:6379",  # Redis for job queue
        client_id="flowerpower_async_example"
    )

    print("MQTT Plugin with job queue created!")
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
    logger.info("Connecting to MQTT broker with job queue enabled...")
    await mqtt.connect()
    logger.info("Connected successfully!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 4: Subscribe with Different Execution Modes

        Subscribe to topics with different execution modes to demonstrate various processing strategies.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # High-volume sensor data: process asynchronously
    await mqtt.subscribe(
        topic="sensors/+/data", 
        pipeline_name="sensor_data_processor",
        qos=1,
        execution_mode="async"  # Background processing
    )
    logger.info("Subscribed to sensor data topic (async mode)")

    # Critical alerts: process synchronously
    await mqtt.subscribe(
        topic="alerts/critical", 
        pipeline_name="critical_alert_handler",
        qos=2,  # Highest QoS for critical data
        execution_mode="sync"  # Immediate processing
    )
    logger.info("Subscribed to critical alerts topic (sync mode)")

    # Mixed mode: QoS-based routing
    await mqtt.subscribe(
        topic="mixed/topic",
        pipeline_name="mixed_processor",
        qos=1,
        execution_mode="mixed"  # QoS determines processing
    )
    logger.info("Subscribed to mixed topic (mixed mode)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 5: Bulk Subscription Example

        Demonstrate subscribing to multiple topics at once using bulk subscription.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Bulk subscription for factory monitoring
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
    logger.info(f"Bulk subscribed to {len(bulk_subscriptions)} factory topics")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 6: Start Background Listener

        Start the MQTT listener in background mode to continuously process messages.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Start listener in background
    logger.info("Starting MQTT listener in background...")
    await mqtt.start_listener(background=True)
    logger.info("Background listener started!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 7: Monitor Processing Statistics

        Monitor the processing statistics to see how messages are being handled.
        """
    )
    return


@app.cell
async def _(asyncio, logger, mqtt):
    # Monitor statistics for 60 seconds
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
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 8: Clean Shutdown

        Properly stop the listener and disconnect from the broker.
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

        Here's the complete example in a single executable cell:
        """
    )
    return


@app.cell
def _(MQTTPlugin, asyncio, logging):
    logging.basicConfig(level=logging.INFO)
    logger_1 = logging.getLogger(__name__)

    async def main():
        """Asynchronous MQTT plugin usage with RQ job queue."""
        mqtt = MQTTPlugin(broker='localhost', port=1883, base_dir='.', use_job_queue=True, redis_url='redis://localhost:6379', client_id='flowerpower_async_example')
        try:
            logger_1.info('Connecting to MQTT broker with job queue enabled...')
            await mqtt.connect()
            await mqtt.subscribe(topic='sensors/+/data', pipeline_name='sensor_data_processor', qos=1, execution_mode='async')
            await mqtt.subscribe(topic='alerts/critical', pipeline_name='critical_alert_handler', qos=2, execution_mode='sync')
            await mqtt.subscribe(topic='mixed/topic', pipeline_name='mixed_processor', qos=1, execution_mode='mixed')
            bulk_subscriptions = [{'topic': 'factory/+/temperature', 'pipeline': 'factory_temp_monitor', 'qos': 1, 'execution_mode': 'async'}, {'topic': 'factory/+/pressure', 'pipeline': 'factory_pressure_monitor', 'qos': 1, 'execution_mode': 'async'}]
            await mqtt.subscribe_bulk(bulk_subscriptions)
            logger_1.info('Starting MQTT listener in background...')
            await mqtt.start_listener(background=True)
            logger_1.info('Monitoring for 60 seconds. Press Ctrl+C to stop early...')
            for i in range(60):
                await asyncio.sleep(1)
                if i % 10 == 0:
                    stats = mqtt.get_statistics()
                    logger_1.info(f"Stats - Messages: {stats.get('message_count', 0)}, Pipelines: {stats.get('pipeline_count', 0)}, Errors: {stats.get('error_count', 0)}")
        except KeyboardInterrupt:
            logger_1.info('Received keyboard interrupt')
        except Exception as e:
            logger_1.error(f'Error: {e}')
        finally:
            logger_1.info('Stopping MQTT plugin...')
            await mqtt.stop_listener(timeout=5.0)
            await mqtt.disconnect()
            logger_1.info('MQTT plugin stopped')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Important Notes

        - Make sure Redis is running and an RQ worker is started: `rq worker mqtt_pipelines --url redis://localhost:6379`
        - The job queue allows for scalable background processing of MQTT messages
        - Different execution modes provide flexibility for various use cases
        - Bulk subscriptions are efficient for setting up multiple related topics
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
