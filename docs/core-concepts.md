# Core Concepts

Understanding the core concepts of `flowerpower-mqtt` is essential for effectively using and integrating the library into your projects.

## The `MQTTPlugin`

The `MQTTPlugin` class is the central interface for programmatic interaction with `flowerpower-mqtt`. It encapsulates the MQTT client, listener, and configuration management, providing a high-level API for connecting to brokers, managing subscriptions, and controlling message processing.

You'll typically instantiate `MQTTPlugin` either directly with connection parameters or by loading a configuration from a YAML file.

```python
from flowerpower_mqtt import MQTTPlugin

# Instantiate directly
mqtt_direct = MQTTPlugin(broker="localhost", base_dir="./my_flowerpower_project")

# Instantiate from a configuration file
mqtt_from_config = MQTTPlugin.from_config("mqtt_config.yml")
```

## Execution Modes

`flowerpower-mqtt` offers flexible execution modes to handle incoming MQTT messages and trigger FlowerPower pipelines. These modes determine how the pipeline execution is managed, especially concerning synchronous vs. asynchronous processing.

### `sync` (Synchronous)

*   **Description**: In `sync` mode, when an MQTT message is received, the associated FlowerPower pipeline is executed directly within the main event loop. This means the message processing is blocking; the listener will wait for the pipeline to complete before processing the next message.
*   **Use Cases**:
    *   Pipelines that are very fast and do not require significant computation time.
    *   Scenarios where immediate feedback or sequential processing is critical.
    *   Simple setups where an external job queue is not desired or available.
*   **Considerations**: Can lead to message backlog if pipelines take too long to execute, potentially impacting MQTT message processing latency.

### `async` (Asynchronous)

