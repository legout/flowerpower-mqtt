"""
CLI integration example for FlowerPower MQTT Plugin.

This example shows how to use the CLI in combination with 
programmatic access for hybrid usage patterns.
"""

import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

from flowerpower_mqtt import MQTTPlugin, FlowerPowerMQTTConfig, MQTTConfig, JobQueueConfig


def run_cli_command(command: str) -> tuple[int, str]:
    """Run a CLI command and return exit code and output."""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)


async def demonstrate_cli_integration():
    """Demonstrate CLI and programmatic integration."""
    
    print("🚀 FlowerPower MQTT CLI Integration Example")
    print("=" * 50)
    
    # 1. Create configuration using CLI
    print("\n1. Creating configuration with CLI...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        config_file = Path(f.name)
    
    # Use CLI to create configuration
    exit_code, output = run_cli_command(
        f"flowerpower-mqtt config create --output {config_file} --job-queue"
    )
    
    if exit_code == 0:
        print(f"   ✅ Configuration created: {config_file}")
    else:
        print(f"   ❌ Configuration creation failed: {output}")
        print("   📝 Note: CLI might not be installed. Using programmatic approach...")
        
        # Fallback: create config programmatically
        config = FlowerPowerMQTTConfig(
            mqtt=MQTTConfig(broker="localhost", port=1883),
            job_queue=JobQueueConfig(enabled=True),
            base_dir="."
        )
        config.to_yaml(config_file)
        print(f"   ✅ Configuration created programmatically: {config_file}")
    
    # 2. Validate configuration using CLI
    print("\n2. Validating configuration with CLI...")
    
    exit_code, output = run_cli_command(f"flowerpower-mqtt config validate {config_file}")
    
    if exit_code == 0:
        print("   ✅ Configuration is valid")
    else:
        print(f"   ❌ Configuration validation failed: {output}")
    
    # 3. Show configuration using CLI
    print("\n3. Showing configuration with CLI...")
    
    exit_code, output = run_cli_command(f"flowerpower-mqtt config show --config {config_file}")
    
    if exit_code == 0:
        print("   ✅ Configuration displayed")
        # Print first few lines of output
        lines = output.split('\n')[:10]
        for line in lines:
            if line.strip():
                print(f"      {line}")
        if len(output.split('\n')) > 10:
            print("      ...")
    else:
        print(f"   ❌ Failed to show configuration: {output}")
    
    # 4. Load plugin using configuration created by CLI
    print("\n4. Loading plugin with CLI-generated configuration...")
    
    try:
        plugin = MQTTPlugin.from_config(config_file)
        print("   ✅ Plugin loaded from CLI-generated config")
        
        # Show plugin info
        stats = plugin.get_statistics()
        print(f"      Broker: {stats['broker']}")
        print(f"      Job Queue: {'Enabled' if stats['job_queue_enabled'] else 'Disabled'}")
        
    except Exception as e:
        print(f"   ❌ Failed to load plugin: {e}")
    
    # 5. Add subscription programmatically and save via CLI approach
    print("\n5. Hybrid approach: Program + CLI...")
    
    try:
        # Connect programmatically
        print("   📡 Connecting to broker...")
        await plugin.connect()
        print("   ✅ Connected")
        
        # Add subscription programmatically
        await plugin.subscribe("sensors/+/data", "sensor_processor", qos=1, execution_mode="async")
        print("   ✅ Subscription added programmatically")
        
        # Save configuration (this could be done via CLI too)
        plugin.save_config(config_file)
        print("   ✅ Configuration updated")
        
        # Show updated subscriptions using CLI
        print("\n   📋 Updated subscriptions (via CLI):")
        exit_code, output = run_cli_command("flowerpower-mqtt list-subscriptions --json")
        
        if exit_code == 0:
            print("   ✅ Subscriptions listed via CLI")
        else:
            # Fallback to programmatic approach
            subscriptions = plugin.get_subscriptions()
            print(f"   📝 {len(subscriptions)} subscriptions (programmatic fallback)")
            for sub in subscriptions:
                print(f"      - {sub.get('topic')} -> {sub.get('pipeline')} (QoS {sub.get('qos')})")
        
    except Exception as e:
        print(f"   ❌ Hybrid operation failed: {e}")
    
    # 6. Demonstrate CLI status checking
    print("\n6. Status checking with CLI...")
    
    exit_code, output = run_cli_command("flowerpower-mqtt status --json")
    
    if exit_code == 0:
        print("   ✅ Status retrieved via CLI")
        # Parse and show key stats
        try:
            import json
            status_data = json.loads(output)
            print(f"      Connected: {status_data.get('status', {}).get('connected', False)}")
            print(f"      Subscriptions: {status_data.get('status', {}).get('subscriptions_count', 0)}")
        except:
            print("      (Status data format changed)")
    else:
        print(f"   ❌ Status check failed: {output}")
        # Programmatic fallback
        try:
            stats = plugin.get_statistics()
            print("   📝 Status via programmatic API:")
            print(f"      Connected: {stats.get('connected', False)}")
            print(f"      Subscriptions: {stats.get('subscriptions_count', 0)}")
        except Exception as e:
            print(f"      Status check failed: {e}")
    
    # Cleanup
    if plugin and plugin.is_connected:
        await plugin.disconnect()
        print("\n🔌 Disconnected")
    
    # Remove temporary config file
    try:
        config_file.unlink()
        print(f"🧹 Cleaned up: {config_file}")
    except:
        pass
    
    print("\n✨ CLI Integration Demo Complete!")
    print("\nKey Benefits Demonstrated:")
    print("• CLI for quick configuration creation and validation")
    print("• CLI for monitoring and status checking")
    print("• Seamless integration between CLI and programmatic API")
    print("• Configuration files as bridge between approaches")
    print("• Fallback mechanisms for robustness")


def demonstrate_cli_workflow():
    """Show typical CLI workflow."""
    
    print("\n" + "=" * 50)
    print("🛠️  Typical CLI Workflow Example")
    print("=" * 50)
    
    cli_commands = [
        # Basic workflow
        ("Create config", "flowerpower-mqtt config create --interactive"),
        ("Validate config", "flowerpower-mqtt config validate mqtt_config.yml"),
        ("Connect to broker", "flowerpower-mqtt connect --config mqtt_config.yml"),
        ("Subscribe to topic", "flowerpower-mqtt subscribe 'sensors/+' sensor_pipeline --qos 1"),
        ("Start listening", "flowerpower-mqtt listen --background"),
        ("Monitor status", "flowerpower-mqtt monitor --interval 5"),
        ("Check subscriptions", "flowerpower-mqtt list-subscriptions"),
        ("Stop and disconnect", "flowerpower-mqtt disconnect"),
        
        # Advanced workflow with job queue
        ("Enable job queue", "flowerpower-mqtt config create --job-queue"),
        ("Start RQ worker", "flowerpower-mqtt jobs worker start --count 2"),
        ("Check job status", "flowerpower-mqtt jobs status"),
        ("Async subscription", "flowerpower-mqtt subscribe 'events/+' event_processor --mode async"),
    ]
    
    print("\n📝 Command Reference:")
    for i, (description, command) in enumerate(cli_commands, 1):
        print(f"{i:2d}. {description}")
        print(f"    {command}")
        print()
    
    print("🔄 Typical Development Workflow:")
    print("1. Create configuration interactively")
    print("2. Validate and test configuration")
    print("3. Connect to broker and subscribe to topics")
    print("4. Start listening and monitor in real-time")
    print("5. Use programmatic API for complex logic")
    print("6. Save and version control configuration files")


async def main():
    """Main demo function."""
    
    print("FlowerPower MQTT Plugin - CLI Integration Examples")
    print("This example demonstrates hybrid CLI + programmatic usage")
    
    # Check if CLI is available
    exit_code, output = run_cli_command("flowerpower-mqtt --help")
    
    if exit_code == 0:
        print("✅ CLI is available and working")
    else:
        print("⚠️  CLI not available (maybe not installed?)")
        print("   Install with: pip install -e .")
        print("   Continuing with limited demo...")
    
    # Run demonstrations
    await demonstrate_cli_integration()
    demonstrate_cli_workflow()
    
    print("\n" + "=" * 60)
    print("🎯 Summary")
    print("=" * 60)
    print("The FlowerPower MQTT CLI provides:")
    print("• Easy configuration management")
    print("• Interactive setup and validation") 
    print("• Real-time monitoring and status")
    print("• Job queue management")
    print("• Beautiful, rich output with tables and colors")
    print("• Seamless integration with programmatic API")
    print("• Shell completion support")
    print("\nUse CLI for development and operations,")
    print("programmatic API for complex application logic!")


if __name__ == "__main__":
    asyncio.run(main())