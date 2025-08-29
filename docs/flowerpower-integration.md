# FlowerPower Integration

`flowerpower-mqtt` is designed to seamlessly integrate with the `flowerpower` library, enabling you to trigger and execute your data pipelines based on incoming MQTT messages. This section explains how `flowerpower-mqtt` interacts with your FlowerPower projects and provides guidance on designing pipelines for MQTT data.

## Pipeline Input

When an MQTT message is received and processed by `flowerpower-mqtt`, the data from that message is passed as input to your designated FlowerPower pipeline. `flowerpower-mqtt` enriches this input with additional metadata, making it easy for your pipelines to access relevant information about the MQTT message.

The inputs provided to your FlowerPower pipeline will include:

*   `mqtt_message` (`Any`): The deserialized payload of the MQTT message. The type of this object depends on the `deserialization_format` specified for the subscription. For example, it could be a Python `dict` (for JSON or YAML), a `bytes` object (for raw binary data), or a `pyarrow.Table` (for PyArrow IPC). If deserialization fails or the `deserialization_format` is "auto" and no format is successfully detected, the `mqtt_message` will contain `raw_payload` (bytes) and `payload_str` (string representation) as attributes, allowing your pipeline to handle the raw data.
*   `mqtt_topic` (`str`): The full MQTT topic on which the message was received.
*   `mqtt_qos` (`int`): The Quality of Service (QoS) level of the received MQTT message (0, 1, or 2).
*   `execution_timestamp` (`str`): An ISO-formatted timestamp indicating when the message was processed by `flowerpower-mqtt`.
*   `execution_mode` (`str`): The execution mode (`sync`, `async`, or `mixed`) that triggered the pipeline.

## Example Pipeline

Here's an example of a FlowerPower pipeline that demonstrates how to access and process the MQTT message data provided by `flowerpower-mqtt`.

Assume you have a pipeline defined in your `pipelines/` directory (e.g., `pipelines/sensor_processor.py`):

```python
# pipelines/sensor_processor.py
import pandas as pd
from hamilton.function_modifiers import parameterize
from typing import Dict, Any

def process_mqtt_message(
    mqtt_message: Dict[str, Any], 
    mqtt_topic: str, 
    mqtt_qos: int,
    execution_timestamp: str
) -> Dict[str, Any]:
    """
    Process incoming MQTT message data.
    
    This function receives the parsed MQTT message payload and metadata.
    """
    print(f"Received message from {mqtt_topic} (QoS {mqtt_qos}) at {execution_timestamp}")

    # The type of mqtt_message depends on the deserialization_format.
    # For JSON/YAML, it's a dict. For PyArrow, it's a pyarrow.Table, etc.
    # If deserialization fails or format is 'auto' and no format detected,
    # mqtt_message will have 'raw_payload' and 'payload_str' attributes.
    if isinstance(mqtt_message, dict):
        # Handle JSON or YAML payloads
        sensor_data = mqtt_message.get("sensor_data", {})
        temperature = sensor_data.get("temperature")
        humidity = sensor_data.get("humidity")
    elif hasattr(mqtt_message, 'to_pandas') and callable(mqtt_message.to_pandas):
        # Handle PyArrow Table (or other Arrow-compatible objects)
        df = mqtt_message.to_pandas()
        if not df.empty:
            temperature = df['temperature'].iloc[0] if 'temperature' in df.columns else None
            humidity = df['humidity'].iloc[0] if 'humidity' in df.columns else None
        else:
            temperature, humidity = None, None
    elif hasattr(mqtt_message, 'raw_payload'):
        # Fallback for raw or undecipherable payloads
        print(f"Received raw payload (bytes): {mqtt_message.raw_payload}")
        print(f"Received payload (string): {mqtt_message.payload_str}")
        temperature, humidity = None, None # Or attempt custom parsing here
    else:
        # Generic handling for other deserialized types
        print(f"Received message of type {type(mqtt_message)}: {mqtt_message}")
        temperature, humidity = None, None # Adjust based on expected types

    # Perform some processing
    processed_data = {
        "processed_at": execution_timestamp,
        "source_topic": mqtt_topic,
        "temperature_celsius": temperature,
        "humidity_percent": humidity,
        "status": "processed" if temperature is not None else "failed_deserialization"
    }
    
    return processed_data

def save_results(process_mqtt_message: Dict[str, Any]) -> str:
    """
    Save the processed results.
    
    This function could save data to a database, file, or send it to another service.
    """
    # Example: Print to console
    print(f"Saving results for topic {process_mqtt_message['source_topic']}:")
    print(f"  Temperature: {process_mqtt_message.get('temperature_celsius')}°C")
    print(f"  Humidity: {process_mqtt_message.get('humidity_percent')}%")
    
    # In a real application, you would save this data persistently
    # e.g., to a database:
    # db.insert_sensor_reading(process_mqtt_message)
    
    return f"Results saved for {process_mqtt_message['source_topic']}"

# You can also define a full pipeline using Hamilton's @parameterize
# For more complex pipelines, refer to the FlowerPower documentation.
```

To link this pipeline, you would configure your `flowerpower-mqtt` subscription like this:

```yaml
# mqtt_config.yml
subscriptions:
  - topic: "sensors/+/data"
    pipeline: "sensor_processor" # Matches the name of your pipeline module
    qos: 1
    execution_mode: "async" # Or "sync", "mixed"
```

## Best Practices for Pipelines

*   **Idempotency**: Design your pipelines to be idempotent, especially if using QoS 1 (at least once delivery) or asynchronous processing, where messages might be processed multiple times due to retries.
*   **Error Handling**: Implement robust error handling within your pipelines. If a pipeline fails, `flowerpower-mqtt` will log the error, and if using an asynchronous job queue, the job might be retried based on your RQ configuration.
*   **Modularity**: Break down complex processing into smaller, reusable FlowerPower functions.
*   **Input Validation**: Validate the `mqtt_message` payload within your pipeline functions to ensure it conforms to your expected schema.
*   **Logging**: Use standard Python logging within your pipelines to provide visibility into their execution.
*   **Performance**: For high-throughput scenarios, optimize your pipelines for performance and consider using asynchronous execution with a job queue.