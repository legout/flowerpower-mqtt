"""RQ job handler functions for pipeline execution."""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from flowerpower.pipeline import PipelineManager
from flowerpower.job_queue import JobQueueManager

from .exceptions import PipelineExecutionError

logger = logging.getLogger(__name__)


def execute_pipeline_job(
    pipeline_name: str, 
    message_data: Dict[str, Any], 
    base_dir: str,
    topic: str,
    qos: int,
    execution_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    RQ job function for executing FlowerPower pipelines.
    
    Args:
        pipeline_name: Name of the pipeline to execute
        message_data: MQTT message data to pass as pipeline input
        base_dir: FlowerPower project base directory
        topic: MQTT topic the message came from
        qos: QoS level of the message
        execution_metadata: Additional metadata for execution
    
    Returns:
        Dict containing execution status and results
    """
    start_time = datetime.now()
    
    try:
        logger.info(
            f"Starting pipeline execution: {pipeline_name} "
            f"for topic {topic} (QoS {qos})"
        )
        
        # Initialize pipeline manager
        pm = PipelineManager(base_dir=base_dir)
        
        # Prepare pipeline inputs
        pipeline_inputs = {
            "mqtt_message": message_data,
            "mqtt_topic": topic,
            "mqtt_qos": qos,
            "execution_timestamp": start_time.isoformat(),
            **(execution_metadata or {})
        }
        
        # Execute the pipeline
        result = pm.run(
            name=pipeline_name,
            inputs=pipeline_inputs
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        success_result = {
            "status": "success",
            "pipeline_name": pipeline_name,
            "topic": topic,
            "qos": qos,
            "execution_time": execution_time,
            "start_time": start_time.isoformat(),
            "result": result
        }
        
        logger.info(
            f"Pipeline {pipeline_name} completed successfully "
            f"in {execution_time:.2f}s"
        )
        
        return success_result
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        
        error_result = {
            "status": "error",
            "pipeline_name": pipeline_name,
            "topic": topic,
            "qos": qos,
            "execution_time": execution_time,
            "start_time": start_time.isoformat(),
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        logger.error(
            f"Pipeline {pipeline_name} failed after {execution_time:.2f}s: {e}"
        )
        
        # Re-raise for RQ to handle retries
        raise PipelineExecutionError(
            f"Pipeline '{pipeline_name}' execution failed: {e}"
        ) from e


def get_job_status(job_id: str, job_queue_manager: JobQueueManager) -> Dict[str, Any]:
    """
    Get the status of a job.
    
    Args:
        job_id: RQ job ID
        job_queue_manager: JobQueueManager instance
        
    Returns:
        Dict containing job status information
    """
    try:
        job = job_queue_manager.get_job(job_id)
        if job is None:
            return {"status": "not_found", "job_id": job_id}
        
        return {
            "status": job.get_status(),
            "job_id": job_id,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "result": job.result if job.is_finished else None,
            "exc_info": job.exc_info if job.is_failed else None
        }
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {e}")
        return {
            "status": "error",
            "job_id": job_id,
            "error": str(e)
        }


def cleanup_completed_jobs(
    job_queue_manager: JobQueueManager,
    max_age_hours: int = 24
) -> Dict[str, int]:
    """
    Clean up completed jobs older than specified age.
    
    Args:
        job_queue_manager: JobQueueManager instance
        max_age_hours: Maximum age of jobs to keep
        
    Returns:
        Dict with cleanup statistics
    """
    try:
        # This would depend on the specific JobQueueManager implementation
        # For now, return a placeholder
        logger.info(f"Job cleanup requested for jobs older than {max_age_hours} hours")
        return {"cleaned_count": 0, "error_count": 0}
    except Exception as e:
        logger.error(f"Error during job cleanup: {e}")
        return {"cleaned_count": 0, "error_count": 1}