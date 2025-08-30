# CLI vs Programmatic Usage

A comprehensive guide comparing CLI and programmatic approaches for using FlowerPower MQTT Plugin.

## Description

This example demonstrates the different ways to use the FlowerPower MQTT Plugin - through the command-line interface (CLI) and programmatic API. It shows when to use each approach and how they complement each other for different use cases.

## CLI vs Programmatic: When to Use What

### CLI Approach
Best for:
- Quick setup and testing
- Development and debugging
- Operations and monitoring
- Interactive configuration
- Simple use cases

### Programmatic Approach
Best for:
- Complex business logic
- Application integration
- Custom error handling
- Dynamic configuration
- Advanced automation

## Configuration Setup

### CLI Configuration
```bash
# Interactive setup
flowerpower-mqtt config create --interactive --job-queue

# One-liner
flowerpower-mqtt config create --output config.yml --job-queue
```

### Programmatic Configuration
```python
from flowerpower_mqtt import FlowerPowerMQTTConfig, MQTTConfig, JobQueueConfig

config = FlowerPowerMQTTConfig(
    mqtt=MQTTConfig(
        broker='mqtt.example.com',
        port=1883,
        keepalive=60
    ),
    job_queue=JobQueueConfig(
        enabled=True,
        redis_url='redis://localhost:6379'
    ),
    base_dir='/path/to/project',
    log_level='INFO'
)
config.to_yaml('config.yml')
```

## Connection and Subscription

### CLI Connection
```bash
# Connect to broker
flowerpower-mqtt connect --broker localhost --job-queue

# Subscribe to topics
flowerpower-mqtt subscribe 'sensors/+' sensor_processor --qos 1
flowerpower-mqtt subscribe 'alerts/#' alert_handler --qos 2

# Start listening
flowerpower-mqtt listen
```

### Programmatic Connection
```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    plugin = MQTTPlugin(
        broker='localhost',
        base_dir='.',
        use_job_queue=True
    )

    await plugin.connect()
    await plugin.subscribe('sensors/+', 'sensor_processor', qos=1)
    await plugin.subscribe('alerts/#', 'alert_handler', qos=2)

    await plugin.start_listener()

asyncio.run(main())
```

## Monitoring and Status

### CLI Monitoring
```bash
# Real-time monitoring
flowerpower-mqtt monitor --interval 5

# Check status
flowerpower-mqtt status

# List subscriptions
flowerpower-mqtt list-subscriptions --active
```

### Programmatic Monitoring
```python
# Get current statistics
stats = plugin.get_statistics()
subscriptions = plugin.get_subscriptions()

print(f'Messages: {stats["message_count"]}')
print(f'Errors: {stats["error_count"]}')

# Custom monitoring logic
for sub in subscriptions:
    if sub['message_count'] > 1000:
        print(f'High activity: {sub["topic"]}')
```

## Decision Matrix

| Scenario | CLI | Programmatic |
|----------|-----|--------------|
| Initial setup | ✅ | ❌ |
| Development/Testing | ✅ | ❌ |
| Production deployment | ✅ | ✅ |
| Application integration | ❌ | ✅ |
| Operations/Monitoring | ✅ | ❌ |
| Configuration management | ✅ | ❌ |
| Dynamic subscriptions | ❌ | ✅ |
| Batch operations | ✅ | ❌ |
| Custom dashboards | ❌ | ✅ |
| DevOps/Automation | ✅ | ✅ |
| Learning/Exploration | ✅ | ❌ |
| Complex error handling | ❌ | ✅ |

## Best Practices

1. **Start with CLI** for quick prototyping
2. **Use programmatic API** for production applications
3. **Combine both approaches** for complex systems
4. **Store configurations** in version control
5. **Use CLI for operations**, programmatic for logic

## How to Run

### Prerequisites

- Python 3.11+
- `uv` package manager
- Docker (for MQTT broker and Redis)

### 1. Start Services

Start both MQTT broker and Redis using Docker:

```bash
docker-compose up -d mqtt redis
```

### 2. Install Dependencies

Install the required Python packages:

```bash
uv pip install -e ../..
uv pip install .
```

### 3. Explore the Examples

This directory contains documentation and examples showing both CLI and programmatic approaches. The examples from `cli_usage.py` and `programmatic_vs_cli.py` have been consolidated into this comprehensive guide.

For practical examples, see the other example directories in the parent `examples/` folder.