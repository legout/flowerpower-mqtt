import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Configuration-Based Example

        This notebook demonstrates how to use YAML configuration files for managing complex MQTT setups with the FlowerPower MQTT Plugin.

        ## Overview

        This example shows how to:
        - Create configuration files programmatically
        - Load plugins from configuration files
        - Manage complex subscription setups
        - Save runtime configuration changes

        ## Prerequisites

        Make sure you have:
        - MQTT broker running
        - Redis server running (for job queue)
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

        Import the necessary libraries for configuration-based MQTT setup.
        """
    )
    return


@app.cell
def _():
    import asyncio
    import logging
    from pathlib import Path
    from flowerpower_mqtt import MQTTPlugin, FlowerPowerMQTTConfig

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return FlowerPowerMQTTConfig, MQTTPlugin, Path, logger, logging


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 2: Create Configuration Programmatically

        Create a comprehensive configuration file with MQTT settings, job queue configuration, and predefined subscriptions.
        """
    )
    return


@app.cell
def _(FlowerPowerMQTTConfig, Path, logger):
    def _create_example_config():
        """Create an example configuration file."""
        config = FlowerPowerMQTTConfig()
        config.mqtt.broker = 'localhost'
        config.mqtt.port = 1883
        config.mqtt.keepalive = 60
        config.mqtt.client_id = 'flowerpower_config_example'
        config.job_queue.enabled = True
        config.job_queue.redis_url = 'redis://localhost:6379'
        config.job_queue.queue_name = 'mqtt_pipelines'
        config.job_queue.worker_count = 4
        config.base_dir = '.'
        config.log_level = 'INFO'
        from flowerpower_mqtt.config import SubscriptionConfig
        config.subscriptions = [SubscriptionConfig(topic='sensors/+/temperature', pipeline='temperature_processor', qos=1, execution_mode='async'), SubscriptionConfig(topic='sensors/+/humidity', pipeline='humidity_processor', qos=1, execution_mode='async'), SubscriptionConfig(topic='alerts/critical', pipeline='critical_alert_handler', qos=2, execution_mode='sync'), SubscriptionConfig(topic='logs/+/error', pipeline='error_log_processor', qos=0, execution_mode='async')]
        config_file = Path('example_mqtt_config.yml')
        config.to_yaml(config_file)
        logger.info(f'Created example configuration: {config_file}')
        return config_file
    config_file = _create_example_config()
    print(f'Configuration file created: {config_file}')
    return (config_file,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 3: Load Plugin from Configuration

        Load the MQTT plugin using the configuration file we just created.
        """
    )
    return


@app.cell
def _(MQTTPlugin, config_file, logger):
    # Load plugin from configuration
    logger.info(f"Loading plugin from configuration: {config_file}")
    mqtt = MQTTPlugin.from_config(config_file)
    logger.info("Plugin loaded successfully from configuration!")
    return (mqtt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 4: Connect to MQTT Broker

        Connect to the MQTT broker using the loaded configuration.
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
        ## Step 5: Display Loaded Subscriptions

        Show the subscriptions that were loaded from the configuration file.
        """
    )
    return


@app.cell
def _(logger, mqtt):
    # Display loaded subscriptions
    subscriptions = mqtt.get_subscriptions()
    logger.info(f"Loaded {len(subscriptions)} subscriptions from config:")
    for sub in subscriptions:
        logger.info(
            f"  - {sub['topic']} -> {sub['pipeline']} "
            f"(QoS {sub['qos']}, {sub['execution_mode']} mode)"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 6: Add Runtime Subscriptions

        Demonstrate adding additional subscriptions programmatically at runtime.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Add a runtime subscription
    await mqtt.subscribe(
        topic="runtime/+/data",
        pipeline_name="runtime_processor",
        qos=1,
        execution_mode="async"
    )
    logger.info("Added runtime subscription")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 7: Start MQTT Listener

        Start listening for MQTT messages using the configured subscriptions.
        """
    )
    return


@app.cell
async def _(logger, mqtt):
    # Start listener
    logger.info("Starting MQTT listener. Press Ctrl+C to stop...")
    await mqtt.start_listener(background=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 8: Save Final Configuration

        Save the final configuration including any runtime changes.
        """
    )
    return


