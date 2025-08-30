# Examples

This section provides an overview of the comprehensive examples available in the `examples/` directory. Each example is now organized as a self-contained project with detailed documentation, dependencies, and multiple runnable formats.

## Example Organization

The examples are now organized as self-contained projects in the `examples/` directory:

### Core Examples

1. **`examples/basic_usage/`** - Simple synchronous MQTT message processing
   - Demonstrates basic connection and subscription
   - Shows synchronous message processing
   - Includes Jupyter and Marimo notebooks

2. **`examples/async_with_rq/`** - Asynchronous processing with RQ job queue
   - Shows background pipeline execution
   - Demonstrates RQ integration
   - Includes monitoring and statistics

3. **`examples/config_based/`** - Configuration file management
   - YAML-based configuration setup
   - Multiple subscription management
   - Runtime configuration updates

4. **`examples/monitoring/`** - Real-time statistics and monitoring
   - Custom monitoring classes
   - Performance metrics tracking
   - Interactive monitoring dashboard

5. **`examples/multiple_qos/`** - Different QoS levels and execution modes
   - QoS 0, 1, 2 demonstrations
   - Execution mode comparisons
   - Performance implications

6. **`examples/cli_vs_programmatic/`** - CLI vs programmatic API comparison
   - When to use each approach
   - Hybrid workflow examples
   - Decision matrix for choosing approaches

### Common Resources

- **`examples/_common/pipelines/example_pipeline.py`** - Sample FlowerPower pipeline
- Shared utilities and common code patterns

## Running Examples

Each example is self-contained with its own README.md:

```bash
# Navigate to any example
cd examples/basic_usage

# Install dependencies
uv pip install -e ../..
uv pip install .

# Run the example
uv run python basic_usage.py

# Or explore interactively
uv run jupyter lab basic_usage.ipynb
uv run marimo run basic_usage_marimo.py
```

## 2. Asynchronous Processing with RQ (Programmatic)

This example demonstrates how to enable the RQ job queue for asynchronous pipeline execution, suitable for long-running tasks.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    # Create plugin with RQ job queue enabled
    mqtt = MQTTPlugin(
        broker="mqtt.example.com", # Replace with your MQTT broker
        base_dir="/path/to/your/flowerpower/project", # IMPORTANT: Replace with your FlowerPower project path
        use_job_queue=True,
        redis_url="redis://localhost:6379" # Replace if your Redis is elsewhere
    )
    
    await mqtt.connect()
    
    # Subscribe with async execution mode
    await mqtt.subscribe("data/sensor", "process_sensor_data", qos=1, execution_mode="async", deserialization_format="msgpack")
    
    print("Listening for MQTT messages on 'data/sensor' (asynchronous execution via RQ)...")
    print("Ensure an RQ worker is running: `rq worker mqtt_pipelines --url redis://localhost:6379`")
    
    # Start listener in background
    await mqtt.start_listener(background=True)
    
    # Keep the main loop running to allow background listener to operate
    print("Listener running in background. Doing other work for 60 seconds...")
    await asyncio.sleep(60) # Simulate other application work
    
    print("Stopping listener...")
    await mqtt.stop_listener()

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Using a Configuration File (Programmatic)

This example shows how to load `flowerpower-mqtt` configuration from a YAML file, promoting easier management and deployment.

First, create a `config.yml` file:

```yaml
# config.yml
mqtt:
  broker: "localhost"
  port: 1883

subscriptions:
  - topic: "device/+/status"
    pipeline: "update_device_status"
    qos: 0
    execution_mode: "sync"
    deserialization_format: "json"
  - topic: "alerts/high"
    pipeline: "send_alert_notification"
    qos: 1
    execution_mode: "async"
    deserialization_format: "yaml"
  - topic: "data/raw"
    pipeline: "process_raw_data"
    qos: 0
    execution_mode: "sync"
    deserialization_format: "auto"

job_queue:
  enabled: true
  redis_url: "redis://localhost:6379"
  queue_name: "mqtt_jobs"

base_dir: "/path/to/your/flowerpower/project" # IMPORTANT: Replace with your FlowerPower project path
log_level: "INFO"
```

