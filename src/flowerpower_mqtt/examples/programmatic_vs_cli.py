"""
Comparison between programmatic and CLI approaches.

This example shows the same operations done both ways to highlight
when to use each approach.
"""

import asyncio
import subprocess
from pathlib import Path

from flowerpower_mqtt import MQTTPlugin, FlowerPowerMQTTConfig, MQTTConfig, JobQueueConfig, SubscriptionConfig


def compare_configuration_setup():
    """Compare configuration setup: programmatic vs CLI."""
    
    print("🔧 Configuration Setup Comparison")
    print("=" * 40)
    
    print("\n📝 Programmatic Approach:")
    print("```python")
    print("from flowerpower_mqtt import FlowerPowerMQTTConfig, MQTTConfig, JobQueueConfig")
    print()
    print("config = FlowerPowerMQTTConfig(")
    print("    mqtt=MQTTConfig(")
    print("        broker='mqtt.example.com',")
    print("        port=1883,")
    print("        keepalive=60")
    print("    ),")
    print("    job_queue=JobQueueConfig(")
    print("        enabled=True,")
    print("        redis_url='redis://localhost:6379'")
    print("    ),")
    print("    base_dir='/path/to/project',")
    print("    log_level='INFO'")
    print(")")
    print("config.to_yaml('config.yml')")
    print("```")
    
    print("\n💻 CLI Approach:")
    print("```bash")
    print("# Interactive setup")
    print("flowerpower-mqtt config create --interactive --job-queue")
    print()
    print("# Or one-liner")
    print("flowerpower-mqtt config create --output config.yml --job-queue")
    print("```")
    
    print("\n✅ When to use each:")
    print("• Programmatic: Complex logic, dynamic config, application embedding")
    print("• CLI: Quick setup, development, operations, interactive configuration")


def compare_connection_and_subscription():
    """Compare connection and subscription: programmatic vs CLI."""
    
    print("\n🔌 Connection & Subscription Comparison")
    print("=" * 45)
    
    print("\n📝 Programmatic Approach:")
    print("```python")
    print("import asyncio")
    print("from flowerpower_mqtt import MQTTPlugin")
    print()
    print("async def main():")
    print("    plugin = MQTTPlugin(")
    print("        broker='localhost',")
    print("        base_dir='.',")
    print("        use_job_queue=True")
    print("    )")
    print("    ")
    print("    await plugin.connect()")
    print("    await plugin.subscribe('sensors/+', 'sensor_processor', qos=1)")
    print("    await plugin.subscribe('alerts/#', 'alert_handler', qos=2)")
    print("    ")
    print("    # Complex logic here...")
    print("    ")
    print("    await plugin.start_listener()")
    print()
    print("asyncio.run(main())")
    print("```")
    
    print("\n💻 CLI Approach:")
    print("```bash")
    print("# Connect to broker")
    print("flowerpower-mqtt connect --broker localhost --job-queue")
    print()
    print("# Subscribe to topics")
    print("flowerpower-mqtt subscribe 'sensors/+' sensor_processor --qos 1")
    print("flowerpower-mqtt subscribe 'alerts/#' alert_handler --qos 2")
    print()
    print("# Start listening")
    print("flowerpower-mqtt listen")
    print("```")
    
    print("\n✅ When to use each:")
    print("• Programmatic: Complex application logic, conditional operations")
    print("• CLI: Quick testing, operations, simple use cases")


def compare_monitoring():
    """Compare monitoring approaches."""
    
    print("\n📊 Monitoring Comparison")
    print("=" * 25)
    
    print("\n📝 Programmatic Approach:")
    print("```python")
    print("# Get current statistics")
    print("stats = plugin.get_statistics()")
    print("subscriptions = plugin.get_subscriptions()")
    print()
    print("print(f'Messages: {stats[\"message_count\"]}')")
    print("print(f'Errors: {stats[\"error_count\"]}')")
    print()
    print("# Custom monitoring logic")
    print("for sub in subscriptions:")
    print("    if sub['message_count'] > 1000:")
    print("        print(f'High activity: {sub[\"topic\"]}')")
    print("```")
    
    print("\n💻 CLI Approach:")
    print("```bash")
    print("# One-time status check")
    print("flowerpower-mqtt status")
    print()
    print("# Real-time monitoring")
    print("flowerpower-mqtt monitor --interval 5")
    print()
    print("# JSON output for scripting")
    print("flowerpower-mqtt status --json | jq '.stats.message_count'")
    print()
    print("# List active subscriptions")
    print("flowerpower-mqtt list-subscriptions --active")
    print("```")
    
    print("\n✅ When to use each:")
    print("• Programmatic: Custom dashboards, application integration, alerts")
    print("• CLI: Quick checks, operations, real-time monitoring, scripting")