@app.cell
def _(Path, logger, mqtt):
    # Save final configuration (including runtime additions)
    final_config_file = Path("final_mqtt_config.yml") 
    mqtt.save_config(final_config_file)
    logger.info(f"Saved final configuration: {final_config_file}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Step 9: Clean Shutdown

        Properly disconnect and clean up resources.
        """
    )
    return


@app.cell
async def _(config_file, logger, mqtt):
    # Clean shutdown
    logger.info("Stopping MQTT plugin...")
    await mqtt.disconnect()
    logger.info("MQTT plugin stopped")

    # Cleanup example config file
    if config_file.exists():
        config_file.unlink()
        logger.info(f"Cleaned up example config: {config_file}")
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
def _(FlowerPowerMQTTConfig, MQTTPlugin, Path, SubscriptionConfig, logging):
    logging.basicConfig(level=logging.INFO)
    logger_1 = logging.getLogger(__name__)

    def _create_example_config():
        """Create an example configuration file."""
        config = FlowerPowerMQTTConfig()
        config.mqtt.broker = 'localhost'
        config.mqtt.port = 1883
        config.mqtt.keepalive = 60
        config.mqtt.client_id = 'flowerpower_config_example'
        config.job_queue.enabled = True
        config.job_queue.redis_url = 'redis://localhost:6379'
        config.job_queue.queue_name = 'mqtt_pipelines'
        config.job_queue.worker_count = 4
        config.base_dir = '.'
        config.log_level = 'INFO'
        config.subscriptions = [SubscriptionConfig(topic='sensors/+/temperature', pipeline='temperature_processor', qos=1, execution_mode='async'), SubscriptionConfig(topic='sensors/+/humidity', pipeline='humidity_processor', qos=1, execution_mode='async'), SubscriptionConfig(topic='alerts/critical', pipeline='critical_alert_handler', qos=2, execution_mode='sync'), SubscriptionConfig(topic='logs/+/error', pipeline='error_log_processor', qos=0, execution_mode='async')]
        config_file = Path('example_mqtt_config.yml')
        config.to_yaml(config_file)
        logger_1.info(f'Created example configuration: {config_file}')
        return config_file

    async def main():
        """Configuration-based MQTT plugin usage."""
        config_file = _create_example_config()
        try:
            logger_1.info(f'Loading plugin from configuration: {config_file}')
            mqtt = MQTTPlugin.from_config(config_file)
            logger_1.info('Connecting to MQTT broker...')
            await mqtt.connect()
            subscriptions = mqtt.get_subscriptions()
            logger_1.info(f'Loaded {len(subscriptions)} subscriptions from config:')
            for sub in subscriptions:
                logger_1.info(f"  - {sub['topic']} -> {sub['pipeline']} (QoS {sub['qos']}, {sub['execution_mode']} mode)")
            await mqtt.subscribe(topic='runtime/+/data', pipeline_name='runtime_processor', qos=1, execution_mode='async')
            logger_1.info('Starting MQTT listener. Press Ctrl+C to stop...')
            await mqtt.start_listener(background=False)
        except KeyboardInterrupt:
            logger_1.info('Received keyboard interrupt')
        except Exception as e:
            logger_1.error(f'Error: {e}')
        finally:
            logger_1.info('Stopping MQTT plugin...')
            if 'mqtt' in locals():
                await mqtt.disconnect()
                final_config_file = Path('final_mqtt_config.yml')
                mqtt.save_config(final_config_file)
                logger_1.info(f'Saved final configuration: {final_config_file}')
            if config_file.exists():
                config_file.unlink()
                logger_1.info(f'Cleaned up example config: {config_file}')
            logger_1.info('MQTT plugin stopped')
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