Then, use it in your Python script:

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    # Load from configuration file
    mqtt = MQTTPlugin.from_config("config.yml")
    
    await mqtt.connect()
    print("Connected and configured from config.yml. Starting listener...")
    await mqtt.start_listener()

if __name__ == "__main__":
    asyncio.run(main())
```

## 4. Mixed-Mode Processing Based on QoS (Programmatic)

This example demonstrates how to use the `mixed` execution mode, where QoS 2 messages are processed synchronously, and QoS 0/1 messages are processed asynchronously.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    mqtt = MQTTPlugin(
        broker="localhost",
        base_dir="/path/to/your/flowerpower/project", # IMPORTANT: Replace with your FlowerPower project path
        use_job_queue=True, # Job queue must be enabled for mixed mode
        redis_url="redis://localhost:6379"
    )
    
    await mqtt.connect()
    
    # Subscribe with mixed execution mode
    # QoS 2 messages will be sync, QoS 0/1 will be async
    await mqtt.subscribe("critical/q2_data", "process_critical_data", qos=2, execution_mode="mixed", deserialization_format="json")
    await mqtt.subscribe("non_critical/q1_data", "process_non_critical_data", qos=1, execution_mode="mixed", deserialization_format="msgpack")
    
    print("Listening with mixed execution mode...")
    print("QoS 2 messages -> synchronous pipeline execution.")
    print("QoS 0/1 messages -> asynchronous pipeline execution via RQ.")
    
    await mqtt.start_listener()

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. CLI-Only Workflow

This workflow demonstrates how to manage `flowerpower-mqtt` entirely from the command line.

1.  **Create Configuration (Interactive)**

    ```bash
    flowerpower-mqtt config create --interactive --output my_cli_config.yml
    ```
    Follow the prompts to set up your broker, base directory, and optionally enable the job queue.

2.  **Connect to Broker**

    ```bash
    flowerpower-mqtt connect --config my_cli_config.yml
    ```

3.  **Add Subscriptions**

    ```bash
    flowerpower-mqtt subscribe "sensors/light" process_light_data --qos 0 --mode sync --deserialization-format json --config my_cli_config.yml --save-config
    flowerpower-mqtt subscribe "sensors/humidity" process_humidity_data --qos 1 --mode async --deserialization-format auto --config my_cli_config.yml --save-config
    ```
    The `--save-config` flag updates `my_cli_config.yml` with the new subscriptions.

4.  **Start Listener in Background**

    ```bash
    flowerpower-mqtt listen --background --config my_cli_config.yml &
    ```

5.  **Monitor Status**

    ```bash
    flowerpower-mqtt monitor --config my_cli_config.yml
    ```
    Press `Ctrl+C` to stop monitoring.

6.  **Check Job Queue Status (if enabled)**

    ```bash
    flowerpower-mqtt jobs status --config my_cli_config.yml
    ```

7.  **Disconnect**

    ```bash
    flowerpower-mqtt disconnect --config my_cli_config.yml
    ```

## 6. Hybrid Workflow (CLI for Setup, Python for Logic)

This approach combines the ease of CLI configuration with the flexibility of programmatic control.

1.  **Generate Configuration via CLI**

    Use the CLI to create and validate your `flowerpower-mqtt` configuration. This is especially useful for setting up complex MQTT and job queue parameters.

    ```bash
    flowerpower-mqtt config create --interactive --output hybrid_config.yml
    flowerpower-mqtt config validate hybrid_config.yml
    ```

## 7. Payload Deserialization Examples

This section demonstrates how to use different `deserialization_format` options for your MQTT subscriptions, including the "auto" detection feature.

### Scenario 1: JSON Payload

Assume an MQTT message on `data/sensor/json` with payload: `{"temperature": 25.5, "humidity": 60}`

**Subscription:**

```python
await mqtt.subscribe("data/sensor/json", "process_sensor_data", deserialization_format="json")
```

**Expected `mqtt_message` in pipeline:**

```python
# mqtt_message will be a Python dictionary
{
    "temperature": 25.5,
    "humidity": 60
}
```

### Scenario 2: MessagePack Payload

Assume an MQTT message on `data/sensor/msgpack` with payload (binary MessagePack encoding of `{"pressure": 1012, "altitude": 150}`):

**Subscription:**

```python
await mqtt.subscribe("data/sensor/msgpack", "process_sensor_data", deserialization_format="msgpack")
```

**Expected `mqtt_message` in pipeline:**

```python
# mqtt_message will be a Python dictionary
{
    "pressure": 1012,
    "altitude": 150
}
```

### Scenario 3: PyArrow IPC Payload (e.g., Arrow Table)

Assume an MQTT message on `data/sensor/arrow` with a PyArrow IPC-encoded Arrow Table payload:

**Subscription:**

```python
await mqtt.subscribe("data/sensor/arrow", "process_sensor_data", deserialization_format="pyarrow")
```

**Expected `mqtt_message` in pipeline:**

```python
# mqtt_message will be a pyarrow.Table object
# You can convert it to a Pandas DataFrame for easier processing:
# df = mqtt_message.to_pandas()
```

### Scenario 4: "Auto" Detection

Assume an MQTT message on `data/sensor/auto` where the payload could be JSON, MessagePack, or YAML.

**Subscription:**

```python
await mqtt.subscribe("data/sensor/auto", "process_sensor_data", deserialization_format="auto")
```

**Expected `mqtt_message` in pipeline (depending on actual payload):**

*   If payload is `{"status": "ok"}` (JSON): `mqtt_message` will be `{"status": "ok"}` (dict).
*   If payload is MessagePack-encoded `{"value": 123}`: `mqtt_message` will be `{"value": 123}` (dict).
*   If payload is YAML-encoded `key: value`: `mqtt_message` will be `{'key': 'value'}` (dict).
*   If payload is `b'raw_bytes'` (and no auto-detection succeeds): `mqtt_message` will contain `raw_payload=b'raw_bytes'` and `payload_str='raw_bytes'`. Your pipeline should handle this fallback.

**Example Python code for a pipeline demonstrating deserialized input:**

```python
# pipelines/process_sensor_data.py
from typing import Any, Dict
import pyarrow as pa
import pandas as pd

