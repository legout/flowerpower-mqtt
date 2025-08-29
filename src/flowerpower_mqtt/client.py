"""MQTT client wrapper with QoS support for FlowerPower integration."""

import asyncio
import logging
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass
import time

import aiomqtt

from .config import MQTTConfig, RuntimeSubscription
from .exceptions import ConnectionError, SubscriptionError

logger = logging.getLogger(__name__)


@dataclass
class MQTTMessage:
    """Wrapper for MQTT messages with additional metadata."""
    topic: str
    payload: bytes
    qos: int
    retain: bool
    timestamp: float
    
    @property
    def payload_str(self) -> str:
        """Get payload as string."""
        return self.payload.decode('utf-8', errors='replace')
    
    def payload_json(self) -> Dict[str, Any]:
        """Parse payload as JSON."""
        import json
        return json.loads(self.payload_str)


class MQTTClient:
    """
    MQTT client wrapper with QoS support and subscription management.
    """
    
    def __init__(self, config: MQTTConfig):
        """
        Initialize MQTT client.
        
        Args:
            config: MQTT configuration
        """
        self.config = config
        self._client: Optional[aiomqtt.Client] = None
        self._subscriptions: Dict[str, RuntimeSubscription] = {}
        self._connected = False
        self._message_handlers: List[Callable[[MQTTMessage], None]] = []
        self._lock = asyncio.Lock()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
        
    async def connect(self) -> None:
        """Establish connection to MQTT broker with automatic reconnection."""
        async with self._lock:
            if self._connected:
                return

            last_exception = None

            for attempt in range(self.config.reconnect_retries + 1):
                try:
                    logger.info(f"Connecting to MQTT broker at {self.config.broker}:{self.config.port} (attempt {attempt + 1}/{self.config.reconnect_retries + 1})")

                    # Create aiomqtt client with configuration
                    self._client = aiomqtt.Client(
                        hostname=self.config.broker,
                        port=self.config.port,
                        keepalive=self.config.keepalive,
                        client_id=self.config.client_id,
                        clean_session=self.config.clean_session,
                        username=self.config.username,
                        password=self.config.password,
                    )

                    # Connect using context manager protocol
                    await self._client.__aenter__()
                    self._connected = True

                    logger.info("Successfully connected to MQTT broker")
                    return

                except Exception as e:
                    last_exception = e
                    logger.warning(f"Connection attempt {attempt + 1} failed: {e}")

                    # Don't wait after the last attempt
                    if attempt < self.config.reconnect_retries:
                        # Exponential backoff: delay = base_delay * (2 ^ attempt)
                        delay = self.config.reconnect_delay * (2 ** attempt)
                        logger.info(f"Retrying connection in {delay} seconds...")
                        await asyncio.sleep(delay)

            # All retry attempts failed
            logger.error(f"Failed to connect to MQTT broker after {self.config.reconnect_retries + 1} attempts")
            raise ConnectionError(f"Failed to connect to MQTT broker after {self.config.reconnect_retries + 1} attempts: {last_exception}") from last_exception
    
    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        async with self._lock:
            if not self._connected or self._client is None:
                return
                
            try:
                logger.info("Disconnecting from MQTT broker")
                await self._client.__aexit__(None, None, None)
                self._connected = False
                self._client = None
                
                logger.info("Successfully disconnected from MQTT broker")
                
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                # Don't raise exception during disconnect
    
    async def subscribe(
        self, 
        topic: str, 
        pipeline: str, 
        qos: int = 0,
        execution_mode: str = "sync"
    ) -> None:
        """
        Subscribe to MQTT topic.
        
        Args:
            topic: MQTT topic pattern to subscribe to
            pipeline: FlowerPower pipeline name to execute
            qos: QoS level (0, 1, or 2)
            execution_mode: Pipeline execution mode (sync, async, mixed)
        """
        if not self._connected or self._client is None:
            raise ConnectionError("Client not connected to broker")
            
        if qos not in [0, 1, 2]:
            raise SubscriptionError(f"Invalid QoS level: {qos}. Must be 0, 1, or 2")
            
        try:
            logger.info(f"Subscribing to topic '{topic}' with QoS {qos}")
            
            await self._client.subscribe(topic, qos=qos)
            
            # Store subscription info
            self._subscriptions[topic] = RuntimeSubscription(
                topic=topic,
                pipeline=pipeline,
                qos=qos,
                execution_mode=execution_mode
            )
            
            logger.info(
                f"Successfully subscribed to '{topic}' -> pipeline '{pipeline}'"
            )
            
        except Exception as e:
            logger.error(f"Failed to subscribe to topic '{topic}': {e}")
            raise SubscriptionError(f"Failed to subscribe to topic '{topic}': {e}") from e
    
    async def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from MQTT topic.
        
        Args:
            topic: MQTT topic pattern to unsubscribe from
        """
        if not self._connected or self._client is None:
            raise ConnectionError("Client not connected to broker")
            
        try:
            logger.info(f"Unsubscribing from topic '{topic}'")
            
            await self._client.unsubscribe(topic)
            
            # Remove subscription info
            if topic in self._subscriptions:
                del self._subscriptions[topic]
                
            logger.info(f"Successfully unsubscribed from '{topic}'")
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic '{topic}': {e}")
            raise SubscriptionError(f"Failed to unsubscribe from topic '{topic}': {e}") from e
    
    def add_message_handler(self, handler: Callable[[MQTTMessage], None]) -> None:
        """
        Add message handler function.
        
        Args:
            handler: Function to call when messages arrive
        """
        self._message_handlers.append(handler)
    
    def remove_message_handler(self, handler: Callable[[MQTTMessage], None]) -> None:
        """
        Remove message handler function.
        
        Args:
            handler: Handler function to remove
        """
        if handler in self._message_handlers:
            self._message_handlers.remove(handler)
    
    async def listen_for_messages(self) -> None:
        """
        Listen for incoming MQTT messages and dispatch to handlers.
        """
        if not self._connected or self._client is None:
            raise ConnectionError("Client not connected to broker")
            
        logger.info("Starting message listener")
        
        try:
            async for message in self._client.messages:
                # Update subscription statistics
                topic_str = str(message.topic)
                for topic_pattern, sub in self._subscriptions.items():
                    if message.topic.matches(topic_pattern):
                        sub.message_count += 1
                        sub.last_message_time = time.time()
                        break
                
                # Create wrapped message
                mqtt_message = MQTTMessage(
                    topic=topic_str,
                    payload=message.payload,
                    qos=message.qos,
                    retain=message.retain,
                    timestamp=time.time()
                )
                
                # Dispatch to all handlers
                for handler in self._message_handlers:
                    try:
                        handler(mqtt_message)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
                        
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
            raise
    
    def get_subscription(self, topic: str) -> Optional[RuntimeSubscription]:
        """
        Get subscription info for a topic.
        
        Args:
            topic: Topic pattern
            
        Returns:
            RuntimeSubscription or None if not found
        """
        return self._subscriptions.get(topic)
    
    def get_all_subscriptions(self) -> Dict[str, RuntimeSubscription]:
        """Get all current subscriptions."""
        return self._subscriptions.copy()
    
    def find_subscription_for_topic(self, topic: str) -> Optional[RuntimeSubscription]:
        """
        Find subscription that matches a specific topic.
        
        Args:
            topic: Specific topic to match against patterns
            
        Returns:
            First matching RuntimeSubscription or None
        """
        import aiomqtt
        
        for pattern, subscription in self._subscriptions.items():
            try:
                if aiomqtt.Topic(topic).matches(pattern):
                    return subscription
            except:
                # Fallback to simple string comparison
                if topic == pattern:
                    return subscription
        
        return None
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected
    
    @property
    def subscription_count(self) -> int:
        """Get number of active subscriptions."""
        return len(self._subscriptions)