def compare_configuration_management():
    """Compare configuration management approaches."""
    
    print("\n⚙️  Configuration Management Comparison")
    print("=" * 40)
    
    print("\n📝 Programmatic Approach:")
    print("```python")
    print("# Load and modify configuration")
    print("config = FlowerPowerMQTTConfig.from_yaml('config.yml')")
    print()
    print("# Add subscription programmatically")
    print("new_sub = SubscriptionConfig(")
    print("    topic='dynamic/+/data',")
    print("    pipeline='dynamic_processor',")
    print("    qos=1,")
    print("    execution_mode='async'")
    print(")")
    print("config.subscriptions.append(new_sub)")
    print()
    print("# Save updated configuration")
    print("config.to_yaml('config.yml')")
    print()
    print("# Validation")
    print("try:")
    print("    config = FlowerPowerMQTTConfig.from_yaml('config.yml')")
    print("    print('Configuration is valid')")
    print("except Exception as e:")
    print("    print(f'Invalid configuration: {e}')")
    print("```")
    
    print("\n💻 CLI Approach:")
    print("```bash")
    print("# View current configuration")
    print("flowerpower-mqtt config show")
    print()
    print("# Edit configuration interactively")
    print("flowerpower-mqtt config edit")
    print()
    print("# Validate configuration")
    print("flowerpower-mqtt config validate config.yml")
    print()
    print("# Create new configuration")
    print("flowerpower-mqtt config create --interactive")
    print("```")
    
    print("\n✅ When to use each:")
    print("• Programmatic: Dynamic config generation, validation in code")
    print("• CLI: Manual configuration, development, validation, editing")


async def demonstrate_practical_example():
    """Show a practical example using both approaches."""
    
    print("\n🎯 Practical Example: IoT Sensor Monitoring")
    print("=" * 45)
    
    print("\n📋 Scenario: Monitor IoT sensors with different priorities")
    print("• Temperature sensors: QoS 1, async processing")
    print("• Pressure sensors: QoS 1, async processing")
    print("• Critical alerts: QoS 2, sync processing")
    print("• Debug logs: QoS 0, async processing")
    
    print("\n🔧 Setup Phase (CLI is better):")
    print("```bash")
    print("# Create configuration interactively")
    print("flowerpower-mqtt config create --interactive --job-queue")
    print()
    print("# Connect to IoT broker")
    print("flowerpower-mqtt connect --broker iot.company.com --port 8883")
    print()
    print("# Set up subscriptions")
    print("flowerpower-mqtt subscribe 'sensors/+/temperature' temp_processor --qos 1 --mode async")
    print("flowerpower-mqtt subscribe 'sensors/+/pressure' pressure_processor --qos 1 --mode async") 
    print("flowerpower-mqtt subscribe 'alerts/critical' alert_handler --qos 2 --mode sync")
    print("flowerpower-mqtt subscribe 'logs/debug/+' log_processor --qos 0 --mode async")
    print("```")
    
    print("\n🏃 Runtime Phase (Programmatic is better):")
    print("```python")
    print("import asyncio")
    print("from flowerpower_mqtt import MQTTPlugin")
    print()
    print("async def smart_monitoring():")
    print("    plugin = MQTTPlugin.from_config('iot_config.yml')")
    print("    await plugin.connect()")
    print("    ")
    print("    # Start monitoring in background")
    print("    await plugin.start_listener(background=True)")
    print("    ")
    print("    # Smart monitoring logic")
    print("    while True:")
    print("        stats = plugin.get_statistics()")
    print("        ")
    print("        # Check error rate")
    print("        error_rate = stats['error_count'] / max(stats['message_count'], 1)")
    print("        if error_rate > 0.1:")
    print("            print('High error rate detected!')")
    print("            # Could send alerts, adjust QoS, etc.")
    print("        ")
    print("        # Dynamic subscription management")
    print("        if stats['message_count'] > 10000:")
    print("            # Add more specific filters for high volume")
    print("            await plugin.subscribe(")
    print("                'sensors/critical-only/+',")
    print("                'critical_processor', ")
    print("                qos=2")
    print("            )")
    print("        ")
    print("        await asyncio.sleep(30)  # Check every 30 seconds")
    print("```")
    
    print("\n🔍 Monitoring Phase (CLI is better):")
    print("```bash")
    print("# Real-time monitoring")
    print("flowerpower-mqtt monitor --interval 10")
    print()
    print("# Check job queue status")
    print("flowerpower-mqtt jobs status")
    print()
    print("# List most active subscriptions")
    print("flowerpower-mqtt list-subscriptions --active")
    print("```")
    
    print("\n✅ Best Practice: Use both approaches")
    print("• CLI for setup, configuration, and monitoring")
    print("• Programmatic for application logic and automation")
    print("• Configuration files as the bridge between both")


