"""
Example scripts for FlowerPower MQTT Plugin.

This directory contains various examples demonstrating different
usage patterns and features of the plugin:

- basic_usage.py: Simple synchronous MQTT message processing
- async_with_rq.py: Asynchronous processing using RQ job queue
- config_based.py: Configuration file-based setup
- multiple_qos.py: Different QoS levels and their use cases
- monitoring.py: Statistics and monitoring capabilities
- example_pipeline.py: Sample FlowerPower pipeline for MQTT data

To run any example:
    python -m flowerpower_mqtt.examples.basic_usage
    python -m flowerpower_mqtt.examples.async_with_rq
    etc.
"""

__all__ = [
    "basic_usage",
    "async_with_rq", 
    "config_based",
    "multiple_qos",
    "monitoring",
    "example_pipeline"
]