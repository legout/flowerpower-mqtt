import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Basic Usage Example for FlowerPower MQTT Plugin

        This notebook demonstrates simple synchronous usage where MQTT messages trigger immediate pipeline execution.

        ## Overview

        This example shows how to:
        - Connect to an MQTT broker
        - Subscribe to MQTT topics
        - Process messages synchronously
        - Handle clean shutdown

        ## Prerequisites

        Make sure you have:
        - MQTT broker running (we'll use Docker)
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

        First, let's import the necessary libraries for our MQTT plugin.
        """
    )
    return


@app.cell
def _():
    import asyncio
    import logging
    from flowerpower_mqtt import MQTTPlugin

    # Configure logging to see what's happening
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return MQTTPlugin, logger, logging


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 2: Create MQTT Plugin Instance

        Now we'll create an instance of the MQTTPlugin with basic configuration.
        """
    )
    return


@app.cell
def _(MQTTPlugin):
    # Create plugin instance
    mqtt = MQTTPlugin(
        broker="localhost",  # Change to your MQTT broker address
        port=1883,
        base_dir=".",  # FlowerPower project directory
        client_id="flowerpower_basic_example"
    )

    print("MQTT Plugin created successfully!")
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
        ## Step 4: Subscribe to Topics

        Subscribe to MQTT topics that will trigger pipeline execution.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Subscribe to temperature sensor topic
    await mqtt.subscribe(
        topic="sensors/temperature", 
        pipeline_name="temperature_processor",
        qos=1  # At least once delivery
    )
    logger.info("Subscribed to temperature sensor topic")

    # Subscribe to humidity sensor topic
    await mqtt.subscribe(
        topic="sensors/humidity",
        pipeline_name="humidity_processor", 
        qos=0  # Fire and forget
    )
    logger.info("Subscribed to humidity sensor topic")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 5: Start Listening for Messages

        Start the MQTT listener to begin processing messages. This will run until interrupted.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Start listening for messages
    logger.info("Starting MQTT listener. Press Ctrl+C to stop...")
    await mqtt.start_listener(background=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 6: Clean Shutdown

        When you're done, make sure to disconnect cleanly.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Clean shutdown
    logger.info("Stopping MQTT plugin...")
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
def _(MQTTPlugin, logging):
    logging.basicConfig(level=logging.INFO)
    logger_1 = logging.getLogger(__name__)

    async def main():
        """Basic synchronous MQTT plugin usage."""
        mqtt = MQTTPlugin(broker='localhost', port=1883, base_dir='.', client_id='flowerpower_basic_example')
        try:
            logger_1.info('Connecting to MQTT broker...')
            await mqtt.connect()
            await mqtt.subscribe(topic='sensors/temperature', pipeline_name='temperature_processor', qos=1)
            await mqtt.subscribe(topic='sensors/humidity', pipeline_name='humidity_processor', qos=0)
            logger_1.info('Starting MQTT listener. Press Ctrl+C to stop...')
            await mqtt.start_listener(background=False)
        except KeyboardInterrupt:
            logger_1.info('Received keyboard interrupt')
        except Exception as e:
            logger_1.error(f'Error: {e}')
        finally:
            logger_1.info('Stopping MQTT plugin...')
            await mqtt.disconnect()
            logger_1.info('MQTT plugin stopped')
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