def process_sensor_data(mqtt_message: Any, mqtt_topic: str) -> Dict[str, Any]:
    """
    Processes incoming sensor data, handling different deserialized formats.
    """
    processed_data = {
        "source_topic": mqtt_topic,
        "processed_payload": None,
        "payload_type": str(type(mqtt_message))
    }

    if isinstance(mqtt_message, dict):
        # Handles JSON, YAML, MessagePack, Pickle (if dict)
        processed_data["processed_payload"] = mqtt_message
        print(f"Processed dictionary payload from {mqtt_topic}: {mqtt_message}")
    elif isinstance(mqtt_message, pa.Table):
        # Handles PyArrow Tables
        df = mqtt_message.to_pandas()
        processed_data["processed_payload"] = df.to_dict(orient="records")
        print(f"Processed PyArrow Table payload from {mqtt_topic}:\n{df}")
    elif hasattr(mqtt_message, 'raw_payload'):
        # Fallback for raw bytes or failed auto-detection
        processed_data["processed_payload"] = {
            "raw_payload_bytes": mqtt_message.raw_payload.hex(),
            "raw_payload_str": mqtt_message.payload_str
        }
        print(f"Processed raw payload from {mqtt_topic}: {mqtt_message.payload_str}")
    else:
        # Handle other potential types or log an error
        print(f"Unsupported payload type for {mqtt_topic}: {type(mqtt_message)}")
        processed_data["processed_payload"] = "Unsupported format"

    return processed_data
```

2.  **Load and Extend in Python**

    Load the CLI-generated configuration in your Python application and add custom business logic or dynamic subscriptions.

    ```python
    import asyncio
    from flowerpower_mqtt import MQTTPlugin

    async def main():
        # Load the configuration generated by the CLI
        mqtt = MQTTPlugin.from_config("hybrid_config.yml")
        
        await mqtt.connect()
        
        # Add dynamic subscriptions or override existing ones
        await mqtt.subscribe("custom/topic", "custom_pipeline", qos=1, deserialization_format="json")
        
        # Implement custom application logic here
        print("Hybrid application running. Listening for messages...")
        
        # Start the listener (can be background or foreground)
        await mqtt.start_listener()

    if __name__ == "__main__":
        asyncio.run(main())

    ```