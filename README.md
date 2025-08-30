# FlowerPower MQTT Plugin

A simple yet powerful MQTT plugin for [FlowerPower](https://github.com/legout/flowerpower) that triggers pipeline execution when messages arrive on subscribed topics. Features configurable QoS levels, optional RQ job queue integration for asynchronous processing, and a beautiful CLI for easy management.

## Features

### Core Features
- **Simple API**: Easy-to-use interface for connecting, subscribing, and listening
- **QoS Support**: Full MQTT QoS support (0, 1, 2) for reliable message delivery
- **Async Processing**: Optional RQ job queue integration for background pipeline execution
- **High Performance**: Uses msgspec for fast serialization and deserialization
- **Flexible Payload Handling**: Supports JSON, YAML, MessagePack, Pickle, Protobuf, and PyArrow IPC payload serialization/deserialization with auto-detection.
- **Multiple Execution Modes**: 
  - `sync`: Direct pipeline execution (blocking)
  - `async`: Background execution via RQ
  - `mixed`: QoS-based routing (QoS 2 → sync, QoS 0/1 → async)
- **Topic Wildcards**: Support for MQTT topic patterns (`+`, `#`)
- **Graceful Shutdown**: Ctrl+C handling and proper cleanup
- **Statistics & Monitoring**: Built-in metrics and job tracking
- **Configuration Management**: YAML-based configuration support with msgspec validation
- **Automatic Reconnection**: Robust connection handling with configurable retry attempts and exponential backoff

### CLI Features
- **Beautiful Interface**: Rich, colorful CLI with tables and progress bars
- **Interactive Configuration**: Step-by-step configuration setup
- **Real-time Monitoring**: Live statistics and subscription monitoring
- **Configuration Management**: Create, validate, edit, and show configurations
- **Job Queue Management**: Monitor and manage RQ workers and jobs
- **Shell Completion**: Auto-completion support for commands and options
- **JSON Output**: Machine-readable output for scripting and automation

## Installation

`flowerpower-mqtt` is available on PyPI and can be installed using `uv pip` (recommended) or `pip`.

### Using `uv pip` (Recommended)

`uv` is a fast Python package installer and resolver. It's the recommended way to install `flowerpower-mqtt`.

```bash
uv pip install flowerpower-mqtt
```

### Using `pip`

If you prefer using `pip`, you can install `flowerpower-mqtt` directly:

```bash
pip install flowerpower-mqtt
```

After installation, the `flowerpower-mqtt` CLI command will be available.

## Quick Start

### CLI Quick Start

The fastest way to get started is using the CLI:

```bash
# 1. Create configuration interactively
flowerpower-mqtt config create --interactive

# 2. Connect to MQTT broker
flowerpower-mqtt connect --config mqtt_config.yml

# 3. Subscribe to topics
flowerpower-mqtt subscribe "sensors/+/temperature" temperature_processor --qos 1

# 4. Start listening (press Ctrl+C to stop)
flowerpower-mqtt listen
```

For async processing with job queue:

```bash
# 1. Create config with job queue enabled
flowerpower-mqtt config create --interactive --job-queue

# 2. Start RQ worker (in separate terminal)
rq worker mqtt_pipelines --url redis://localhost:6379

# 3. Connect and subscribe with async mode
flowerpower-mqtt connect --config mqtt_config.yml
flowerpower-mqtt subscribe "data/+" data_processor --qos 1 --mode async

# 4. Start listening and monitor
flowerpower-mqtt listen --background &
flowerpower-mqtt monitor --interval 5
```

### Programmatic Usage

### 1. Basic Synchronous Usage

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    # Create plugin instance
    mqtt = MQTTPlugin(
        broker="localhost",
        base_dir="/path/to/flowerpower/project"
    )
    
    # Connect to broker
    await mqtt.connect()
    
    # Subscribe to topic
    await mqtt.subscribe("sensors/temperature", "temperature_pipeline", qos=1)
    
    # Start listening (blocks until Ctrl+C)
    await mqtt.start_listener()

# Run the plugin
asyncio.run(main())
```

### 2. Asynchronous with Job Queue

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    # Create plugin with RQ job queue enabled
    mqtt = MQTTPlugin(
        broker="mqtt.example.com",
        base_dir="/path/to/flowerpower/project",
        use_job_queue=True,
        redis_url="redis://localhost:6379"
    )
    
    await mqtt.connect()
    
    # Subscribe with async execution
    await mqtt.subscribe("sensors/+/data", "sensor_processor", qos=1, execution_mode="async")
    await mqtt.subscribe("alerts/critical", "alert_handler", qos=2, execution_mode="sync")
    
    # Start listener in background
    await mqtt.start_listener(background=True)
    
    # Do other work...
    await asyncio.sleep(60)
    
    # Stop gracefully
    await mqtt.stop_listener()

asyncio.run(main())
```

### 3. Using Configuration File

Create `mqtt_config.yml`:

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

job_queue:
  enabled: true
  type: "rq"
  redis_url: "redis://localhost:6379"
  queue_name: "mqtt_pipelines"
  worker_count: 4

base_dir: "/path/to/flowerpower/project"
log_level: "INFO"
```

Then use it:

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    # Load from configuration
    mqtt = MQTTPlugin.from_config("mqtt_config.yml")
    
    await mqtt.connect()
    await mqtt.start_listener()

asyncio.run(main())
```

## CLI Reference

The FlowerPower MQTT CLI provides a comprehensive interface for managing MQTT connections, subscriptions, and monitoring.

### Configuration Management

```bash
# Create configuration interactively
flowerpower-mqtt config create --interactive

# Create configuration with job queue enabled
flowerpower-mqtt config create --job-queue --output my_config.yml

# Validate configuration file
flowerpower-mqtt config validate mqtt_config.yml

# Show current configuration
flowerpower-mqtt config show

# Edit configuration (opens in $EDITOR)
flowerpower-mqtt config edit
```

### Connection Management

```bash
# Connect to MQTT broker
flowerpower-mqtt connect --broker localhost --port 1883

# Connect with job queue enabled
flowerpower-mqtt connect --broker mqtt.example.com --job-queue --redis-url redis://localhost:6379

# Connect using configuration file
flowerpower-mqtt connect --config mqtt_config.yml

# Disconnect from broker
flowerpower-mqtt disconnect
```

### Subscription Management

```bash
# Subscribe to topic
flowerpower-mqtt subscribe "sensors/temperature" temp_processor --qos 1

# Subscribe with async execution
flowerpower-mqtt subscribe "data/+/events" event_processor --qos 1 --mode async

# Subscribe with mixed mode (QoS-based routing)
flowerpower-mqtt subscribe "mixed/data" mixed_processor --qos 2 --mode mixed

# List all subscriptions
flowerpower-mqtt list-subscriptions

# List only active subscriptions
flowerpower-mqtt list-subscriptions --active

# Unsubscribe from topic
flowerpower-mqtt unsubscribe "sensors/temperature"
```

### Listening and Monitoring

```bash
# Start listening (blocks until Ctrl+C)
flowerpower-mqtt listen

# Start listening in background
flowerpower-mqtt listen --background

# Start with execution mode override
flowerpower-mqtt listen --override-mode async

# Start with timeout
flowerpower-mqtt listen --timeout 300

# Show current status
flowerpower-mqtt status

# Show status as JSON
flowerpower-mqtt status --json

# Real-time monitoring
flowerpower-mqtt monitor --interval 5

# Monitor for specific duration
flowerpower-mqtt monitor --interval 10 --duration 300
```

### Job Queue Management

```bash
# Check job queue status
flowerpower-mqtt jobs status

# Start RQ worker (shows command to run)
flowerpower-mqtt jobs worker start --count 2

# Check worker status
flowerpower-mqtt jobs worker status
```

### Common CLI Workflows

#### Development Workflow
```bash
# 1. Create and validate configuration
flowerpower-mqtt config create --interactive
flowerpower-mqtt config validate mqtt_config.yml

# 2. Quick testing
flowerpower-mqtt connect
flowerpower-mqtt subscribe "test/+" test_pipeline --qos 0
flowerpower-mqtt listen --timeout 60

# 3. Real-time monitoring
flowerpower-mqtt monitor --interval 5
```

#### Production Workflow
```bash
# 1. Load from version-controlled config
flowerpower-mqtt config validate production_config.yml
flowerpower-mqtt connect --config production_config.yml

# 2. Start with job queue
rq worker mqtt_pipelines --url redis://localhost:6379 &
flowerpower-mqtt listen --background --override-mode async

# 3. Monitor operations
flowerpower-mqtt monitor --json > monitoring.log &
flowerpower-mqtt jobs status
```

### CLI Tips

- Use `--json` flag for machine-readable output in scripts
- Configuration files can be version controlled and shared
- Use `--save-config` to persist CLI-created subscriptions
- The CLI supports shell completion (enable with your shell)
- Use `flowerpower-mqtt --help` to see all available commands
- Each command has detailed help: `flowerpower-mqtt connect --help`

## Documentation

For comprehensive and detailed information about FlowerPower MQTT, including advanced topics, API references, and in-depth usage guides, please refer to our [Full Documentation](https://legout.github.io/flowerpower-mqtt/).

Our documentation has been recently reorganized to provide a more user-friendly navigation structure, making it easier to find the information you need.

## Usage Patterns

### QoS Levels

Choose the appropriate QoS level based on your use case:

```python
# QoS 0: Fire-and-forget (best for high-volume, non-critical data)
await mqtt.subscribe("logs/debug", "log_processor", qos=0)

# QoS 1: At-least-once delivery (good for important events)
await mqtt.subscribe("sensors/data", "data_processor", qos=1)

# QoS 2: Exactly-once delivery (critical business processes)
await mqtt.subscribe("payments/completed", "payment_processor", qos=2)
```

### Execution Modes

```python
# Synchronous: Direct execution (blocking)
await mqtt.subscribe("critical/alerts", "alert_handler", execution_mode="sync")

# Asynchronous: Background execution via RQ
await mqtt.subscribe("batch/data", "batch_processor", execution_mode="async")

# Mixed: QoS-based routing
await mqtt.subscribe("mixed/topic", "mixed_pipeline", execution_mode="mixed")

### Payload Deserialization

Specify how incoming MQTT message payloads should be deserialized:

```python
# JSON (default if not specified for text-based payloads)
await mqtt.subscribe("data/json", "json_processor", deserialization_format="json")

# MessagePack
await mqtt.subscribe("data/msgpack", "msgpack_processor", deserialization_format="msgpack")

# YAML
await mqtt.subscribe("data/yaml", "yaml_processor", deserialization_format="yaml")

# Pickle
await mqtt.subscribe("data/pickle", "pickle_processor", deserialization_format="pickle")

# Protobuf (requires a compiled Protobuf schema)
await mqtt.subscribe("data/protobuf", "protobuf_processor", deserialization_format="protobuf")

# PyArrow IPC (e.g., for Arrow Tables)
await mqtt.subscribe("data/arrow", "arrow_processor", deserialization_format="pyarrow")

# Auto-detection (attempts JSON, MessagePack, YAML, PyArrow, Pickle in order)
await mqtt.subscribe("data/auto", "auto_processor", deserialization_format="auto")
```
```

### Context Manager Usage

```python
async def main():
    async with MQTTPlugin("localhost", base_dir=".") as mqtt:
        await mqtt.subscribe("test/topic", "test_pipeline")
        await mqtt.start_listener()
```

### Bulk Subscriptions

```python
subscriptions = [
    {"topic": "sensors/+/temperature", "pipeline": "temp_monitor", "qos": 1},
    {"topic": "alerts/critical/#", "pipeline": "alert_handler", "qos": 2},
    {"topic": "data/batch/+", "pipeline": "batch_processor", "qos": 0}
]

await mqtt.subscribe_bulk(subscriptions)
```

## Pipeline Integration

Your FlowerPower pipelines will receive MQTT message data as input:

```python
# pipelines/sensor_processor.py
import pandas as pd
from hamilton.function_modifiers import parameterize

def process_mqtt_message(mqtt_message: dict, mqtt_topic: str, mqtt_qos: int) -> dict:
    """Process incoming MQTT message."""
    print(f"Received message from {mqtt_topic} (QoS {mqtt_qos})")
    
    # Access message payload
    sensor_data = mqtt_message.get("sensor_data", {})
    
    # Process the data
    result = {
        "processed_at": mqtt_message["execution_timestamp"],
        "topic": mqtt_topic,
        "temperature": sensor_data.get("temperature"),
        "status": "processed"
    }
    
    return result

def save_results(process_mqtt_message: dict) -> str:
    """Save processing results."""
    # Save to database, file, etc.
    return f"Saved results: {process_mqtt_message['status']}"
```

## Monitoring and Statistics

```python
# Get current subscriptions
subscriptions = mqtt.get_subscriptions()
for sub in subscriptions:
    print(f"Topic: {sub['topic']}, Messages: {sub['message_count']}")

# Get plugin statistics
stats = mqtt.get_statistics()
print(f"Connected: {stats['connected']}")
print(f"Message count: {stats['message_count']}")
print(f"Pipeline executions: {stats['pipeline_count']}")
print(f"Errors: {stats['error_count']}")

# Save current configuration
mqtt.save_config("current_config.yml")
```

## Job Queue Integration

When using RQ for asynchronous processing:

### Start RQ Worker

```bash
# In a separate terminal, start RQ worker
rq worker mqtt_pipelines --url redis://localhost:6379
```

### Monitor Jobs

```python
# Job status is automatically tracked
stats = mqtt.get_statistics()
if "job_queue_stats" in stats:
    print(f"Queue: {stats['job_queue_stats']['queue_name']}")
```

## Error Handling

The plugin includes comprehensive error handling:

```python
from flowerpower_mqtt import MQTTPlugin, ConnectionError, SubscriptionError

try:
    mqtt = MQTTPlugin("invalid.broker.com")
    await mqtt.connect()
except ConnectionError as e:
    print(f"Connection failed: {e}")

try:
    await mqtt.subscribe("test/topic", "nonexistent_pipeline", qos=3)
except SubscriptionError as e:
    print(f"Subscription failed: {e}")
```

## Examples

Check the `examples/` directory for comprehensive, self-contained examples. Each example is organized in its own dedicated folder with complete setup instructions, dependencies, and runnable notebooks.

### Available Examples

- **`examples/basic_usage/`** - Simple synchronous MQTT message processing
- **`examples/async_with_rq/`** - Asynchronous processing with RQ job queue
- **`examples/config_based/`** - Configuration file management and usage
- **`examples/monitoring/`** - Real-time statistics and monitoring
- **`examples/multiple_qos/`** - Different QoS levels and execution modes
- **`examples/cli_vs_programmatic/`** - CLI vs programmatic API comparison

### Example Structure

Each example folder contains:
- `README.md` - Detailed setup and usage instructions
- `pyproject.toml` - Project dependencies and configuration
- `[example_name].py` - Original Python script
- `[example_name].ipynb` - Interactive Jupyter notebook
- `[example_name]_marimo.py` - Marimo notebook for reactive exploration

### Quick Start with Examples

```bash
# Navigate to an example
cd examples/basic_usage

# Install dependencies
uv pip install -e ../..
uv pip install .

# Run the example
uv run python basic_usage.py

# Or explore interactively with Jupyter
uv run jupyter lab basic_usage.ipynb

# Or use Marimo for reactive exploration
uv run marimo run basic_usage_marimo.py
```

### Common Pipeline

The `examples/_common/pipelines/example_pipeline.py` contains a sample FlowerPower pipeline that demonstrates how to process MQTT messages within your data pipelines.

## CLI vs Programmatic Usage

Choose the right approach for your use case:

### Use CLI When:
- **Development & Testing**: Quick iterations and prototyping
- **Operations**: Monitoring, troubleshooting, and administration
- **Configuration Management**: Creating, validating, and editing configurations
- **Simple Use Cases**: Basic MQTT message processing
- **Learning**: Exploring features with immediate feedback
- **Scripting**: Automation with shell scripts

### Use Programmatic API When:
- **Application Integration**: Embedding in larger applications
- **Complex Logic**: Conditional operations and business rules
- **Custom Monitoring**: Integration with existing dashboards
- **Error Handling**: Advanced error handling and recovery
- **Dynamic Behavior**: Runtime decision making
- **Performance Critical**: Fine-tuned control over operations

### Hybrid Approach (Recommended):
Use CLI for setup and operations, programmatic API for application logic:

```python
# Use CLI-generated config in Python code
from flowerpower_mqtt import MQTTPlugin

plugin = MQTTPlugin.from_config("cli_generated_config.yml")
# Add custom business logic here...
```

## Requirements

- Python >=3.11
- FlowerPower
- aiomqtt >=2.0.0
- msgspec >=0.18.0 (high-performance serialization)
- typer[all] >=0.9.0 (CLI framework)
- rich >=13.0.0 (beautiful CLI output)
- Redis (for job queue functionality)
- RQ >=1.15.0 (for async processing)

## Development

```bash
# Clone repository
git clone https://github.com/legout/flowerpower-mqtt.git
cd flowerpower-mqtt

# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Code formatting
black src/
ruff check src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v0.2.0 (Current)
- **Breaking Change**: Migrated from Pydantic to msgspec.Struct for 10-50x performance improvement
- **New**: Comprehensive CLI with beautiful rich output
- **New**: Interactive configuration creation and management
- **New**: Real-time monitoring with rich tables and charts
- **New**: Job queue management via CLI
- **New**: Shell completion support
- **New**: JSON output for scripting and automation
- **Enhanced**: Configuration validation with detailed error messages
- **Enhanced**: Better error handling throughout the codebase

### v0.1.0
- Initial release
- Basic MQTT subscription and pipeline execution
- QoS support (0, 1, 2)
- RQ job queue integration
- Configuration management
- Graceful shutdown handling
- Statistics and monitoring