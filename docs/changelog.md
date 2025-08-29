# Changelog

This document tracks significant changes and new features in `flowerpower-mqtt`.
## v0.2.1 (Current)

*   **Breaking Change**: Migrated from Pydantic to `msgspec.Struct` including `MQTTMessage`.
*   **New**: Enhanced `MQTTMessage` with comprehensive payload serialization/deserialization capabilities (JSON, YAML, MessagePack, Pickle, Protobuf, PyArrow IPC).
*   **New**: Introduced `deserialization_format` field in `SubscriptionConfig` and `MQTTClient.subscribe()` for specifying expected payload formats.
*   **New**: "Auto" detection mechanism for payload deserialization, attempting formats in a prioritized order (JSON, MessagePack, YAML, PyArrow, Pickle).

## v0.2.0 (Current)

*   **New**: Comprehensive CLI with beautiful `rich` output.
*   **New**: Interactive configuration creation and management via CLI.
*   **New**: Real-time monitoring with `rich` tables and charts.
*   **New**: Job queue management commands via CLI.
*   **New**: Shell completion support for CLI commands.
*   **New**: JSON output option for CLI commands, enabling easier scripting and automation.
*   **Enhanced**: Configuration validation with detailed error messages.
*   **Enhanced**: Better error handling throughout the codebase.

## v0.1.0

*   Initial release.
*   Basic MQTT subscription and FlowerPower pipeline execution.
*   QoS support (0, 1, 2) for MQTT messages.
*   RQ job queue integration for asynchronous processing.
*   Basic configuration management.
*   Graceful shutdown handling.
*   Initial statistics and monitoring capabilities.