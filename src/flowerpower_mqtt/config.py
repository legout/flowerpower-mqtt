"""Configuration management for FlowerPower MQTT plugin."""

from typing import Optional, Dict, Any, List, Annotated
from dataclasses import dataclass
import msgspec
from msgspec import Struct, Meta
import yaml
from pathlib import Path


def _validate_qos(value: int) -> int:
    """Validate QoS level."""
    if value not in [0, 1, 2]:
        raise ValueError(f"QoS must be 0, 1, or 2, got {value}")
    return value


def _validate_execution_mode(value: str) -> str:
    """Validate execution mode."""
    if value not in ["sync", "async", "mixed"]:
        raise ValueError(f"Execution mode must be 'sync', 'async', or 'mixed', got '{value}'")
    return value


def _validate_deserialization_format(value: str) -> str:
    """Validate deserialization format."""
    supported_formats = ["json", "yaml", "msgpack", "pickle", "protobuf", "pyarrow", "auto"]
    if value not in supported_formats:
        raise ValueError(f"Deserialization format must be one of {supported_formats}, got '{value}'")
    return value



class MQTTConfig(Struct, frozen=True):
    """MQTT broker configuration."""
    broker: str = "localhost"
    port: int = 1883
    keepalive: int = 60
    client_id: Optional[str] = None
    clean_session: bool = True
    username: Optional[str] = None
    password: Optional[str] = None
    reconnect_retries: int = 5
    reconnect_delay: int = 5


class JobQueueConfig(Struct, frozen=True):
    """Job queue configuration."""
    enabled: bool = False
    type: str = "rq"
    redis_url: str = "redis://localhost:6379"
    queue_name: str = "mqtt_pipelines"
    worker_count: int = 4
    max_retries: int = 3


class SubscriptionConfig(Struct):
    """Individual subscription configuration."""
    topic: str
    pipeline: str
    qos: int = 0
    execution_mode: str = "sync"
    deserialization_format: str = "auto"

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        _validate_qos(self.qos)
        _validate_execution_mode(self.execution_mode)
        _validate_deserialization_format(self.deserialization_format)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility."""
        return msgspec.to_builtins(self)


class FlowerPowerMQTTConfig(Struct):
    """Main configuration for FlowerPower MQTT plugin."""
    mqtt: MQTTConfig = msgspec.field(default_factory=lambda: MQTTConfig())
    job_queue: JobQueueConfig = msgspec.field(default_factory=lambda: JobQueueConfig())
    subscriptions: List[SubscriptionConfig] = msgspec.field(default_factory=list)
    base_dir: str = "."
    log_level: str = "INFO"

    @classmethod
    def from_yaml(cls, file_path: Path) -> "FlowerPowerMQTTConfig":
        """Load configuration from YAML file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            return msgspec.yaml.decode(f.read(), type=cls)
        

    
    def to_yaml(self, file_path: Path) -> None:
        """Save configuration to YAML file."""
        # Convert struct to dictionary
        data = msgspec.to_builtins(self)
        
        with open(file_path, 'wb') as f:
            f.write(msgspec.yaml.encode(data))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility."""
        return msgspec.to_builtins(self)


@dataclass
class RuntimeSubscription:
    """Runtime subscription data with additional metadata."""
    topic: str
    pipeline: str
    qos: int = 0
    execution_mode: str = "sync"
    deserialization_format: str = "auto"
    message_count: int = 0
    last_message_time: Optional[float] = None
    error_count: int = 0