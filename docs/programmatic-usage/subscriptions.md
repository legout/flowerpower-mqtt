# Subscriptions

Managing MQTT subscriptions is a core function of `flowerpower-mqtt`. This section details how to programmatically subscribe to topics, specify Quality of Service (QoS) levels, define execution modes for pipelines, and retrieve current subscription information.

## Subscribing to Topics

The `subscribe()` method allows you to link an MQTT topic pattern to a FlowerPower pipeline.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def setup_subscriptions(mqtt: MQTTPlugin):
    # Subscribe to a single topic with default QoS 0 and sync execution
    await mqtt.subscribe("sensor/temperature", "process_temperature")

    # Subscribe with QoS 1 and asynchronous execution
    await mqtt.subscribe("data/logs", "store_logs", qos=1, execution_mode="async")

    # Subscribe with QoS 2 and mixed execution mode
    await mqtt.subscribe("critical/alerts", "handle_alert", qos=2, execution_mode="mixed")

async def main():
    async with MQTTPlugin(broker="localhost", base_dir=".") as mqtt:
        await setup_subscriptions(mqtt)
        await mqtt.start_listener()

if __name__ == "__main__":
    asyncio.run(main())
```

**Parameters:**

*   `topic` (`str`): The MQTT topic pattern to subscribe to. This can include wildcards (`+` for single-level, `#` for multi-level).
*   `pipeline_name` (`str`): The name of the FlowerPower pipeline to execute when a message arrives on this topic.
*   `qos` (`int`, optional): The Quality of Service level for the subscription. Must be 0, 1, or 2. Defaults to 0.
    *   **0 (At most once)**: Messages are delivered at most once, or they may not be delivered at all. No acknowledgment is sent by the receiver, and no retransmission is performed by the sender.
    *   **1 (At least once)**: Messages are guaranteed to arrive at least once. The receiver sends an acknowledgment (PUBACK), and the sender retransmits if no PUBACK is received within a certain time. Duplicate messages are possible.
    *   **2 (Exactly once)**: Messages are guaranteed to arrive exactly once. This involves a four-way handshake between sender and receiver to ensure no duplication and guaranteed delivery.
*   `execution_mode` (`str`, optional): The execution mode for the linked pipeline. Must be `"sync"`, `"async"`, or `"mixed"`. Defaults to `"sync"`. See [Core Concepts - Execution Modes](../core-concepts.md#execution-modes) for details.

**Exceptions:**

*   [`ConnectionError`](../advanced-topics.md#error-handling): If the plugin is not connected to the MQTT broker.
*   [`SubscriptionError`](../advanced-topics.md#error-handling): If an invalid QoS level or execution mode is provided.

## Bulk Subscriptions

For convenience, you can subscribe to multiple topics at once using the `subscribe_bulk()` method. This method takes a list of dictionaries, where each dictionary represents a subscription with the same parameters as the `subscribe()` method.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def setup_bulk_subscriptions(mqtt: MQTTPlugin):
    subscriptions_list = [
        {"topic": "sensors/+/temperature", "pipeline": "temp_monitor", "qos": 1, "execution_mode": "async"},
        {"topic": "alerts/critical/#", "pipeline": "alert_handler", "qos": 2, "execution_mode": "sync"},
        {"topic": "data/batch/+", "pipeline": "batch_processor", "qos": 0, "execution_mode": "async"}
    ]
    await mqtt.subscribe_bulk(subscriptions_list)

async def main():
    async with MQTTPlugin(broker="localhost", base_dir=".") as mqtt:
        await setup_bulk_subscriptions(mqtt)
        await mqtt.start_listener()

if __name__ == "__main__":
    asyncio.run(main())
```

**Parameters:**

*   `subscriptions` (`List[Dict[str, Any]]`): A list of dictionaries, each containing `topic`, `pipeline`, `qos` (optional), and `execution_mode` (optional) keys.

## Unsubscribing from Topics

The `unsubscribe()` method allows you to remove an existing subscription.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    async with MQTTPlugin(broker="localhost", base_dir=".") as mqtt:
        await mqtt.subscribe("test/topic", "test_pipeline")
        # ... later ...
        await mqtt.unsubscribe("test/topic")

if __name__ == "__main__":
    asyncio.run(main())
```

**Parameters:**

*   `topic` (`str`): The exact MQTT topic pattern that was previously subscribed to.

**Exceptions:**

*   [`ConnectionError`](../advanced-topics.md#error-handling): If the plugin is not connected to the MQTT broker.

## Listing Subscriptions

You can retrieve a list of all currently active subscriptions using the `get_subscriptions()` method. This returns a list of dictionaries, each containing details about a subscription, including runtime statistics like message counts.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    async with MQTTPlugin(broker="localhost", base_dir=".") as mqtt:
        await mqtt.subscribe("sensors/temp", "temp_pipeline")
        await mqtt.subscribe("sensors/hum", "hum_pipeline")

        # Get current subscriptions
        subscriptions = mqtt.get_subscriptions()
        for sub in subscriptions:
            print(f"Topic: {sub['topic']}, Pipeline: {sub['pipeline']}, Messages: {sub.get('message_count', 0)}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Returns:**

*   `List[Dict[str, Any]]`: A list of dictionaries, where each dictionary contains:
    *   `topic` (`str`): The subscribed topic pattern.
    *   `pipeline` (`str`): The name of the associated FlowerPower pipeline.
    *   `qos` (`int`): The QoS level of the subscription.
    *   `execution_mode` (`str`): The execution mode for the pipeline.
    *   `message_count` (`int`): The number of messages received on this topic since the listener started.
    *   `last_message_time` (`float`, optional): Timestamp of the last message received.
    *   `error_count` (`int`): The number of errors encountered for this subscription.
