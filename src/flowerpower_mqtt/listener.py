"""MQTT listener with FlowerPower pipeline execution and job queue integration."""

import asyncio
import logging
import signal
from typing import Optional, Dict, Any, List, Callable
import json
from datetime import datetime

from flowerpower.pipeline import PipelineManager
from flowerpower.job_queue import JobQueueManager

from .client import MQTTClient, MQTTMessage
from .config import FlowerPowerMQTTConfig, JobQueueConfig
from .job_handler import execute_pipeline_job
from .exceptions import PipelineExecutionError, JobQueueError

logger = logging.getLogger(__name__)


class MQTTListener:
    """
    MQTT listener that processes messages and executes FlowerPower pipelines.
    Supports both synchronous and asynchronous execution via RQ job queue.
    """
    
    def __init__(
        self, 
        mqtt_client: MQTTClient,
        config: FlowerPowerMQTTConfig
    ):
        """
        Initialize MQTT listener.
        
        Args:
            mqtt_client: Connected MQTT client instance
            config: FlowerPower MQTT configuration
        """
        self.mqtt_client = mqtt_client
        self.config = config
        
        # FlowerPower managers
        self.pipeline_manager = PipelineManager(base_dir=config.base_dir)
        self.job_queue_manager: Optional[JobQueueManager] = None
        
        # State management
        self._running = False
        self._listener_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Statistics
        self._message_count = 0
        self._pipeline_count = 0
        self._error_count = 0
        self._start_time: Optional[datetime] = None
        
        # Initialize job queue if enabled
        if config.job_queue.enabled:
            self._init_job_queue()
        
        # Register message handler
        self.mqtt_client.add_message_handler(self._handle_message)
    
    def _init_job_queue(self) -> None:
        """Initialize job queue manager."""
        try:
            jq_config = self.config.job_queue
            
            logger.info(f"Initializing job queue: {jq_config.type}")
            
            self.job_queue_manager = JobQueueManager(
                type=jq_config.type,
                name=jq_config.queue_name,
                base_dir=self.config.base_dir
            )
            
            logger.info("Job queue manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize job queue: {e}")
            raise JobQueueError(f"Failed to initialize job queue: {e}") from e
    
    def _handle_message(self, message: MQTTMessage) -> None:
        """
        Handle incoming MQTT message.
        
        Args:
            message: MQTT message to process
        """
        self._message_count += 1
        
        try:
            # Find matching subscription
            subscription = self.mqtt_client.find_subscription_for_topic(message.topic)
            if not subscription:
                logger.warning(f"No subscription found for topic: {message.topic}")
                return
            
            logger.info(
                f"Processing message from topic '{message.topic}' "
                f"-> pipeline '{subscription.pipeline}' (QoS {message.qos})"
            )
            
            # Parse message payload
            message_data = self._parse_message_payload(message)
            
            # Determine execution mode
            execution_mode = self._determine_execution_mode(subscription, message)
            
            # Execute pipeline based on mode
            if execution_mode == "sync":
                self._execute_pipeline_sync(subscription.pipeline, message_data, message)
            elif execution_mode == "async":
                self._execute_pipeline_async(subscription.pipeline, message_data, message)
            else:
                logger.error(f"Unknown execution mode: {execution_mode}")
                self._error_count += 1
                
        except Exception as e:
            logger.error(f"Error handling message from topic '{message.topic}': {e}")
            self._error_count += 1
    
    def _parse_message_payload(self, message: MQTTMessage) -> Dict[str, Any]:
        """
        Parse MQTT message payload.

        Args:
            message: MQTT message

        Returns:
            Parsed payload data
        """
        # Try to parse as JSON
        json_data = message.deserialize_json()
        if json_data is not None:
            return json_data

        # Fallback to string payload
        payload_str = message.payload_str
        if payload_str is not None:
            return {
                "raw_payload": payload_str,
                "payload_bytes": message.payload
            }

        # Binary payload
        return {
            "payload_bytes": message.payload,
            "is_binary": True
        }
    
    def _determine_execution_mode(self, subscription, message: MQTTMessage) -> str:
        """
        Determine execution mode based on configuration and message.
        
        Args:
            subscription: Runtime subscription info
            message: MQTT message
            
        Returns:
            Execution mode ("sync" or "async")
        """
        if not self.config.job_queue.enabled:
            return "sync"
        
        mode = subscription.execution_mode
        
        if mode == "mixed":
            # QoS 2 messages are executed synchronously, others async
            return "sync" if message.qos >= 2 else "async"
        
        return mode
    
    def _execute_pipeline_sync(
        self, 
        pipeline_name: str, 
        message_data: Dict[str, Any],
        message: MQTTMessage
    ) -> None:
        """
        Execute pipeline synchronously.
        
        Args:
            pipeline_name: Name of pipeline to execute
            message_data: Parsed message data
            message: Original MQTT message
        """
        try:
            start_time = datetime.now()
            
            # Prepare pipeline inputs
            pipeline_inputs = {
                "mqtt_message": message_data,
                "mqtt_topic": message.topic,
                "mqtt_qos": message.qos,
                "execution_timestamp": start_time.isoformat(),
                "execution_mode": "sync"
            }
            
            # Execute pipeline
            result = self.pipeline_manager.run(
                name=pipeline_name,
                inputs=pipeline_inputs
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._pipeline_count += 1
            
            logger.info(
                f"Pipeline '{pipeline_name}' completed synchronously "
                f"in {execution_time:.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Synchronous pipeline execution failed: {e}")
            self._error_count += 1
            raise PipelineExecutionError(
                f"Synchronous execution of '{pipeline_name}' failed: {e}"
            ) from e
    
    def _execute_pipeline_async(
        self, 
        pipeline_name: str, 
        message_data: Dict[str, Any],
        message: MQTTMessage
    ) -> Optional[str]:
        """
        Execute pipeline asynchronously via job queue.
        
        Args:
            pipeline_name: Name of pipeline to execute
            message_data: Parsed message data
            message: Original MQTT message
            
        Returns:
            Job ID if successful, None if failed
        """
        if not self.job_queue_manager:
            logger.error("Job queue not available for async execution")
            self._error_count += 1
            return None
        
        try:
            # Enqueue pipeline execution job
            job = self.job_queue_manager.enqueue(
                execute_pipeline_job,
                pipeline_name,
                message_data,
                self.config.base_dir,
                message.topic,
                message.qos,
                {"execution_mode": "async"}
            )
            
            job_id = job.id if hasattr(job, 'id') else str(job)
            self._pipeline_count += 1
            
            logger.info(
                f"Pipeline '{pipeline_name}' queued for async execution "
                f"(job ID: {job_id})"
            )
            
            return job_id
            
        except Exception as e:
            logger.error(f"Async pipeline execution failed: {e}")
            self._error_count += 1
            return None
    
    async def start_listener(self, background: bool = False) -> None:
        """
        Start MQTT message listener.
        
        Args:
            background: If True, run listener in background task
        """
        if self._running:
            logger.warning("Listener already running")
            return
        
        self._running = True
        self._start_time = datetime.now()
        
        logger.info(f"Starting MQTT listener (background={background})")
        
        if background:
            self._listener_task = asyncio.create_task(self._listen_loop())
        else:
            await self._listen_loop()
    
    async def _listen_loop(self) -> None:
        """Main listening loop."""
        try:
            # Set up signal handlers for graceful shutdown
            if not asyncio.current_task().cancelled():
                loop = asyncio.get_event_loop()
                for sig in [signal.SIGINT, signal.SIGTERM]:
                    try:
                        loop.add_signal_handler(sig, self._signal_handler)
                    except NotImplementedError:
                        # Windows doesn't support signal handlers
                        pass
            
            # Start listening for messages
            await self.mqtt_client.listen_for_messages()
            
        except asyncio.CancelledError:
            logger.info("Listener loop cancelled")
        except Exception as e:
            logger.error(f"Error in listener loop: {e}")
            raise
        finally:
            self._running = False
    
    def _signal_handler(self) -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal")
        self._shutdown_event.set()
        if self._listener_task:
            self._listener_task.cancel()
    
    async def stop_listener(self, timeout: float = 10.0) -> None:
        """
        Stop MQTT message listener.
        
        Args:
            timeout: Maximum time to wait for graceful shutdown
        """
        if not self._running:
            logger.warning("Listener not running")
            return
        
        logger.info("Stopping MQTT listener")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel listener task if running in background
        if self._listener_task:
            self._listener_task.cancel()
            
            try:
                await asyncio.wait_for(self._listener_task, timeout=timeout)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                logger.warning("Listener task did not stop gracefully")
        
        self._running = False
        logger.info("MQTT listener stopped")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get listener statistics.
        
        Returns:
            Dictionary with current statistics
        """
        runtime = None
        if self._start_time:
            runtime = (datetime.now() - self._start_time).total_seconds()
        
        stats = {
            "running": self._running,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "runtime_seconds": runtime,
            "message_count": self._message_count,
            "pipeline_count": self._pipeline_count,
            "error_count": self._error_count,
            "subscriptions": len(self.mqtt_client.get_all_subscriptions()),
            "job_queue_enabled": self.config.job_queue.enabled
        }
        
        # Add job queue stats if available
        if self.job_queue_manager:
            try:
                # This would depend on the JobQueueManager implementation
                stats["job_queue_stats"] = {
                    "queue_name": self.config.job_queue.queue_name,
                    "type": self.config.job_queue.type
                }
            except Exception as e:
                logger.debug(f"Could not get job queue stats: {e}")
        
        return stats
    
    @property
    def is_running(self) -> bool:
        """Check if listener is running."""
        return self._running