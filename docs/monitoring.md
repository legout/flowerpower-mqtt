# Monitoring

`flowerpower-mqtt` provides built-in capabilities for monitoring its operation, including connection status, message counts, pipeline execution statistics, and error tracking. This allows you to gain insights into the health and performance of your MQTT-driven data processing workflows.

Monitoring information is accessible through both the Command Line Interface (CLI) and the programmatic API.

## CLI Monitoring

The `flowerpower-mqtt` CLI offers two primary commands for monitoring: `status` for a snapshot view and `monitor` for real-time updates.

### `flowerpower-mqtt status`

This command provides a summary of the current plugin status and key statistics.

```bash
flowerpower-mqtt status
```

**Example Output:**

```
╭─────────────────────────── Plugin Status ───────────────────────────╮
│ Property             Value                                        │
├─────────────────────────────────────────────────────────────────────┤
│ Connected            ✅ Yes                                        │
│ Broker               localhost:1883                               │
│ Listening            ✅ Yes                                        │
│ Runtime              360.5s                                       │
│ Messages             1250                                         │
│ Pipelines Executed   1245                                         │
│ Errors               5                                            │
│ Subscriptions        2                                            │
│ Job Queue            ✅ Enabled                                    │
╰─────────────────────────────────────────────────────────────────────╯

╭─────────────────────── Subscription Details ────────────────────────╮
│ Topic                 Pipeline            QoS   Mode    Messages  │
├─────────────────────────────────────────────────────────────────────┤
│ sensors/temperature   process_temp_data   1     async   750       │
│ alerts/critical       handle_alert        2     sync    495       │
╰─────────────────────────────────────────────────────────────────────╯
```

**Options:**

*   `--config`, `-c` (`Path`): Specify a configuration file to use.
*   `--json` (`bool`): Output the status as a machine-readable JSON object. This is useful for integrating with other monitoring systems or for scripting.

    ```bash
    flowerpower-mqtt status --json
    ```

### `flowerpower-mqtt monitor`

The `monitor` command provides a real-time, continuously updating view of the plugin's statistics and active subscription activity.

```bash
flowerpower-mqtt monitor [OPTIONS]
```

**Example Output (continuously updates):**

```
Monitor #1 - 1678886400.0

╭──────────────────────── Real-time Statistics ─────────────────────────╮
│ Metric               Value                                          │
├───────────────────────────────────────────────────────────────────────┤
│ Connected            ✅ Yes                                          │
│ Listening            ✅ Yes                                          │
│ Runtime              365.1s                                         │
│ Messages             1260                                           │
│ Pipeline Executions  1255                                           │
│ Errors               5                                              │
╰───────────────────────────────────────────────────────────────────────╯

╭──────────────────────── Active Subscriptions ─────────────────────────╮
│ Topic                 Messages   Pipeline                             │
├───────────────────────────────────────────────────────────────────────┤
│ sensors/temperature   755        process_temp_data                    │
│ alerts/critical       498        handle_alert                         │
╰───────────────────────────────────────────────────────────────────────╯

Press Ctrl+C to stop monitoring...
```

**Options:**

*   `--config`, `-c` (`Path`): Specify a configuration file to use.
*   `--interval`, `-i` (`int`): The update frequency in seconds (default: `5`).
*   `--duration`, `-d` (`int`): The total duration in seconds for which to monitor. If not specified, monitoring runs indefinitely until `Ctrl+C` is pressed.
*   `--json` (`bool`): Output real-time monitoring data as JSON. Each update will print a new JSON object to standard output.

    ```bash
    flowerpower-mqtt monitor --interval 1 --json
    ```

## Programmatic Statistics

You can retrieve the same statistics and subscription information programmatically using methods of the `MQTTPlugin` instance.

### `get_statistics()`

