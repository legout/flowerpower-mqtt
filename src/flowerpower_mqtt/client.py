"""MQTT client wrapper with QoS support for FlowerPower integration."""

import asyncio
import logging
from typing import Dict, Optional, Callable, Any, List, Type, Union
import time

import aiomqtt
import msgspec
import yaml
import msgpack
import pickle
from google.protobuf.message import Message as ProtobufMessage
import pyarrow as pa

from .config import MQTTConfig, RuntimeSubscription
from .exceptions import ConnectionError, SubscriptionError

logger = logging.getLogger(__name__)


class MQTTMessage(msgspec.Struct):
    """Immutable wrapper for MQTT messages with additional metadata and deserialization support."""

    topic: str
    payload: bytes
    qos: int
    retain: bool
    timestamp: float

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not isinstance(self.topic, str) or not self.topic.strip():
            raise ValueError("Topic must be a non-empty string")

        if not isinstance(self.payload, bytes):
            raise ValueError("Payload must be bytes")

        if self.qos not in (0, 1, 2):
            raise ValueError(f"QoS must be 0, 1, or 2, got {self.qos}")

        if not isinstance(self.timestamp, (int, float)) or self.timestamp < 0:
            raise ValueError("Timestamp must be a non-negative number")

    @property
    def payload_str(self) -> Optional[str]:
        """Attempt to decode payload as UTF-8 string."""
        if not self.payload:
            return ""

        try:
            return self.payload.decode('utf-8')
        except UnicodeDecodeError:
            logger.debug("Payload is not valid UTF-8")
            return None

    def deserialize_json(self) -> Optional[Any]:
        """Deserialize payload as JSON using msgspec."""
        payload_str = self.payload_str
        if payload_str is None:
            logger.debug("Cannot deserialize non-UTF-8 payload as JSON")
            return None

        try:
            return msgspec.json.decode(self.payload, type=Any)
        except Exception as e:
            logger.debug(f"Failed to deserialize as JSON: {e}")
            return None

    def deserialize_yaml(self) -> Optional[Any]:
        """Deserialize payload as YAML."""
        payload_str = self.payload_str
        if payload_str is None:
            logger.debug("Cannot deserialize non-UTF-8 payload as YAML")
            return None

        try:
            return msgspec.yaml.decode(payload_str, type=Any)
        except Exception as e:
            logger.debug(f"Failed to deserialize as YAML: {e}")
            return None

    def deserialize_msgpack(self) -> Optional[Any]:
        """Deserialize payload as MessagePack using msgspec."""
        try:
            return msgspec.msgpack.decode(self.payload, type=Any)
        except Exception as e:
            logger.debug(f"Failed to deserialize as MessagePack: {e}")
            return None

    def deserialize_pickle(self) -> Optional[Any]:
        """Deserialize payload as Python pickle."""
        try:
            return pickle.loads(self.payload)
        except Exception as e:
            logger.debug(f"Failed to deserialize as pickle: {e}")
            return None

    def deserialize_protobuf(self, message_class: Type[ProtobufMessage]) -> Optional[ProtobufMessage]:
        """Deserialize payload as Protocol Buffers."""
        try:
            message = message_class()
            message.ParseFromString(self.payload)
            return message
        except Exception as e:
            logger.debug(f"Failed to deserialize as protobuf: {e}")
            return None

    def deserialize_pyarrow(self) -> Optional[Any]:
        """Deserialize payload as PyArrow IPC format."""
        try:
            reader = pa.ipc.open_stream(self.payload)
            return reader.read_all()
        except Exception as e:
            logger.debug(f"Failed to deserialize as PyArrow IPC: {e}")
            return None

    def serialize_json(self, data: Any) -> bytes:
        """Serialize data to JSON format."""
        try:
            return msgspec.json.encode(data)
        except Exception as e:
            logger.error(f"Failed to serialize as JSON: {e}")
            raise

    def serialize_yaml(self, data: Any) -> bytes:
        """Serialize data to YAML format."""
        try:
            return msgspec.yaml.encode(data)
        except Exception as e:
            logger.error(f"Failed to serialize as YAML: {e}")
            raise

    def serialize_msgpack(self, data: Any) -> bytes:
        """Serialize data to MessagePack format."""
        try:
            return msgspec.msgpack.encode(data)
        except Exception as e:
            logger.error(f"Failed to serialize as MessagePack: {e}")
            raise

    def serialize_pickle(self, data: Any) -> bytes:
        """Serialize data to Python pickle format."""
        try:
            return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Failed to serialize as pickle: {e}")
            raise

    def serialize_protobuf(self, message: ProtobufMessage) -> bytes:
        """Serialize Protocol Buffers message."""
        try:
            return message.SerializeToString()
        except Exception as e:
            logger.error(f"Failed to serialize as protobuf: {e}")
            raise

    def serialize_pyarrow(self, data: Any) -> bytes:
        """Serialize data to PyArrow IPC format."""
        try:
            # Handle different input types
            if isinstance(data, pa.Table):
                table = data
            elif isinstance(data, pa.RecordBatch):
                table = pa.Table.from_batches([data])
            elif isinstance(data, dict):
                # Convert dict to PyArrow table directly
                arrays = []
                names = []
                for key, value in data.items():
                    if isinstance(value, list):
                        arrays.append(pa.array(value))
                    else:
                        arrays.append(pa.array([value]))
                    names.append(key)
                table = pa.Table.from_arrays(arrays, names=names)
            elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                # Handle iterable of dicts (list of records)
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # Convert list of dicts to table
                    arrays = []
                    names = list(data[0].keys())
                    for name in names:
                        values = [record.get(name) for record in data]
                        arrays.append(pa.array(values))
                    table = pa.Table.from_arrays(arrays, names=names)
                else:
                    raise ValueError("Unsupported data type for PyArrow serialization")
            else:
                raise ValueError("Unsupported data type for PyArrow serialization")

            sink = pa.BufferOutputStream()
            with pa.ipc.new_stream(sink, table.schema) as writer:
                writer.write(table)
            return sink.getvalue().to_pybytes()
        except Exception as e:
            logger.error(f"Failed to serialize as PyArrow IPC: {e}")
            raise

    def serialize(self, format_name: str, data: Any, **kwargs) -> bytes:
        """
        Serialize data using the specified format.

        Args:
            format_name: Format name ('json', 'yaml', 'msgpack', 'pickle', 'protobuf', 'pyarrow')
            data: Data to serialize
            **kwargs: Additional arguments for specific formats

        Returns:
            Serialized data as bytes

        Raises:
            ValueError: If format is not supported
        """
        format_name = format_name.lower()

        if format_name == 'json':
            return self.serialize_json(data)
        elif format_name == 'yaml':
            return self.serialize_yaml(data)
        elif format_name == 'msgpack':
            return self.serialize_msgpack(data)
        elif format_name == 'pickle':
            return self.serialize_pickle(data)
        elif format_name == 'protobuf':
            if 'message' in kwargs:
                return self.serialize_protobuf(kwargs['message'])
            else:
                raise ValueError("protobuf format requires 'message' kwarg with ProtobufMessage instance")
        elif format_name == 'pyarrow':
            return self.serialize_pyarrow(data)
        else:
            raise ValueError(f"Unsupported serialization format: {format_name}")

    def deserialize_auto(self) -> Optional[Any]:
        """
        Automatically detect and deserialize payload format.

        Detection order (most common to least common):
        1. JSON - Most common for MQTT payloads
        2. MessagePack - Efficient binary format
        3. YAML - Human-readable structured data
        4. PyArrow IPC - Columnar data format
        5. Pickle - Python-specific binary format

        Returns:
            Deserialized data or None if no format matches
        """
        # Try JSON first (most common)
        result = self.deserialize_json()
        if result is not None:
            logger.debug("Auto-detected format: JSON")
            return result

        # Try MessagePack (efficient binary)
        result = self.deserialize_msgpack()
        if result is not None:
            logger.debug("Auto-detected format: MessagePack")
            return result

        # Try YAML (human-readable)
        result = self.deserialize_yaml()
        if result is not None:
            logger.debug("Auto-detected format: YAML")
            return result

        # Try PyArrow IPC (columnar data)
        result = self.deserialize_pyarrow()
        if result is not None:
            logger.debug("Auto-detected format: PyArrow IPC")
            return result

        # Try Pickle (Python-specific, least safe)
        result = self.deserialize_pickle()
        if result is not None:
            logger.debug("Auto-detected format: Pickle")
            return result

        # No format detected
        logger.debug("Could not auto-detect payload format")
        return None

    def deserialize(self, format_name: str, **kwargs) -> Optional[Any]:
        """
        Deserialize payload using the specified format.

        Args:
            format_name: Format name ('json', 'yaml', 'msgpack', 'pickle', 'protobuf', 'pyarrow')
            **kwargs: Additional arguments for specific formats

        Returns:
            Deserialized data or None if deserialization fails

        Raises:
            ValueError: If format is not supported
        """
        format_name = format_name.lower()

        if format_name == 'auto':
            return self.deserialize_auto()
        elif format_name == 'json':
            return self.deserialize_json()
        elif format_name == 'yaml':
            return self.deserialize_yaml()
        elif format_name == 'msgpack':
            return self.deserialize_msgpack()
        elif format_name == 'pickle':
            return self.deserialize_pickle()
        elif format_name == 'protobuf':
            if 'message_class' in kwargs:
                return self.deserialize_protobuf(kwargs['message_class'])
            else:
                raise ValueError("protobuf format requires 'message_class' kwarg with message type")
        elif format_name == 'pyarrow':
            return self.deserialize_pyarrow()
        else:
            raise ValueError(f"Unsupported deserialization format: {format_name}")

    def is_empty_payload(self) -> bool:
        """Check if payload is empty."""
        return len(self.payload) == 0

    def get_payload_size(self) -> int:
        """Get payload size in bytes."""
        return len(self.payload)


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
                        identifier=self.config.client_id,
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
        execution_mode: str = "sync",
        deserialization_format: str = "auto"
    ) -> None:
        """
        Subscribe to MQTT topic.

        Args:
            topic: MQTT topic pattern to subscribe to
            pipeline: FlowerPower pipeline name to execute
            qos: QoS level (0, 1, or 2)
            execution_mode: Pipeline execution mode (sync, async, mixed)
            deserialization_format: Format to use for deserializing message payloads
                                   (json, yaml, msgpack, pickle, protobuf, pyarrow, auto)
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
                execution_mode=execution_mode,
                deserialization_format=deserialization_format
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
                # Convert payload to bytes to match MQTTMessage type
                if isinstance(message.payload, bytes):
                    payload_bytes = message.payload
                elif isinstance(message.payload, str):
                    payload_bytes = message.payload.encode('utf-8')
                else:
                    payload_bytes = str(message.payload).encode('utf-8')

                mqtt_message = MQTTMessage(
                    topic=topic_str,
                    payload=payload_bytes,
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