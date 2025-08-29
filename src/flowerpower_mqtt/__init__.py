"""
FlowerPower MQTT Plugin

A simple MQTT plugin for FlowerPower that triggers pipeline execution
when messages arrive on subscribed topics, with configurable QoS levels
and optional RQ job queue integration for asynchronous processing.
"""

import asyncio
import logging
import os
import sys
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import importlib.metadata

from .client import MQTTClient
from .listener import MQTTListener
from .config import (
    FlowerPowerMQTTConfig, 
    MQTTConfig, 
    JobQueueConfig,
    SubscriptionConfig
)
from .exceptions import (
    FlowerPowerMQTTError,
    ConnectionError,
    SubscriptionError,
    ConfigurationError
)

__version__ = importlib.metadata.version("flowerpower-mqtt")
__all__ = [
    "MQTTPlugin",
    "FlowerPowerMQTTConfig",
    "MQTTConfig", 
    "JobQueueConfig",
    "SubscriptionConfig",
    "FlowerPowerMQTTError",
    "ConnectionError",
    "SubscriptionError",
    "ConfigurationError"
]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MQTTPlugin:
    """
    Main interface for FlowerPower MQTT plugin.
    
    Provides simple API for connecting to MQTT brokers, subscribing to topics,
    and triggering FlowerPower pipeline execution with support for different
    QoS levels and execution modes.
    """
    
    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        base_dir: str = ".",
        use_job_queue: bool = False,
        redis_url: str = "redis://localhost:6379",
        config: Optional[FlowerPowerMQTTConfig] = None,
        **mqtt_kwargs
    ):
        """
        Initialize MQTT plugin.
        
        Args:
            broker: MQTT broker hostname
            port: MQTT broker port
            base_dir: FlowerPower project base directory
            use_job_queue: Enable RQ job queue for async execution
            redis_url: Redis connection URL for job queue
            config: Complete configuration object (overrides other params)
            **mqtt_kwargs: Additional MQTT client configuration
        """
        # Handle Windows event loop policy for aiomqtt
        if sys.platform.lower() == "win32" or os.name.lower() == "nt":
            try:
                from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
                set_event_loop_policy(WindowsSelectorEventLoopPolicy())
            except ImportError:
                logger.warning("Could not set Windows event loop policy")
        
        # Initialize configuration
        if config is not None:
            self.config = config
        else:
            mqtt_config = MQTTConfig(
                broker=broker,
                port=port,
                **mqtt_kwargs
            )
            
            job_queue_config = JobQueueConfig(
                enabled=use_job_queue,
                redis_url=redis_url
            ) if use_job_queue else JobQueueConfig()
            
            self.config = FlowerPowerMQTTConfig(
                mqtt=mqtt_config,
                job_queue=job_queue_config,
                base_dir=base_dir
            )
        
        # Initialize components
        self.mqtt_client = MQTTClient(self.config.mqtt)
        self.listener: Optional[MQTTListener] = None
        self._connected = False
        
        # Configure logging level
        logging.getLogger().setLevel(getattr(logging, self.config.log_level.upper()))
    
    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> "MQTTPlugin":
        """
        Create plugin instance from configuration file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Configured MQTTPlugin instance
        """
        config = FlowerPowerMQTTConfig.from_yaml(Path(config_path))
        return cls(config=config)
    
    async def connect(self) -> None:
        """Connect to MQTT broker."""
        if self._connected:
            logger.warning("Already connected to MQTT broker")
            return
        
        logger.info(f"Connecting to MQTT broker at {self.config.mqtt.broker}:{self.config.mqtt.port}")
        await self.mqtt_client.connect()
        
        # Initialize listener
        self.listener = MQTTListener(self.mqtt_client, self.config)
        self._connected = True
        
        logger.info("Successfully connected to MQTT broker")
    
    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if not self._connected:
            logger.warning("Not connected to MQTT broker")
            return
        
        logger.info("Disconnecting from MQTT broker")
        
        # Stop listener if running
        if self.listener and self.listener.is_running:
            await self.listener.stop_listener()
        
        await self.mqtt_client.disconnect()
        self._connected = False
        
        logger.info("Successfully disconnected from MQTT broker")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def subscribe(
        self,
        topic: str,
        pipeline_name: str,
        qos: int = 0,
        execution_mode: str = "sync"
    ) -> None:
        """
        Subscribe to MQTT topic and link to FlowerPower pipeline.
        
        Args:
            topic: MQTT topic pattern to subscribe to
            pipeline_name: Name of FlowerPower pipeline to execute
            qos: QoS level (0=at most once, 1=at least once, 2=exactly once)
            execution_mode: Execution mode (sync, async, mixed)
        """
        if not self._connected:
            raise ConnectionError("Not connected to MQTT broker. Call connect() first.")
        
        if qos not in [0, 1, 2]:
            raise SubscriptionError(f"Invalid QoS level: {qos}. Must be 0, 1, or 2.")
        
        if execution_mode not in ["sync", "async", "mixed"]:
            raise SubscriptionError(
                f"Invalid execution mode: {execution_mode}. Must be 'sync', 'async', or 'mixed'."
            )
        
        # Add to configuration
        subscription = SubscriptionConfig(
            topic=topic,
            pipeline=pipeline_name,
            qos=qos,
            execution_mode=execution_mode
        )
        self.config.subscriptions.append(subscription)
        
        # Subscribe via MQTT client
        await self.mqtt_client.subscribe(topic, pipeline_name, qos, execution_mode)
        
        logger.info(
            f"Subscribed to '{topic}' -> pipeline '{pipeline_name}' "
            f"(QoS {qos}, {execution_mode} mode)"
        )
    
    async def subscribe_bulk(self, subscriptions: List[Dict[str, Any]]) -> None:
        """
        Subscribe to multiple topics at once.
        
        Args:
            subscriptions: List of subscription dictionaries
        """
        for sub in subscriptions:
            await self.subscribe(
                topic=sub["topic"],
                pipeline_name=sub["pipeline"],
                qos=sub.get("qos", 0),
                execution_mode=sub.get("execution_mode", "sync")
            )
    
    async def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from MQTT topic.
        
        Args:
            topic: MQTT topic pattern to unsubscribe from
        """
        if not self._connected:
            raise ConnectionError("Not connected to MQTT broker")
        
        await self.mqtt_client.unsubscribe(topic)
        
        # Remove from configuration
        self.config.subscriptions = [
            sub for sub in self.config.subscriptions if sub.topic != topic
        ]
        
        logger.info(f"Unsubscribed from '{topic}'")
    
    async def start_listener(
        self,
        background: bool = False,
        execution_mode: Optional[str] = None
    ) -> None:
        """
        Start listening for MQTT messages.
        
        Args:
            background: If True, run listener in background task
            execution_mode: Override execution mode for all pipelines
        """
        if not self._connected:
            raise ConnectionError("Not connected to MQTT broker. Call connect() first.")
        
        if not self.listener:
            raise ConfigurationError("Listener not initialized")
        
        if not self.config.subscriptions:
            logger.warning("No subscriptions configured")
        
        # Override execution mode if specified
        if execution_mode:
            for sub in self.config.subscriptions:
                sub.execution_mode = execution_mode
        
        logger.info(
            f"Starting listener with {len(self.config.subscriptions)} subscriptions "
            f"(background={background})"
        )
        
        try:
            await self.listener.start_listener(background=background)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, stopping listener")
            await self.stop_listener()
        except Exception as e:
            logger.error(f"Error in listener: {e}")
            raise
    
    async def stop_listener(self, timeout: float = 10.0) -> None:
        """
        Stop MQTT message listener.
        
        Args:
            timeout: Maximum time to wait for graceful shutdown
        """
        if not self.listener:
            logger.warning("No listener to stop")
            return
        
        await self.listener.stop_listener(timeout=timeout)
    
    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Get current subscriptions.
        
        Returns:
            List of subscription information dictionaries
        """
        if not self._connected:
            return [sub.to_dict() for sub in self.config.subscriptions]
        
        subscriptions = []
        for topic, runtime_sub in self.mqtt_client.get_all_subscriptions().items():
            sub_info = {
                "topic": runtime_sub.topic,
                "pipeline": runtime_sub.pipeline,
                "qos": runtime_sub.qos,
                "execution_mode": runtime_sub.execution_mode,
                "message_count": runtime_sub.message_count,
                "last_message_time": runtime_sub.last_message_time,
                "error_count": runtime_sub.error_count
            }
            subscriptions.append(sub_info)
        
        return subscriptions
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get plugin statistics.
        
        Returns:
            Dictionary with current statistics
        """
        stats = {
            "connected": self._connected,
            "broker": f"{self.config.mqtt.broker}:{self.config.mqtt.port}",
            "subscriptions_count": len(self.config.subscriptions),
            "job_queue_enabled": self.config.job_queue.enabled
        }
        
        if self.listener:
            stats.update(self.listener.get_statistics())
        
        return stats
    
    def save_config(self, file_path: Union[str, Path]) -> None:
        """
        Save current configuration to YAML file.
        
        Args:
            file_path: Path where to save configuration
        """
        self.config.to_yaml(Path(file_path))
        logger.info(f"Configuration saved to {file_path}")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to MQTT broker."""
        return self._connected
    
    @property
    def is_listening(self) -> bool:
        """Check if listener is running."""
        return self.listener.is_running if self.listener else False


# Convenience function for simple usage
async def create_simple_mqtt_plugin(
    broker: str = "localhost",
    topic: str = "test/topic", 
    pipeline: str = "test_pipeline",
    qos: int = 0,
    base_dir: str = "."
) -> MQTTPlugin:
    """
    Create and configure a simple MQTT plugin instance.
    
    Args:
        broker: MQTT broker hostname
        topic: MQTT topic to subscribe to
        pipeline: FlowerPower pipeline name
        qos: QoS level
        base_dir: FlowerPower project directory
        
    Returns:
        Configured and connected MQTTPlugin instance
    """
    plugin = MQTTPlugin(broker=broker, base_dir=base_dir)
    await plugin.connect()
    await plugin.subscribe(topic, pipeline, qos)
    return plugin
