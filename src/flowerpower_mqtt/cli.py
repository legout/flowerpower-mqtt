"""
Command Line Interface for FlowerPower MQTT Plugin.

Provides a comprehensive CLI for managing MQTT connections, subscriptions,
and pipeline execution with beautiful rich output.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.syntax import Syntax

from . import MQTTPlugin
from .config import FlowerPowerMQTTConfig, MQTTConfig, JobQueueConfig, SubscriptionConfig
from .exceptions import FlowerPowerMQTTError

# Initialize Typer app and Rich console
app = typer.Typer(
    name="flowerpower-mqtt",
    help="FlowerPower MQTT Plugin CLI - Trigger pipeline execution via MQTT messages",
    add_completion=True,
    rich_markup_mode="rich"
)
console = Console()

# Global state for CLI
_current_plugin: Optional[MQTTPlugin] = None
_config_file: Optional[Path] = None


def get_config_path() -> Path:
    """Get configuration file path."""
    global _config_file
    if _config_file and _config_file.exists():
        return _config_file
    
    # Check common locations
    candidates = [
        Path("mqtt_config.yml"),
        Path("config.yml"),
        Path(".flowerpower-mqtt.yml"),
        Path.home() / ".config" / "flowerpower-mqtt.yml"
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    # Return default
    return Path("mqtt_config.yml")


def load_plugin(
    config: Optional[Path] = None,
    broker: Optional[str] = None,
    port: Optional[int] = None,
    base_dir: Optional[str] = None,
    use_job_queue: bool = False,
    redis_url: Optional[str] = None
) -> MQTTPlugin:
    """Load MQTTPlugin from config or parameters."""
    global _current_plugin, _config_file
    
    if config and config.exists():
        _config_file = config
        _current_plugin = MQTTPlugin.from_config(config)
        return _current_plugin
    
    # Create from parameters
    kwargs = {}
    if broker:
        kwargs["broker"] = broker
    if port:
        kwargs["port"] = port
    if base_dir:
        kwargs["base_dir"] = base_dir
    if use_job_queue:
        kwargs["use_job_queue"] = use_job_queue
    if redis_url:
        kwargs["redis_url"] = redis_url
    
    _current_plugin = MQTTPlugin(**kwargs)
    return _current_plugin


def handle_async(coro):
    """Handle async functions in CLI commands."""
    try:
        return asyncio.run(coro)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def connect(
    broker: str = typer.Option("localhost", "--broker", "-b", help="MQTT broker hostname"),
    port: int = typer.Option(1883, "--port", "-p", help="MQTT broker port"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    base_dir: str = typer.Option(".", "--base-dir", help="FlowerPower project directory"),
    use_job_queue: bool = typer.Option(False, "--job-queue", help="Enable RQ job queue"),
    redis_url: str = typer.Option("redis://localhost:6379", "--redis-url", help="Redis URL for job queue"),
    save_config: bool = typer.Option(False, "--save-config", help="Save configuration to file")
):
    """Connect to MQTT broker."""
    
    async def _connect():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Connecting to {broker}:{port}...", total=None)
            
            try:
                plugin = load_plugin(
                    config=config,
                    broker=broker,
                    port=port,
                    base_dir=base_dir,
                    use_job_queue=use_job_queue,
                    redis_url=redis_url
                )
                
                await plugin.connect()
                
                progress.update(task, description=f"✅ Connected to {broker}:{port}")
                
                # Show connection info
                console.print()
                info_table = Table(title="Connection Information")
                info_table.add_column("Property", style="bold blue")
                info_table.add_column("Value", style="green")
                
                info_table.add_row("Broker", f"{broker}:{port}")
                info_table.add_row("Base Directory", base_dir)
                info_table.add_row("Job Queue", "Enabled" if use_job_queue else "Disabled")
                if use_job_queue:
                    info_table.add_row("Redis URL", redis_url)
                
                console.print(info_table)
                
                # Save config if requested
                if save_config:
                    config_path = get_config_path()
                    plugin.save_config(config_path)
                    console.print(f"\n[green]Configuration saved to {config_path}[/green]")
                
            except Exception as e:
                progress.update(task, description=f"❌ Connection failed: {e}")
                raise
    
    handle_async(_connect())


@app.command()
def subscribe(
    topic: str = typer.Argument(..., help="MQTT topic to subscribe to"),
    pipeline: str = typer.Argument(..., help="FlowerPower pipeline name"),
    qos: int = typer.Option(0, "--qos", "-q", help="QoS level (0, 1, or 2)"),
    execution_mode: str = typer.Option("sync", "--mode", "-m", help="Execution mode (sync, async, mixed)"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    save_config: bool = typer.Option(False, "--save-config", help="Save subscription to config file")
):
    """Subscribe to MQTT topic."""
    
    # Validate inputs
    if qos not in [0, 1, 2]:
        console.print("[red]QoS must be 0, 1, or 2[/red]")
        raise typer.Exit(1)
    
    if execution_mode not in ["sync", "async", "mixed"]:
        console.print("[red]Execution mode must be sync, async, or mixed[/red]")
        raise typer.Exit(1)
    
    async def _subscribe():
        try:
            # Load or use existing plugin
            plugin = _current_plugin or load_plugin(config=config)
            
            if not plugin.is_connected:
                console.print("[yellow]Plugin not connected. Connecting first...[/yellow]")
                await plugin.connect()
            
            await plugin.subscribe(topic, pipeline, qos, execution_mode)
            
            # Show subscription info
            console.print(f"\n[green]✅ Subscribed to '{topic}' -> '{pipeline}'[/green]")
            
            sub_table = Table(title="Subscription Details")
            sub_table.add_column("Property", style="bold blue")
            sub_table.add_column("Value", style="green")
            
            sub_table.add_row("Topic", topic)
            sub_table.add_row("Pipeline", pipeline)
            sub_table.add_row("QoS Level", str(qos))
            sub_table.add_row("Execution Mode", execution_mode)
            
            console.print(sub_table)
            
            # Save config if requested
            if save_config:
                config_path = get_config_path()
                plugin.save_config(config_path)
                console.print(f"\n[green]Subscription saved to {config_path}[/green]")
                
        except Exception as e:
            console.print(f"[red]Subscription failed: {e}[/red]")
            raise typer.Exit(1)
    
    handle_async(_subscribe())


@app.command()
def listen(
    background: bool = typer.Option(False, "--background", "-bg", help="Run listener in background"),
    execution_mode: Optional[str] = typer.Option(None, "--override-mode", help="Override execution mode for all pipelines"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    timeout: Optional[int] = typer.Option(None, "--timeout", help="Stop after specified seconds")
):
    """Start listening for MQTT messages."""
    
    async def _listen():
        try:
            # Load or use existing plugin
            plugin = _current_plugin or load_plugin(config=config)
            
            if not plugin.is_connected:
                console.print("[yellow]Plugin not connected. Connecting first...[/yellow]")
                await plugin.connect()
            
            subscriptions = plugin.get_subscriptions()
            if not subscriptions:
                console.print("[yellow]No subscriptions configured. Use 'subscribe' command first.[/yellow]")
                return
            
            # Show listener info
            console.print(Panel(
                f"[bold green]Starting MQTT Listener[/bold green]\n\n"
                f"Subscriptions: {len(subscriptions)}\n"
                f"Background mode: {'Yes' if background else 'No'}\n"
                f"Execution override: {execution_mode or 'None'}\n"
                f"Timeout: {timeout or 'None'}",
                title="Listener Configuration"
            ))
            
            # Show subscriptions table
            sub_table = Table(title="Active Subscriptions")
            sub_table.add_column("Topic", style="bold blue")
            sub_table.add_column("Pipeline", style="green")
            sub_table.add_column("QoS", style="yellow")
            sub_table.add_column("Mode", style="magenta")
            
            for sub in subscriptions:
                sub_table.add_row(
                    sub.get("topic", ""),
                    sub.get("pipeline", ""),
                    str(sub.get("qos", 0)),
                    sub.get("execution_mode", "sync")
                )
            
            console.print(sub_table)
            console.print("\n[bold yellow]Press Ctrl+C to stop listener[/bold yellow]\n")
            
            # Start listener
            if timeout:
                # Run with timeout
                try:
                    await asyncio.wait_for(
                        plugin.start_listener(background=background, execution_mode=execution_mode),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    console.print(f"\n[yellow]Listener stopped after {timeout} seconds[/yellow]")
            else:
                # Run indefinitely
                await plugin.start_listener(background=background, execution_mode=execution_mode)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopping listener...[/yellow]")
            if plugin:
                await plugin.stop_listener()
                console.print("[green]Listener stopped gracefully[/green]")
        except Exception as e:
            console.print(f"[red]Listener error: {e}[/red]")
            raise typer.Exit(1)
    
    handle_async(_listen())


@app.command()
def status(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """Show current plugin status and statistics."""
    
    async def _status():
        try:
            # Load or use existing plugin
            plugin = _current_plugin or load_plugin(config=config)
            
            # Get statistics
            stats = plugin.get_statistics()
            subscriptions = plugin.get_subscriptions()
            
            if json_output:
                # JSON output
                output = {
                    "status": stats,
                    "subscriptions": subscriptions
                }
                console.print(json.dumps(output, indent=2, default=str))
                return
            
            # Rich formatted output
            status_table = Table(title="Plugin Status")
            status_table.add_column("Property", style="bold blue")
            status_table.add_column("Value", style="green")
            
            status_table.add_row("Connected", "✅ Yes" if stats.get("connected", False) else "❌ No")
            status_table.add_row("Broker", stats.get("broker", "N/A"))
            status_table.add_row("Listening", "✅ Yes" if stats.get("running", False) else "❌ No")
            status_table.add_row("Runtime", f"{stats.get('runtime_seconds', 0):.1f}s")
            status_table.add_row("Messages", str(stats.get("message_count", 0)))
            status_table.add_row("Pipelines Executed", str(stats.get("pipeline_count", 0)))
            status_table.add_row("Errors", str(stats.get("error_count", 0)))
            status_table.add_row("Subscriptions", str(len(subscriptions)))
            status_table.add_row("Job Queue", "✅ Enabled" if stats.get("job_queue_enabled", False) else "❌ Disabled")
            
            console.print(status_table)
            
            if subscriptions:
                console.print("\n")
                sub_table = Table(title="Subscription Details")
                sub_table.add_column("Topic", style="bold blue")
                sub_table.add_column("Pipeline", style="green")
                sub_table.add_column("QoS", style="yellow")
                sub_table.add_column("Mode", style="magenta")
                sub_table.add_column("Messages", style="cyan")
                
                for sub in subscriptions:
                    sub_table.add_row(
                        sub.get("topic", ""),
                        sub.get("pipeline", ""),
                        str(sub.get("qos", 0)),
                        sub.get("execution_mode", "sync"),
                        str(sub.get("message_count", 0))
                    )
                
                console.print(sub_table)
            
        except Exception as e:
            console.print(f"[red]Status check failed: {e}[/red]")
            raise typer.Exit(1)
    
    handle_async(_status())


@app.command()
def disconnect(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file")
):
    """Disconnect from MQTT broker."""
    
    async def _disconnect():
        try:
            plugin = _current_plugin or load_plugin(config=config)
            
            if not plugin.is_connected:
                console.print("[yellow]Plugin not connected[/yellow]")
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Disconnecting...", total=None)
                
                await plugin.disconnect()
                
                progress.update(task, description="✅ Disconnected successfully")
            
            console.print("[green]Disconnected from MQTT broker[/green]")
            
        except Exception as e:
            console.print(f"[red]Disconnect failed: {e}[/red]")
            raise typer.Exit(1)
    
    handle_async(_disconnect())


# Configuration management commands
config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")


@config_app.command("create")
def config_create(
    output: Path = typer.Option("mqtt_config.yml", "--output", "-o", help="Output configuration file"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive configuration"),
    with_job_queue: bool = typer.Option(False, "--job-queue", help="Enable job queue configuration")
):
    """Create a new configuration file."""
    
    try:
        if output.exists() and not Confirm.ask(f"Configuration file {output} exists. Overwrite?"):
            console.print("[yellow]Configuration creation cancelled[/yellow]")
            return
        
        config = FlowerPowerMQTTConfig()
        
        if interactive:
            console.print(Panel("[bold blue]Interactive Configuration Setup[/bold blue]"))
            
            # MQTT Configuration
            console.print("\n[bold]MQTT Broker Configuration[/bold]")
            config.mqtt.broker = Prompt.ask("MQTT Broker hostname", default=config.mqtt.broker)
            config.mqtt.port = int(Prompt.ask("MQTT Broker port", default=str(config.mqtt.port)))
            config.mqtt.keepalive = int(Prompt.ask("Keep alive seconds", default=str(config.mqtt.keepalive)))
            config.mqtt.client_id = Prompt.ask("Client ID (optional)", default=config.mqtt.client_id or "")
            
            # Base directory
            config.base_dir = Prompt.ask("FlowerPower base directory", default=config.base_dir)
            
            # Job Queue
            if with_job_queue or Confirm.ask("Enable job queue for async processing?"):
                config.job_queue.enabled = True
                config.job_queue.redis_url = Prompt.ask("Redis URL", default=config.job_queue.redis_url)
                config.job_queue.queue_name = Prompt.ask("Queue name", default=config.job_queue.queue_name)
                config.job_queue.worker_count = int(Prompt.ask("Worker count", default=str(config.job_queue.worker_count)))
            
            # Log level
            log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            console.print(f"Log levels: {', '.join(log_levels)}")
            config.log_level = Prompt.ask("Log level", default=config.log_level, choices=log_levels)
            
        elif with_job_queue:
            config.job_queue.enabled = True
        
        # Save configuration
        config.to_yaml(output)
        
        console.print(f"\n[green]✅ Configuration created: {output}[/green]")
        
        # Show configuration preview
        with open(output) as f:
            config_content = f.read()
        
        syntax = Syntax(config_content, "yaml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Configuration Preview"))
        
    except Exception as e:
        console.print(f"[red]Configuration creation failed: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("validate")
def config_validate(
    config_file: Path = typer.Argument(..., help="Configuration file to validate")
):
    """Validate configuration file."""
    
    try:
        if not config_file.exists():
            console.print(f"[red]Configuration file not found: {config_file}[/red]")
            raise typer.Exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Validating configuration...", total=None)
            
            # Load and validate configuration
            config = FlowerPowerMQTTConfig.from_yaml(config_file)
            
            progress.update(task, description="✅ Configuration is valid")
        
        console.print(f"[green]✅ Configuration file {config_file} is valid[/green]")
        
        # Show summary
        summary_table = Table(title="Configuration Summary")
        summary_table.add_column("Section", style="bold blue")
        summary_table.add_column("Details", style="green")
        
        summary_table.add_row("MQTT Broker", f"{config.mqtt.broker}:{config.mqtt.port}")
        summary_table.add_row("Base Directory", config.base_dir)
        summary_table.add_row("Job Queue", "Enabled" if config.job_queue.enabled else "Disabled")
        summary_table.add_row("Subscriptions", str(len(config.subscriptions)))
        summary_table.add_row("Log Level", config.log_level)
        
        console.print(summary_table)
        
        if config.subscriptions:
            console.print("\n")
            sub_table = Table(title="Configured Subscriptions")
            sub_table.add_column("Topic", style="bold blue")
            sub_table.add_column("Pipeline", style="green")
            sub_table.add_column("QoS", style="yellow")
            sub_table.add_column("Mode", style="magenta")
            
            for sub in config.subscriptions:
                sub_table.add_row(sub.topic, sub.pipeline, str(sub.qos), sub.execution_mode)
            
            console.print(sub_table)
        
    except Exception as e:
        console.print(f"[red]Configuration validation failed: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("show")
def config_show(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    format_output: str = typer.Option("yaml", "--format", help="Output format (yaml, json)")
):
    """Show current configuration."""
    
    try:
        config_path = config_file or get_config_path()
        
        if not config_path.exists():
            console.print(f"[yellow]Configuration file not found: {config_path}[/yellow]")
            console.print("Use 'flowerpower-mqtt config create' to create a new configuration.")
            return
        
        config = FlowerPowerMQTTConfig.from_yaml(config_path)
        
        if format_output == "json":
            config_dict = config.to_dict()
            console.print(json.dumps(config_dict, indent=2, default=str))
        else:
            # Show YAML content with syntax highlighting
            with open(config_path) as f:
                content = f.read()
            
            syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Configuration: {config_path}"))
        
    except Exception as e:
        console.print(f"[red]Failed to show configuration: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("edit")
def config_edit(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    editor: Optional[str] = typer.Option(None, "--editor", help="Editor to use (default: $EDITOR)")
):
    """Edit configuration file."""
    
    import os
    import subprocess
    
    try:
        config_path = config_file or get_config_path()
        
        if not config_path.exists():
            if Confirm.ask(f"Configuration file {config_path} does not exist. Create it?"):
                # Create basic config
                config = FlowerPowerMQTTConfig()
                config.to_yaml(config_path)
                console.print(f"[green]Created {config_path}[/green]")
            else:
                return
        
        # Determine editor
        editor_cmd = editor or os.environ.get("EDITOR", "nano")
        
        console.print(f"[blue]Opening {config_path} with {editor_cmd}...[/blue]")
        
        # Open editor
        result = subprocess.run([editor_cmd, str(config_path)])
        
        if result.returncode == 0:
            console.print(f"[green]Configuration file {config_path} updated[/green]")
            
            # Validate after editing
            try:
                FlowerPowerMQTTConfig.from_yaml(config_path)
                console.print("[green]✅ Configuration is valid[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Configuration validation warning: {e}[/yellow]")
        else:
            console.print(f"[yellow]Editor exited with code {result.returncode}[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Failed to edit configuration: {e}[/red]")
        raise typer.Exit(1)


# Monitoring commands
@app.command()
def monitor(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    interval: int = typer.Option(5, "--interval", "-i", help="Update interval in seconds"),
    duration: Optional[int] = typer.Option(None, "--duration", "-d", help="Monitor duration in seconds"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """Monitor MQTT plugin in real-time."""
    
    async def _monitor():
        try:
            plugin = _current_plugin or load_plugin(config=config)
            
            if not plugin.is_connected:
                console.print("[yellow]Plugin not connected. Connect first with 'flowerpower-mqtt connect'[/yellow]")
                return
            
            console.print(Panel(
                f"[bold green]Real-time Monitoring[/bold green]\n\n"
                f"Update interval: {interval}s\n"
                f"Duration: {'Unlimited' if not duration else f'{duration}s'}\n"
                f"Press Ctrl+C to stop",
                title="Monitor Configuration"
            ))
            
            start_time = asyncio.get_event_loop().time()
            iteration = 0
            
            try:
                while True:
                    # Check duration limit
                    if duration and (asyncio.get_event_loop().time() - start_time) >= duration:
                        console.print(f"\n[yellow]Monitoring stopped after {duration} seconds[/yellow]")
                        break
                    
                    iteration += 1
                    stats = plugin.get_statistics()
                    subscriptions = plugin.get_subscriptions()
                    
                    if json_output:
                        output = {
                            "timestamp": asyncio.get_event_loop().time(),
                            "iteration": iteration,
                            "stats": stats,
                            "subscriptions": subscriptions
                        }
                        console.print(json.dumps(output, indent=2, default=str))
                    else:
                        # Clear screen and show updated stats
                        console.clear()
                        console.print(f"[bold blue]Monitor #{iteration}[/bold blue] - {asyncio.get_event_loop().time():.1f}")
                        
                        # Stats table
                        stats_table = Table(title="Real-time Statistics")
                        stats_table.add_column("Metric", style="bold blue")
                        stats_table.add_column("Value", style="green")
                        
                        stats_table.add_row("Connected", "✅ Yes" if stats.get("connected", False) else "❌ No")
                        stats_table.add_row("Listening", "✅ Yes" if stats.get("running", False) else "❌ No")
                        stats_table.add_row("Runtime", f"{stats.get('runtime_seconds', 0):.1f}s")
                        stats_table.add_row("Messages", str(stats.get("message_count", 0)))
                        stats_table.add_row("Pipeline Executions", str(stats.get("pipeline_count", 0)))
                        stats_table.add_row("Errors", str(stats.get("error_count", 0)))
                        
                        console.print(stats_table)
                        
                        # Subscription activity
                        if subscriptions:
                            active_subs = [s for s in subscriptions if s.get('message_count', 0) > 0]
                            if active_subs:
                                console.print("\n")
                                activity_table = Table(title="Active Subscriptions")
                                activity_table.add_column("Topic", style="bold blue")
                                activity_table.add_column("Messages", style="yellow")
                                activity_table.add_column("Pipeline", style="green")
                                
                                for sub in active_subs:
                                    activity_table.add_row(
                                        sub.get("topic", ""),
                                        str(sub.get("message_count", 0)),
                                        sub.get("pipeline", "")
                                    )
                                
                                console.print(activity_table)
                        
                        console.print(f"\n[dim]Press Ctrl+C to stop monitoring...[/dim]")
                    
                    await asyncio.sleep(interval)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Monitoring failed: {e}[/red]")
            raise typer.Exit(1)
    
    handle_async(_monitor())


@app.command()
def list_subscriptions(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    active_only: bool = typer.Option(False, "--active", help="Show only subscriptions with messages"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """List all MQTT subscriptions."""
    
    async def _list_subscriptions():
        try:
            plugin = _current_plugin or load_plugin(config=config)
            subscriptions = plugin.get_subscriptions()
            
            if not subscriptions:
                console.print("[yellow]No subscriptions found[/yellow]")
                return
            
            if active_only:
                subscriptions = [s for s in subscriptions if s.get('message_count', 0) > 0]
                if not subscriptions:
                    console.print("[yellow]No active subscriptions found[/yellow]")
                    return
            
            if json_output:
                console.print(json.dumps(subscriptions, indent=2, default=str))
                return
            
            # Rich formatted table
            sub_table = Table(title=f"MQTT Subscriptions ({'Active Only' if active_only else 'All'})")
            sub_table.add_column("Topic", style="bold blue")
            sub_table.add_column("Pipeline", style="green")
            sub_table.add_column("QoS", style="yellow")
            sub_table.add_column("Mode", style="magenta")
            sub_table.add_column("Messages", style="cyan")
            sub_table.add_column("Errors", style="red")
            
            for sub in subscriptions:
                sub_table.add_row(
                    sub.get("topic", ""),
                    sub.get("pipeline", ""),
                    str(sub.get("qos", 0)),
                    sub.get("execution_mode", "sync"),
                    str(sub.get("message_count", 0)),
                    str(sub.get("error_count", 0))
                )
            
            console.print(sub_table)
            console.print(f"\n[dim]Total subscriptions: {len(subscriptions)}[/dim]")
            
        except Exception as e:
            console.print(f"[red]Failed to list subscriptions: {e}[/red]")
            raise typer.Exit(1)
    
    handle_async(_list_subscriptions())


@app.command() 
def unsubscribe(
    topic: str = typer.Argument(..., help="Topic to unsubscribe from"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    save_config: bool = typer.Option(False, "--save-config", help="Save changes to config file")
):
    """Unsubscribe from MQTT topic."""
    
    async def _unsubscribe():
        try:
            plugin = _current_plugin or load_plugin(config=config)
            
            if not plugin.is_connected:
                console.print("[yellow]Plugin not connected. Connect first.[/yellow]")
                return
            
            # Check if topic exists
            subscriptions = plugin.get_subscriptions()
            topic_exists = any(sub.get("topic") == topic for sub in subscriptions)
            
            if not topic_exists:
                console.print(f"[yellow]Topic '{topic}' is not subscribed[/yellow]")
                return
            
            await plugin.unsubscribe(topic)
            console.print(f"[green]✅ Unsubscribed from '{topic}'[/green]")
            
            if save_config:
                config_path = get_config_path()
                plugin.save_config(config_path)
                console.print(f"[green]Changes saved to {config_path}[/green]")
                
        except Exception as e:
            console.print(f"[red]Unsubscribe failed: {e}[/red]")
            raise typer.Exit(1)
    
    handle_async(_unsubscribe())


# Job queue management commands
jobs_app = typer.Typer(help="Job queue management commands")
app.add_typer(jobs_app, name="jobs")


@jobs_app.command("status")
def jobs_status(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """Show job queue status."""
    
    async def _jobs_status():
        try:
            plugin = _current_plugin or load_plugin(config=config)
            
            if not plugin.config.job_queue.enabled:
                console.print("[yellow]Job queue is not enabled in configuration[/yellow]")
                return
            
            stats = plugin.get_statistics()
            
            if json_output:
                console.print(json.dumps({
                    "job_queue_enabled": stats.get("job_queue_enabled", False),
                    "job_queue_stats": stats.get("job_queue_stats", {})
                }, indent=2))
                return
            
            # Rich formatted output
            queue_table = Table(title="Job Queue Status")
            queue_table.add_column("Property", style="bold blue")
            queue_table.add_column("Value", style="green")
            
            queue_table.add_row("Enabled", "✅ Yes" if stats.get("job_queue_enabled", False) else "❌ No")
            
            if "job_queue_stats" in stats:
                job_stats = stats["job_queue_stats"]
                queue_table.add_row("Queue Name", job_stats.get("queue_name", "N/A"))
                queue_table.add_row("Queue Type", job_stats.get("type", "N/A"))
            
            console.print(queue_table)
            
        except Exception as e:
            console.print(f"[red]Failed to get job queue status: {e}[/red]")
            raise typer.Exit(1)
    
    handle_async(_jobs_status())


@jobs_app.command("worker")
def jobs_worker(
    action: str = typer.Argument(..., help="Worker action (start, stop, status)"),
    count: int = typer.Option(1, "--count", "-c", help="Number of workers"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file")
):
    """Manage RQ workers."""
    
    if action not in ["start", "stop", "status"]:
        console.print("[red]Worker action must be: start, stop, or status[/red]")
        raise typer.Exit(1)
    
    try:
        plugin = load_plugin(config=config)
        
        if not plugin.config.job_queue.enabled:
            console.print("[yellow]Job queue is not enabled in configuration[/yellow]")
            return
        
        if action == "start":
            import subprocess
            redis_url = plugin.config.job_queue.redis_url
            queue_name = plugin.config.job_queue.queue_name
            
            console.print(f"[blue]Starting {count} RQ worker(s) for queue '{queue_name}'...[/blue]")
            
            for i in range(count):
                cmd = f"rq worker {queue_name} --url {redis_url}"
                console.print(f"[dim]Worker {i+1} command: {cmd}[/dim]")
                
                # In a real implementation, you'd start these as background processes
                console.print(f"[green]Worker {i+1} started (run manually: {cmd})[/green]")
            
            console.print(f"\n[bold blue]To start workers manually, run:[/bold blue]")
            console.print(f"rq worker {queue_name} --url {redis_url}")
            
        elif action == "status":
            console.print("[blue]Checking worker status...[/blue]")

            try:
                import subprocess
                import psutil

                redis_url = plugin.config.job_queue.redis_url
                queue_name = plugin.config.job_queue.queue_name

                # Check for running RQ worker processes
                worker_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python' and proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            if f'rq worker {queue_name}' in cmdline and redis_url in cmdline:
                                worker_processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if worker_processes:
                    console.print(f"[green]✅ Found {len(worker_processes)} running worker(s)[/green]")

                    status_table = Table(title="Running Workers")
                    status_table.add_column("PID", style="bold blue")
                    status_table.add_column("Command", style="green")
                    status_table.add_column("Status", style="yellow")

                    for proc in worker_processes:
                        status_table.add_row(
                            str(proc['pid']),
                            ' '.join(proc['cmdline'][:4]) + '...' if len(proc['cmdline']) > 4 else ' '.join(proc['cmdline']),
                            "Running"
                        )

                    console.print(status_table)
                else:
                    console.print(f"[yellow]No running workers found for queue '{queue_name}'[/yellow]")
                    console.print(f"[dim]To start workers, run: rq worker {queue_name} --url {redis_url}[/dim]")

            except ImportError:
                console.print("[red]psutil not available. Install with: pip install psutil[/red]")
                console.print("[yellow]Cannot check worker status without psutil[/yellow]")
            except Exception as e:
                console.print(f"[red]Error checking worker status: {e}[/red]")

        elif action == "stop":
            console.print("[blue]Stopping workers...[/blue]")

            try:
                import subprocess
                import signal
                import psutil

                redis_url = plugin.config.job_queue.redis_url
                queue_name = plugin.config.job_queue.queue_name

                # Find and stop running RQ worker processes
                stopped_count = 0
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python' and proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            if f'rq worker {queue_name}' in cmdline and redis_url in cmdline:
                                console.print(f"[blue]Stopping worker PID {proc.info['pid']}...[/blue]")
                                proc.terminate()
                                stopped_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if stopped_count > 0:
                    console.print(f"[green]✅ Stopped {stopped_count} worker(s)[/green]")
                else:
                    console.print(f"[yellow]No running workers found for queue '{queue_name}'[/yellow]")

            except ImportError:
                console.print("[red]psutil not available. Install with: pip install psutil[/red]")
                console.print("[yellow]Cannot stop workers without psutil[/yellow]")
            except Exception as e:
                console.print(f"[red]Error stopping workers: {e}[/red]")
            
    except Exception as e:
        console.print(f"[red]Worker management failed: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()