def show_decision_matrix():
    """Show when to use programmatic vs CLI approach."""
    
    print("\n🤔 Decision Matrix: When to Use What")
    print("=" * 40)
    
    scenarios = [
        ("Initial setup", "CLI", "Interactive configuration is easier"),
        ("Development/Testing", "CLI", "Quick iterations and testing"),
        ("Production deployment", "Both", "CLI for config, code for logic"),
        ("Application integration", "Programmatic", "Need custom logic and error handling"),
        ("Operations/Monitoring", "CLI", "Better visualization and tools"),
        ("Configuration management", "CLI", "Validation and editing tools"),
        ("Dynamic subscriptions", "Programmatic", "Runtime decision making"),
        ("Batch operations", "CLI", "Simpler for bulk operations"),
        ("Custom dashboards", "Programmatic", "Need stats integration"),
        ("DevOps/Automation", "Both", "CLI in scripts, API in apps"),
        ("Learning/Exploration", "CLI", "Interactive and immediate feedback"),
        ("Complex error handling", "Programmatic", "Better control flow")
    ]
    
    print("\n| Scenario | Approach | Reason |")
    print("|----------|----------|--------|")
    
    for scenario, approach, reason in scenarios:
        print(f"| {scenario:<18} | {approach:<12} | {reason} |")
    
    print("\n💡 Pro Tips:")
    print("• Start with CLI for quick prototyping")
    print("• Move to programmatic for production applications")
    print("• Use configuration files to bridge both approaches")
    print("• CLI is great for debugging and operations")
    print("• Programmatic is better for complex business logic")


async def main():
    """Main comparison demo."""
    
    print("FlowerPower MQTT Plugin - Programmatic vs CLI Comparison")
    print("=" * 60)
    
    compare_configuration_setup()
    compare_connection_and_subscription()
    compare_monitoring()
    compare_configuration_management()
    await demonstrate_practical_example()
    show_decision_matrix()
    
    print("\n" + "=" * 60)
    print("🏆 Conclusion")
    print("=" * 60)
    print("Both approaches have their strengths:")
    print()
    print("🖥️  CLI Strengths:")
    print("• Quick setup and configuration")
    print("• Interactive development")
    print("• Beautiful output and monitoring")
    print("• Easy operations and troubleshooting")
    print("• Great for learning and experimentation")
    print()
    print("🐍 Programmatic Strengths:")
    print("• Complex business logic")
    print("• Error handling and resilience")
    print("• Application integration")
    print("• Dynamic behavior")
    print("• Custom monitoring and alerting")
    print()
    print("🤝 Best Practice: Use Both!")
    print("Use CLI for development and operations,")
    print("programmatic API for application logic.")
    print("Configuration files bridge both approaches.")


if __name__ == "__main__":
    asyncio.run(main())