Returns a dictionary containing overall plugin statistics.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    mqtt = MQTTPlugin(broker="localhost", base_dir=".")
    await mqtt.connect()
    
    stats = mqtt.get_statistics()
    print(f"Connected: {stats['connected']}")
    print(f"Total Messages Received: {stats['message_count']}")
    print(f"Pipelines Executed: {stats['pipeline_count']}")
    print(f"Errors: {stats['error_count']}")
    print(f"Listener Running: {stats['running']}")
    print(f"Runtime: {stats['runtime_seconds']:.2f} seconds")
    
    if stats.get("job_queue_enabled"):
        print(f"Job Queue Enabled: Yes")
        print(f"  Queue Name: {stats['job_queue_stats']['queue_name']}")
    
    await mqtt.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

**Returns:**

*   `Dict[str, Any]`: A dictionary with the following keys:
    *   `connected` (`bool`): Whether the plugin is connected to the MQTT broker.
    *   `broker` (`str`): The broker address and port.
    *   `running` (`bool`): Whether the listener is active.
    *   `start_time` (`str`, optional): ISO formatted timestamp when the listener started.
    *   `runtime_seconds` (`float`, optional): How long the listener has been running.
    *   `message_count` (`int`): Total number of MQTT messages processed.
    *   `pipeline_count` (`int`): Total number of pipelines executed (synchronously or asynchronously).
    *   `error_count` (`int`): Total number of errors encountered.
    *   `subscriptions` (`int`): Number of active subscriptions.
    *   `job_queue_enabled` (`bool`): Whether the job queue is enabled.
    *   `job_queue_stats` (`Dict`, optional): Dictionary with job queue specific statistics (e.g., `queue_name`, `type`).

### `get_subscriptions()`

Returns a list of dictionaries, each providing detailed information and runtime statistics for an individual subscription.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    mqtt = MQTTPlugin(broker="localhost", base_dir=".")
    await mqtt.connect()
    await mqtt.subscribe("sensor/data", "process_sensor")
    await mqtt.subscribe("alert/high", "handle_alert")
    
    # Simulate some messages
    # In a real scenario, messages would come from the broker
    # For demonstration, manually update counts (not how it works in practice)
    mqtt.get_subscriptions()[0]['message_count'] = 10
    mqtt.get_subscriptions()[1]['message_count'] = 3
    
    subscriptions_info = mqtt.get_subscriptions()
    for sub in subscriptions_info:
        print(f"Topic: {sub['topic']}")
        print(f"  Pipeline: {sub['pipeline']}")
        print(f"  QoS: {sub['qos']}")
        print(f"  Mode: {sub['execution_mode']}")
        print(f"  Messages Received: {sub['message_count']}")
        print(f"  Errors: {sub['error_count']}")
        print("-" * 20)
    
    await mqtt.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

**Returns:**

*   `List[Dict[str, Any]]`: A list of dictionaries. Each dictionary represents a subscription and includes:
    *   `topic` (`str`): The subscribed MQTT topic pattern.
    *   `pipeline` (`str`): The name of the associated FlowerPower pipeline.
    *   `qos` (`int`): The QoS level of the subscription.
    *   `execution_mode` (`str`): The execution mode for the pipeline.
    *   `message_count` (`int`): Number of messages received on this topic.
    *   `last_message_time` (`float`, optional): Timestamp of the last message received.
    *   `error_count` (`int`): Number of errors encountered for this subscription.

## Interpreting Monitoring Data

*   **`message_count` vs. `pipeline_count`**: A significant discrepancy might indicate issues with pipeline execution (e.g., pipelines failing or taking too long, leading to messages being dropped or not processed).
*   **`error_count`**: Monitor this closely. Non-zero values indicate problems with message handling or pipeline execution. Check logs for details.
*   **`runtime_seconds`**: Provides an idea of how long the plugin has been actively running and processing messages.
*   **Job Queue Statistics**: If using asynchronous processing, monitor the job queue itself (e.g., RQ dashboard, `rqinfo`) to check queue length, worker health, and job failures.