"""
Example FlowerPower pipeline for processing MQTT messages.

This is a sample pipeline that demonstrates how to process MQTT messages
received by the FlowerPower MQTT plugin. Place this file in your
FlowerPower project's pipelines/ directory.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any
from hamilton.function_modifiers import parameterize
from pathlib import Path


def mqtt_message_data(mqtt_message: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and validate MQTT message data."""
    return mqtt_message


def mqtt_metadata(mqtt_topic: str, mqtt_qos: int, execution_timestamp: str) -> Dict[str, str]:
    """Create metadata from MQTT message context."""
    return {
        "topic": mqtt_topic,
        "qos": str(mqtt_qos),
        "timestamp": execution_timestamp,
        "processing_time": datetime.now().isoformat()
    }


def sensor_data(mqtt_message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract sensor data from MQTT message."""
    # Handle different message formats
    if "sensor_data" in mqtt_message_data:
        return mqtt_message_data["sensor_data"]
    elif "data" in mqtt_message_data:
        return mqtt_message_data["data"]
    else:
        # Fallback: treat entire payload as sensor data
        return mqtt_message_data


def temperature_reading(sensor_data: Dict[str, Any]) -> float:
    """Extract temperature reading."""
    temp = sensor_data.get("temperature", 0.0)
    return float(temp) if temp is not None else 0.0


def humidity_reading(sensor_data: Dict[str, Any]) -> float:
    """Extract humidity reading."""
    humidity = sensor_data.get("humidity", 0.0)
    return float(humidity) if humidity is not None else 0.0


def temperature_status(temperature_reading: float) -> str:
    """Classify temperature reading."""
    if temperature_reading < 0:
        return "freezing"
    elif temperature_reading < 10:
        return "cold" 
    elif temperature_reading < 25:
        return "normal"
    elif temperature_reading < 35:
        return "warm"
    else:
        return "hot"


def humidity_status(humidity_reading: float) -> str:
    """Classify humidity reading."""
    if humidity_reading < 30:
        return "dry"
    elif humidity_reading < 60:
        return "normal"
    else:
        return "humid"


def alert_conditions(temperature_status: str, humidity_status: str) -> Dict[str, bool]:
    """Check for alert conditions."""
    return {
        "temperature_alert": temperature_status in ["freezing", "hot"],
        "humidity_alert": humidity_status in ["dry", "humid"],
        "combined_alert": (
            temperature_status in ["freezing", "hot"] and 
            humidity_status in ["dry", "humid"]
        )
    }


def processed_data(
    mqtt_metadata: Dict[str, str],
    temperature_reading: float,
    humidity_reading: float, 
    temperature_status: str,
    humidity_status: str,
    alert_conditions: Dict[str, bool]
) -> Dict[str, Any]:
    """Combine all processed data."""
    return {
        "metadata": mqtt_metadata,
        "readings": {
            "temperature": temperature_reading,
            "humidity": humidity_reading
        },
        "status": {
            "temperature": temperature_status,
            "humidity": humidity_status
        },
        "alerts": alert_conditions,
        "processed_at": datetime.now().isoformat()
    }


def save_to_log(processed_data: Dict[str, Any]) -> str:
    """Save processed data to log file."""
    log_file = Path("mqtt_processing.log")
    
    # Create log entry
    log_entry = (
        f"{processed_data['processed_at']} - "
        f"Topic: {processed_data['metadata']['topic']} - "
        f"Temp: {processed_data['readings']['temperature']:.1f}°C "
        f"({processed_data['status']['temperature']}) - "
        f"Humidity: {processed_data['readings']['humidity']:.1f}% "
        f"({processed_data['status']['humidity']}) - "
        f"Alerts: {processed_data['alerts']}\n"
    )
    
    # Append to log file
    with open(log_file, "a") as f:
        f.write(log_entry)
    
    return f"Logged to {log_file}"


def generate_response(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate response data (final pipeline output)."""
    return {
        "success": True,
        "message": f"Processed MQTT message from {processed_data['metadata']['topic']}",
        "data": processed_data,
        "summary": {
            "temperature": f"{processed_data['readings']['temperature']:.1f}°C ({processed_data['status']['temperature']})",
            "humidity": f"{processed_data['readings']['humidity']:.1f}% ({processed_data['status']['humidity']})",
            "has_alerts": any(processed_data['alerts'].values())
        }
    }


# Example usage in a pipeline configuration:
# 
# conf/pipelines/sensor_processor.yml:
# ---
# run:
#   final_vars:
#     - generate_response
#   inputs: {}  # MQTT plugin provides inputs automatically
# 
# params: {}  # No additional parameters needed
# 
# schedule: {}  # No schedule needed (triggered by MQTT)