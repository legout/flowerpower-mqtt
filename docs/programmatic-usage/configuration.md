# Configuration

`flowerpower-mqtt` offers robust configuration management, allowing you to define MQTT connection parameters, job queue settings, and topic subscriptions using YAML files. This promotes consistency, reusability, and version control of your application settings.

## Loading Configuration from a File

The recommended way to load configuration is from a YAML file using the `MQTTPlugin.from_config()` class method.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    # Load configuration from a YAML file
    mqtt = MQTTPlugin.from_config("my_mqtt_config.yml")
    
    await mqtt.connect()
    await mqtt.start_listener()
    # ...
    await mqtt.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

**Parameters:**

*   `config_path` (`Union[str, Path]`): The path to your YAML configuration file.

## Configuration Structure

The configuration is structured hierarchically, with top-level keys for `mqtt`, `job_queue`, `subscriptions`, `base_dir`, and `log_level`.

```yaml
# my_mqtt_config.yml
mqtt:
  broker: "mqtt.example.com"
  port: 1883
  keepalive: 60
  client_id: "flowerpower_mqtt_client"
  reconnect_retries: 5
  reconnect_delay: 5
  username: "optional_username"
  password: "optional_password"

subscriptions:
  - topic: "sensors/+/temperature"
    pipeline: "temperature_processor"
    qos: 1
    execution_mode: "async"
  - topic: "alerts/critical"
    pipeline: "alert_handler"
    qos: 2
    execution_mode: "sync"

job_queue:
  enabled: true
  type: "rq" # Currently only "rq" is supported
  redis_url: "redis://localhost:6379/0"
  queue_name: "mqtt_pipelines"
  worker_count: 4
  max_retries: 3 # Max retries for failed jobs

base_dir: "/path/to/your/flowerpower/project" # Absolute or relative path
log_level: "INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Configuration Sections:

*   **`mqtt`**: Defines parameters for the MQTT broker connection.
    *   `broker` (`str`): MQTT broker hostname or IP.
    *   `port` (`int`): Broker port.
    *   `keepalive` (`int`): Maximum period in seconds between messages sent or received.
    *   `client_id` (`str`, optional): MQTT client ID. If not provided, a random one is generated.
    *   `clean_session` (`bool`): Set to `True` for a clean session (no persistent session state).
    *   `username` (`str`, optional): Username for authentication.
    *   `password` (`str`, optional): Password for authentication.
    *   `reconnect_retries` (`int`): Number of times to attempt reconnection.
    *   `reconnect_delay` (`int`): Base delay in seconds for exponential backoff during reconnection.
*   **`subscriptions`**: A list of individual subscription configurations. Each item in the list is a dictionary with:
    *   `topic` (`str`): MQTT topic pattern.
    *   `pipeline` (`str`): Name of the FlowerPower pipeline.
    *   `qos` (`int`, optional): QoS level (0, 1, or 2).
    *   `execution_mode` (`str`, optional): Pipeline execution mode (`sync`, `async`, `mixed`).
*   **`job_queue`**: Configures the optional job queue for asynchronous processing.
    *   `enabled` (`bool`): Set to `true` to enable job queue.
    *   `type` (`str`): Type of job queue (currently only `"rq"` is supported).
    *   `redis_url` (`str`): Redis connection URL (e.g., `redis://localhost:6379/0`).
    *   `queue_name` (`str`): Name of the Redis queue.
    *   `worker_count` (`int`): Recommended number of RQ workers.
    *   `max_retries` (`int`): Maximum number of times a failed job will be retried.
*   **`base_dir` (`str`)**: The base directory of your FlowerPower project. This is essential for `flowerpower-mqtt` to find and execute your pipelines.
*   **`log_level` (`str`)**: The logging level for the plugin (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

## Saving Current Configuration

You can save the plugin's current configuration (including any subscriptions added programmatically) to a YAML file using the `save_config()` method.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    mqtt = MQTTPlugin(broker="localhost", base_dir=".")
    await mqtt.connect()
    await mqtt.subscribe("new/data", "new_pipeline")
    
    # Save the current configuration to a file
    mqtt.save_config("updated_mqtt_config.yml")
    
    await mqtt.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

**Parameters:**

*   `file_path` (`Union[str, Path]`): The path where the configuration will be saved.

## `FlowerPowerMQTTConfig` Class

For advanced use cases, you can directly interact with the `FlowerPowerMQTTConfig` class, which is a `msgspec.Struct`. This allows for programmatic construction and manipulation of the configuration object.

```python
from flowerpower_mqtt.config import FlowerPowerMQTTConfig, MQTTConfig, SubscriptionConfig, JobQueueConfig

# Create configuration objects programmatically
mqtt_conf = MQTTConfig(broker="test.mosquitto.org", port=1883)
job_queue_conf = JobQueueConfig(enabled=True, redis_url="redis://my_redis:6379")
sub_conf = SubscriptionConfig(topic="my/topic", pipeline="my_pipeline", qos=1)

full_config = FlowerPowerMQTTConfig(
    mqtt=mqtt_conf,
    job_queue=job_queue_conf,
    subscriptions=[sub_conf],
    base_dir="/app/pipelines",
    log_level="DEBUG"
)

# You can then pass this object to the MQTTPlugin constructor
plugin = MQTTPlugin(config=full_config)

# Or convert it to a dictionary or YAML
config_dict = full_config.to_dict()
# full_config.to_yaml("programmatic_config.yml")
```