*   **Description**: In `async` mode, when an MQTT message is received, the associated FlowerPower pipeline is enqueued as a job into an external job queue (currently [RQ](https://python-rq.org/)). The main event loop continues to process incoming messages without waiting for the pipeline to complete. A separate worker process (or processes) then picks up and executes these jobs in the background.
*   **Use Cases**:
    *   Long-running or computationally intensive pipelines.
    *   Scenarios requiring high message throughput without blocking the MQTT listener.
    *   Distributed processing where multiple workers can handle jobs concurrently.
    *   When you need robust retry mechanisms and persistent job queues.
*   **Considerations**: Requires a running Redis instance and RQ workers. Adds complexity due to distributed processing.

### `mixed` (QoS-based Routing)

*   **Description**: `mixed` mode provides a dynamic approach to execution by routing messages based on their MQTT Quality of Service (QoS) level.
    *   Messages with **QoS 2** (Exactly-once delivery) are executed **synchronously**. This is because QoS 2 messages require a more robust acknowledgment handshake, and synchronous processing ensures the pipeline completes before the MQTT broker is fully acknowledged.
    *   Messages with **QoS 0** (At most once) or **QoS 1** (At least once) are executed **asynchronously** via the job queue.
*   **Use Cases**:
    *   Environments with a mix of critical and non-critical data streams.
    *   When you want to prioritize the reliability of certain messages while maintaining high throughput for others.
*   **Considerations**: Requires careful consideration of your MQTT QoS strategy and a properly configured job queue.

## Configuration

`flowerpower-mqtt` uses a flexible YAML-based configuration system. This allows you to define MQTT connection parameters, job queue settings, and all your topic subscriptions in a human-readable file.

A typical configuration file (`mqtt_config.yml`) looks like this:

```yaml
mqtt:
  broker: "mqtt.example.com"
  port: 1883
  keepalive: 60
  client_id: "flowerpower_mqtt_client"
  reconnect_retries: 5
  reconnect_delay: 5

subscriptions:
  - topic: "sensors/+/temperature"
    pipeline: "temperature_processor"
    qos: 1
    execution_mode: "async"
  - topic: "alerts/critical"
    pipeline: "alert_handler"
    qos: 2
    execution_mode: "sync"
    deserialization_format: "json" # Example: explicitly set deserialization format
  - topic: "sensors/binary_data"
    pipeline: "process_binary_sensor"
    qos: 0
    execution_mode: "async"
    deserialization_format: "msgpack" # Example: MessagePack payload
  - topic: "mixed/format_data"
    pipeline: "handle_mixed_format"
    qos: 1
    execution_mode: "async"
    deserialization_format: "auto" # Example: auto-detect payload format

job_queue:
  enabled: true
  type: "rq"
  redis_url: "redis://localhost:6379"
  queue_name: "mqtt_pipelines"
  worker_count: 4

base_dir: "/path/to/flowerpower/project"
log_level: "INFO"
```

This configuration can be loaded by both the CLI and the programmatic API, ensuring consistency across different usage patterns. The configuration is validated using `msgspec` for robust error checking.

## Statistics and Monitoring

`flowerpower-mqtt` provides built-in mechanisms for monitoring its operation and gathering statistics. This includes:

*   **Message Counts**: Tracks the total number of messages received and the count per subscription.
*   **Pipeline Execution Counts**: Records how many pipelines have been triggered.
*   **Error Counts**: Logs errors encountered during message processing or pipeline execution.
*   **Connection Status**: Indicates whether the plugin is currently connected to the MQTT broker.
*   **Job Queue Status**: Provides insights into the state of the job queue if enabled.

## Payload Deserialization

`flowerpower-mqtt` offers robust payload deserialization capabilities, allowing you to automatically convert incoming MQTT message payloads from various formats into Python objects. This is managed primarily through the `deserialization_format` field in your `SubscriptionConfig`.

### Supported Formats

The `MQTTMessage` class supports the following payload serialization/deserialization formats:

*   **`json`**: For payloads encoded as JSON strings. Deserialized into Python dictionaries or lists.
*   **`yaml`**: For payloads encoded as YAML strings. Deserialized into Python dictionaries or lists.
*   **`msgpack`**: For payloads encoded using MessagePack, a binary serialization format. Deserialized into standard Python types.
*   **`pickle`**: For payloads serialized using Python's `pickle` module. Deserialized into the original Python object. **Use with caution** as unpickling data from untrusted sources can be a security risk.
*   **`protobuf`**: For payloads serialized using Google's Protocol Buffers. Requires a compiled Protobuf schema and the corresponding Python classes to be available.
*   **`pyarrow`**: For payloads serialized using Apache Arrow IPC format (e.g., Arrow Tables, Arrays). Deserialized into PyArrow objects.

### The `deserialization_format` Field

When defining a subscription, you can specify the `deserialization_format` to instruct `flowerpower-mqtt` how to interpret the incoming payload:

```yaml
subscriptions:
  - topic: "sensors/json_data"
    pipeline: "process_json"
    deserialization_format: "json"
  - topic: "sensor/readings/msgpack"
    pipeline: "process_msgpack"
    deserialization_format: "msgpack"
```

If `deserialization_format` is not specified for a subscription, `flowerpower-mqtt` will attempt to deserialize text-based payloads as JSON by default.

### "Auto" Detection Mechanism

The `deserialize()` method within `MQTTMessage` includes an intelligent "auto" detection feature. When `deserialization_format` is set to `"auto"`, the system attempts to deserialize the payload in a specific, prioritized order until a successful parse is achieved. This provides flexibility when the payload format might vary or is not strictly known beforehand.

The order of attempts for "auto" detection is:

1.  **JSON**: Attempts to parse the payload as a JSON string. This is a common and often human-readable format.
2.  **MessagePack**: If JSON parsing fails, it attempts MessagePack deserialization. MessagePack is a compact binary format, making it efficient for many IoT and data streaming scenarios.
3.  **YAML**: If MessagePack fails, it tries YAML. YAML is human-friendly and often used for configuration, but can also be used for data serialization.
4.  **PyArrow**: Next, it attempts PyArrow IPC deserialization. This is particularly useful for structured tabular data.
5.  **Pickle**: Finally, it attempts Python's Pickle format. This is a Python-specific serialization and should be used with caution, especially with untrusted data, due to potential security vulnerabilities.

**Rationale for the Order:**
The order is chosen to prioritize commonly used, safer, and more efficient formats first (JSON, MessagePack, PyArrow) before falling back to less common or potentially less secure formats like Pickle. This ensures that the most likely successful and performant deserialization attempts are made early. If all attempts fail, the payload will be available as `raw_payload` (bytes) and `payload_str` (string) in the `MQTTMessage` object passed to your pipeline, allowing for manual handling.

These statistics are accessible via both the CLI (`flowerpower-mqtt status`, `flowerpower-mqtt monitor`) and the programmatic API (`MQTTPlugin.get_statistics()`, `MQTTPlugin.get_subscriptions()`), allowing you to integrate monitoring into your existing dashboards or scripts.