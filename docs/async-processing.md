# Asynchronous Processing

`flowerpower-mqtt` can offload the execution of FlowerPower pipelines to a job queue, enabling asynchronous processing. This is particularly useful for long-running or computationally intensive pipelines, ensuring that the MQTT listener remains responsive and can handle high message throughput.

## When to Use Asynchronous Processing

Consider using asynchronous processing with a job queue in the following scenarios:

*   **Long-running Pipelines**: If your FlowerPower pipelines take a significant amount of time to execute (e.g., several seconds to minutes), running them synchronously would block the MQTT listener, potentially causing message backlogs or disconnections.
*   **High Message Throughput**: For applications receiving a large volume of MQTT messages, asynchronous processing allows the system to quickly acknowledge messages and queue pipeline executions without being bottlenecked by the processing time of individual pipelines.
*   **Decoupling**: Separating the message reception and pipeline execution logic provides better system decoupling, making it more resilient and scalable.
*   **Distributed Processing**: A job queue allows you to distribute pipeline execution across multiple worker processes or even different machines, horizontally scaling your processing capabilities.
*   **Reliability and Retries**: Job queues often provide built-in mechanisms for retrying failed jobs, improving the overall reliability of your pipeline executions.

## Configuration

To enable asynchronous processing, you need to configure the `job_queue` section in your `flowerpower-mqtt` configuration.

```yaml
# mqtt_config.yml
job_queue:
  enabled: true
  type: "rq" # Currently only "rq" is supported
  redis_url: "redis://localhost:6379" # Your Redis connection URL
  queue_name: "mqtt_pipelines" # Name of the RQ queue
  worker_count: 4 # Recommended number of RQ workers
  max_retries: 3 # Max retries for failed jobs
```

*   `enabled` (`bool`): Set to `true` to activate the job queue.
*   `type` (`str`): Specifies the type of job queue. Currently, only `"rq"` (RQ - Redis Queue) is supported.
*   `redis_url` (`str`): The connection URL for your Redis server. Redis is required by RQ to store job data and manage queues.
*   `queue_name` (`str`): The name of the RQ queue that `flowerpower-mqtt` will enqueue jobs into. Your RQ workers must listen to this same queue name.
*   `worker_count` (`int`): This is a recommended value for the number of RQ workers you might want to run. It does not automatically start workers.
*   `max_retries` (`int`): The maximum number of times a failed job will be retried by RQ.

## RQ Worker

While `flowerpower-mqtt` enqueues jobs, it does not execute them. You need to run separate RQ worker processes that listen to the configured queue and execute the enqueued FlowerPower pipelines.

### Starting an RQ Worker

You can start an RQ worker from your terminal. Ensure you have `rq` installed (`pip install rq`) and that your Redis server is running.

```bash
# In a separate terminal, from your project's root directory
rq worker mqtt_pipelines --url redis://localhost:6379
```

*   Replace `mqtt_pipelines` with the `queue_name` specified in your `flowerpower-mqtt` configuration.
*   Replace `redis://localhost:6379` with your `redis_url`.

You can run multiple RQ workers to process jobs concurrently. Each worker will pick up jobs from the queue as they become available.

### Managing Workers via CLI

The `flowerpower-mqtt` CLI provides convenience commands for managing RQ workers:

*   **`flowerpower-mqtt jobs worker status`**: Checks if RQ workers are running for the configured queue.
*   **`flowerpower-mqtt jobs worker start --count N`**: Provides the command to manually start `N` RQ workers.
*   **`flowerpower-mqtt jobs worker stop`**: Attempts to stop running RQ worker processes.

## Job Lifecycle

1.  **Message Reception**: `flowerpower-mqtt` receives an MQTT message on a subscribed topic.
2.  **Execution Mode Check**: If the subscription's `execution_mode` is `"async"` or `"mixed"` (and QoS is 0/1), the pipeline execution is prepared as a job.
3.  **Job Enqueueing**: The job is enqueued into the configured RQ queue (e.g., `mqtt_pipelines`) in Redis.
4.  **Worker Processing**: An available RQ worker picks up the job from the queue.
5.  **Pipeline Execution**: The worker executes the specified FlowerPower pipeline, passing the MQTT message data as input.
6.  **Job Completion/Failure**:
    *   If the pipeline completes successfully, the job is marked as finished.
    *   If the pipeline fails, the job is marked as failed, and RQ may retry it based on the `max_retries` setting.

## Monitoring Jobs

You can monitor the status of enqueued and executed jobs using both the CLI and programmatic methods.

### CLI Monitoring

Use the `flowerpower-mqtt jobs status` command to get an overview of the job queue:

```bash
flowerpower-mqtt jobs status
```

This command provides information about whether the job queue is enabled and details about the queue name and type.

### Programmatic Monitoring

The `MQTTPlugin.get_statistics()` method includes information about the job queue if it's enabled.

```python
import asyncio
from flowerpower_mqtt import MQTTPlugin

async def main():
    mqtt = MQTTPlugin.from_config("mqtt_config.yml")
    await mqtt.connect()
    
    stats = mqtt.get_statistics()
    if stats.get("job_queue_enabled"):
        print(f"Job Queue Name: {stats['job_queue_stats']['queue_name']}")
        print(f"Job Queue Type: {stats['job_queue_stats']['type']}")
        # Additional RQ-specific monitoring would require direct RQ API interaction
    
    await mqtt.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

For more detailed job monitoring (e.g., viewing individual job statuses, retries, or worker health), you would typically use RQ's built-in tools like `rqinfo` or integrate with a monitoring dashboard that supports RQ.