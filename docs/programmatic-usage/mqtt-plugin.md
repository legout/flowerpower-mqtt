# MQTT Plugin

The `MQTTPlugin` class is the core of the `flowerpower-mqtt` programmatic API. It provides all the necessary methods to interact with an MQTT broker, manage subscriptions, and integrate with FlowerPower pipelines.

## Initialization

You can initialize the `MQTTPlugin` in two primary ways:

### 1. Direct Initialization

Initialize the plugin by passing connection parameters directly. This is useful for simple setups or when your configuration is dynamic.

```python
from flowerpower_mqtt import MQTTPlugin

# Basic initialization
mqtt = MQTTPlugin(
    broker="localhost",
    port=1883,
    base_dir="/path/to/your/flowerpower/project"
)

# With job queue enabled
mqtt_with_rq = MQTTPlugin(
    broker="mqtt.example.com",
    base_dir="/path/to/your/flowerpower/project",
    use_job_queue=True,
    redis_url="redis://localhost:6379"
)

# With additional MQTT client options
mqtt_custom = MQTTPlugin(
    broker="broker.hivemq.com",
    client_id="my_custom_client",
    username="myuser",
    password="mypassword",
    reconnect_retries=10,
    base_dir="/path/to/your/flowerpower/project"
)
```

**Parameters:**

*   `broker` (`str`, optional): The hostname or IP address of the MQTT broker. Defaults to `"localhost"`.
*   `port` (`int`, optional): The port of the MQTT broker. Defaults to `1883`.
*   `base_dir` (`str`): The base directory of your FlowerPower project. This is crucial for `flowerpower-mqtt` to locate and execute your pipelines.
*   `use_job_queue` (`bool`, optional): Set to `True` to enable asynchronous pipeline execution via RQ job queue. Defaults to `False`.
*   `redis_url` (`str`, optional): The Redis connection URL if `use_job_queue` is `True`. Defaults to `"redis://localhost:6379"`.
*   `config` ([`FlowerPowerMQTTConfig`](../core-concepts.md#configuration), optional): A complete configuration object. If provided, it overrides all other direct parameters.
*   `**mqtt_kwargs`: Additional keyword arguments are passed directly to the underlying `aiomqtt.Client` for advanced MQTT client configuration (e.g., `client_id`, `username`, `password`, `keepalive`, `clean_session`, `reconnect_retries`, `reconnect_delay`).

### 2. Initialization from Configuration File

Load the plugin's configuration from a YAML file. This is the recommended approach for production deployments and complex setups, as it allows for easy version control and management of your settings.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    # Load from a YAML configuration file
    mqtt = MQTTPlugin.from_config("mqtt_config.yml")
    
    await mqtt.connect()
    # ...
    await mqtt.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

**Parameters:**

*   `config_path` (`Union[str, Path]`): The path to your YAML configuration file.

## Connection Management

### `connect()`

Asynchronously connects the plugin to the configured MQTT broker. This method must be called before subscribing to topics or starting the listener.

```python
await mqtt.connect()
```

### `disconnect()`

Asynchronously disconnects the plugin from the MQTT broker. It also stops the listener if it's running.

```python
await mqtt.disconnect()
```

### Context Manager Usage

The `MQTTPlugin` can be used as an asynchronous context manager, ensuring that the connection is properly established and closed, even if errors occur. This is the recommended way to manage the plugin's lifecycle in `asyncio` applications.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def run_mqtt_application():
    async with MQTTPlugin(broker="localhost", base_dir=".") as mqtt:
        # Connection is established here
        await mqtt.subscribe("sensor/data", "process_sensor_data")
        await mqtt.start_listener()
    # Connection is automatically disconnected when exiting the 'async with' block
```

## Properties

*   `is_connected` (`bool`): Returns `True` if the plugin is currently connected to the MQTT broker, `False` otherwise.
*   `is_listening` (`bool`): Returns `True` if the MQTT message listener is currently running, `False` otherwise.