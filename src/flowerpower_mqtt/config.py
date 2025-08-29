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


class MQTTConfig(Struct):
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


class JobQueueConfig(Struct):
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
    qos: Annotated[int, Meta(extra=_validate_qos)] = 0
    execution_mode: Annotated[str, Meta(extra=_validate_execution_mode)] = "sync"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility."""
        return msgspec.to_builtins(self)


class FlowerPowerMQTTConfig(Struct):
    """Main configuration for FlowerPower MQTT plugin."""
    mqtt: MQTTConfig = MQTTConfig()
    job_queue: JobQueueConfig = JobQueueConfig()
    subscriptions: List[SubscriptionConfig] = msgspec.field(default_factory=list)
    base_dir: str = "."
    log_level: str = "INFO"

    @classmethod
    def from_yaml(cls, file_path: Path) -> "FlowerPowerMQTTConfig":
        """Load configuration from YAML file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Convert nested dictionaries to proper types
        return msgspec.convert(data, cls)
    
    def to_yaml(self, file_path: Path) -> None:
        """Save configuration to YAML file."""
        # Convert struct to dictionary
        data = msgspec.to_builtins(self)
        
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
    
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
    message_count: int = 0
    last_message_time: Optional[float] = None
    error_count: int = 0