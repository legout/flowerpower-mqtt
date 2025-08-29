"""Custom exceptions for FlowerPower MQTT plugin."""


class FlowerPowerMQTTError(Exception):
    """Base exception for FlowerPower MQTT plugin."""
    pass


class ConnectionError(FlowerPowerMQTTError):
    """Raised when MQTT connection fails."""
    pass


class SubscriptionError(FlowerPowerMQTTError):
    """Raised when MQTT subscription fails."""
    pass


class PipelineExecutionError(FlowerPowerMQTTError):
    """Raised when pipeline execution fails."""
    pass


class JobQueueError(FlowerPowerMQTTError):
    """Raised when job queue operations fail."""
    pass


class ConfigurationError(FlowerPowerMQTTError):
    """Raised when configuration is invalid."""
    pass