# Advanced Topics

This section covers more advanced aspects of `flowerpower-mqtt`, including error handling, graceful shutdown procedures, context manager usage, and automatic reconnection mechanisms.

## Error Handling

`flowerpower-mqtt` is designed with robust error handling to provide informative feedback when issues arise. The library defines a hierarchy of custom exceptions, all inheriting from `FlowerPowerMQTTError`.

*   [`FlowerPowerMQTTError`](#flowerpowermqt-error): Base exception for all `flowerpower-mqtt` errors.
*   [`ConnectionError`](#connectionerror): Raised when there are issues connecting to or disconnecting from the MQTT broker.
*   [`SubscriptionError`](#subscriptionerror): Raised when there are problems with subscribing to or unsubscribing from MQTT topics (e.g., invalid QoS level).
*   [`ConfigurationError`](#configurationerror): Raised when there are issues with the `flowerpower-mqtt` configuration (e.g., invalid settings, missing required fields).
*   [`PipelineExecutionError`](#pipelineexecutionerror): Raised when a FlowerPower pipeline fails during execution.
*   [`JobQueueError`](#jobqueueerror): Raised when there are issues related to the job queue (e.g., failed initialization).

You should wrap your `flowerpower-mqtt` operations in `try-except` blocks to gracefully handle these exceptions.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin, ConnectionError, SubscriptionError, ConfigurationError

async def main():
    try:
        # Example: Connection error
        mqtt_bad_broker = MQTTPlugin(broker="nonexistent.broker.com", base_dir=".")
        await mqtt_bad_broker.connect()
    except ConnectionError as e:
        print(f"Caught ConnectionError: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {type(e).__name__}: {e}")

    try:
        # Example: Subscription error (invalid QoS)
        mqtt_valid = MQTTPlugin(broker="localhost", base_dir=".")
        await mqtt_valid.connect()
        await mqtt_valid.subscribe("test/topic", "my_pipeline", qos=5) # Invalid QoS
    except SubscriptionError as e:
        print(f"Caught SubscriptionError: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {type(e).__name__}: {e}")
    finally:
        if mqtt_valid.is_connected:
            await mqtt_valid.disconnect()

    try:
        # Example: Configuration error (e.g., missing base_dir if not provided in config)
        # This would typically happen during MQTTPlugin initialization if config is invalid
        pass # Configuration errors are usually caught during from_config or __init__
    except ConfigurationError as e:
        print(f"Caught ConfigurationError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Logging Errors

In addition to raising exceptions, `flowerpower-mqtt` extensively uses Python's standard `logging` module to report events and errors. You can configure the logging level in your `mkdocs.yml` file (`log_level` parameter) or programmatically.

It's recommended to configure your application's logging to capture `ERROR` and `WARNING` level messages from `flowerpower_mqtt` for effective troubleshooting.

## Graceful Shutdown

`flowerpower-mqtt` is designed to shut down gracefully, ensuring that all pending operations are completed and resources are released cleanly.

When the listener is running (via `mqtt.start_listener()`), it listens for `Ctrl+C` (KeyboardInterrupt) signals. Upon receiving such a signal, it initiates a graceful shutdown sequence:

1.  Logs an informational message about the shutdown.
2.  Attempts to stop the internal message listener task.
3.  Disconnects from the MQTT broker, which also cleans up any active subscriptions.

You can also explicitly stop the listener programmatically using `stop_listener()`.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    mqtt = MQTTPlugin(broker="localhost", base_dir=".")
    await mqtt.connect()
    await mqtt.subscribe("test/topic", "test_pipeline")
    
    # Start listener in background
    listener_task = asyncio.create_task(mqtt.start_listener(background=True))
    
    print("Listener started in background. Running for 5 seconds...")
    await asyncio.sleep(5)
    
    print("Stopping listener gracefully...")
    await mqtt.stop_listener()
    
    # Wait for the background task to finish (optional but good practice)
    await listener_task
    
    print("Listener stopped and resources released.")
    await mqtt.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Context Manager Usage

For robust resource management, especially in asynchronous applications, it is highly recommended to use `MQTTPlugin` as an asynchronous context manager (`async with`).

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def run_my_app():
    async with MQTTPlugin(broker="localhost", base_dir=".") as mqtt:
        # Connection is automatically established when entering the 'async with' block
        print("Connected to MQTT broker.")
        
        await mqtt.subscribe("data/sensors", "process_sensor_data")
        print("Subscribed to 'data/sensors'.")
        
        print("Starting listener...")
        await mqtt.start_listener()
        
        # When the 'async with' block exits (either normally or due to an exception),
        # the 'mqtt.disconnect()' method is automatically called, ensuring
        # a clean shutdown and resource release.
    
    print("Disconnected from MQTT broker.")

if __name__ == "__main__":
    asyncio.run(run_my_app())
```

Using the context manager ensures that `connect()` is called upon entry and `disconnect()` is called upon exit, even if exceptions occur within the block.

## Automatic Reconnection

The `MQTTClient` (used internally by `MQTTPlugin`) is designed to handle temporary disconnections from the MQTT broker automatically. It implements a reconnection strategy with configurable retries and exponential backoff.

*   **`reconnect_retries`**: The maximum number of times `flowerpower-mqtt` will attempt to reconnect to the broker after a disconnection.
*   **`reconnect_delay`**: The base delay in seconds used for exponential backoff between reconnection attempts. The delay increases with each failed attempt (e.g., `delay * (2 ** attempt)`).

These parameters can be configured in your `mqtt` configuration section:

```yaml
mqtt:
  broker: "mqtt.example.com"
  reconnect_retries: 10 # Try to reconnect 10 times
  reconnect_delay: 5   # Start with 5 seconds delay, then 10s, 20s, etc.
```

During reconnection attempts, `flowerpower-mqtt` will log warnings and informational messages. If all reconnection attempts fail, a `ConnectionError` will be raised.