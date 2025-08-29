# Programmatic Usage

The `flowerpower-mqtt` library provides a powerful and flexible Python API for integrating MQTT message processing directly into your applications. This section details how to use the `MQTTPlugin` class and its associated methods to connect to MQTT brokers, manage subscriptions, and configure pipeline execution.

## Overview of the `MQTTPlugin`

The `MQTTPlugin` class is the primary entry point for programmatic interaction. It allows you to:

*   Establish and manage connections to MQTT brokers.
*   Subscribe and unsubscribe from MQTT topics.
*   Link incoming MQTT messages to FlowerPower pipelines.
*   Control the execution mode (synchronous, asynchronous, or mixed) of pipelines.
*   Load configurations from YAML files or define them directly in code.
*   Access real-time statistics and monitoring data.

## Key Classes and Concepts

Before diving into the specifics, it's helpful to understand the main components you'll interact with:

*   [`MQTTPlugin`](./mqtt-plugin.md): The main class for managing MQTT connections and pipeline execution.
*   [`MQTTConfig`](../core-concepts.md#configuration): Defines the MQTT broker connection parameters.
*   [`JobQueueConfig`](../core-concepts.md#configuration): Configures the optional RQ job queue for asynchronous processing.
*   [`SubscriptionConfig`](./subscriptions.md): Represents a single MQTT topic subscription and its associated FlowerPower pipeline.
*   [`FlowerPowerMQTTConfig`](../core-concepts.md#configuration): The overarching configuration object that combines MQTT, job queue, and subscription settings.

## Asynchronous Nature

`flowerpower-mqtt` is built on `asyncio`, Python's framework for writing concurrent code. This means most of its core operations (connecting, subscribing, listening) are `awaitable` coroutines. When using the programmatic API, you'll typically run these operations within an `asyncio` event loop.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def my_application():
    # Your MQTTPlugin logic here
    pass

if __name__ == "__main__":
    asyncio.run(my_application())
```

This asynchronous design ensures that your application remains responsive while waiting for network I/O (like MQTT messages) and allows for efficient handling of multiple concurrent operations.