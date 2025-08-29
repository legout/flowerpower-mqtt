# CLI Reference

The `flowerpower-mqtt` Command Line Interface (CLI) provides a comprehensive set of commands for managing MQTT connections, subscriptions, and monitoring, all with rich and interactive output.

## Global Options

These options can be used with most `flowerpower-mqtt` commands:

*   `--config`, `-c` (`Path`, optional): Specify a configuration file to use.
*   `--json` (`bool`): Output results in JSON format, useful for scripting and automation.

## Commands

### `flowerpower-mqtt connect`

Connects to an MQTT broker.

```bash
flowerpower-mqtt connect [OPTIONS]
```

**Options:**

*   `--broker`, `-b` (`str`): MQTT broker hostname (default: `localhost`).
*   `--port`, `-p` (`int`): MQTT broker port (default: `1883`).
*   `--config`, `-c` (`Path`): Configuration file to use.
*   `--base-dir` (`str`): FlowerPower project directory (default: `.`).
*   `--job-queue` (`bool`): Enable RQ job queue.
*   `--redis-url` (`str`): Redis URL for job queue (default: `redis://localhost:6379`).
*   `--save-config` (`bool`): Save the current connection configuration to a file.

**Examples:**

```bash
# Connect to a broker on default port
flowerpower-mqtt connect --broker mqtt.example.com

# Connect with job queue enabled
flowerpower-mqtt connect --broker mqtt.example.com --job-queue --redis-url redis://my-redis:6379

# Connect using a configuration file
flowerpower-mqtt connect --config my_mqtt_config.yml
```

### `flowerpower-mqtt disconnect`

Disconnects from the currently connected MQTT broker.

```bash
flowerpower-mqtt disconnect [OPTIONS]
```

**Options:**

*   `--config`, `-c` (`Path`): Configuration file to use.

**Examples:**

```bash
flowerpower-mqtt disconnect
```

### `flowerpower-mqtt subscribe`

Subscribes to an MQTT topic and links it to a FlowerPower pipeline.

```bash
flowerpower-mqtt subscribe TOPIC PIPELINE_NAME [OPTIONS]
```

**Arguments:**

*   `TOPIC` (`str`): MQTT topic pattern to subscribe to.
*   `PIPELINE_NAME` (`str`): Name of the FlowerPower pipeline to execute.

**Options:**

*   `--qos`, `-q` (`int`): QoS level (0, 1, or 2) (default: `0`).
*   `--mode`, `-m` (`str`): Execution mode (`sync`, `async`, or `mixed`) (default: `sync`).
*   `--config`, `-c` (`Path`): Configuration file to use.
*   `--save-config` (`bool`): Save the new subscription to the configuration file.

**Examples:**

```bash
# Subscribe to a topic with default settings
flowerpower-mqtt subscribe "sensors/temp" process_temp_data

# Subscribe with QoS 1 and async execution
flowerpower-mqtt subscribe "logs/system" analyze_logs --qos 1 --mode async

# Subscribe with mixed execution mode
flowerpower-mqtt subscribe "events/#" handle_event --qos 2 --mode mixed
```

### `flowerpower-mqtt unsubscribe`

Unsubscribes from a previously subscribed MQTT topic.

```bash
flowerpower-mqtt unsubscribe TOPIC [OPTIONS]
```

**Arguments:**

*   `TOPIC` (`str`): The exact MQTT topic pattern to unsubscribe from.

**Options:**

*   `--config`, `-c` (`Path`): Configuration file to use.
*   `--save-config` (`bool`): Save changes to the configuration file.

**Examples:**

```bash
flowerpower-mqtt unsubscribe "sensors/temp"
```

### `flowerpower-mqtt listen`

Starts listening for incoming MQTT messages and triggers pipeline execution.

```bash
flowerpower-mqtt listen [OPTIONS]
```

**Options:**

*   `--background`, `-bg` (`bool`): Run the listener in the background.
*   `--override-mode` (`str`): Override the execution mode for all pipelines (`sync`, `async`, or `mixed`).
*   `--config`, `-c` (`Path`): Configuration file to use.
*   `--timeout` (`int`): Stop listening after a specified number of seconds.

**Examples:**

```bash
# Start listening indefinitely (blocks terminal)
flowerpower-mqtt listen

# Start listening in the background
flowerpower-mqtt listen --background &

# Override all subscriptions to use async execution
flowerpower-mqtt listen --override-mode async --config my_config.yml

# Listen for 60 seconds
flowerpower-mqtt listen --timeout 60
```

### `flowerpower-mqtt status`

Shows the current plugin status and statistics.

```bash
flowerpower-mqtt status [OPTIONS]
```

**Options:**

*   `--config`, `-c` (`Path`): Configuration file to use.
*   `--json` (`bool`): Output status as JSON.

**Examples:**

```bash
flowerpower-mqtt status
flowerpower-mqtt status --json
```

### `flowerpower-mqtt monitor`

Monitors the MQTT plugin in real-time, displaying live statistics and subscription activity.

```bash
flowerpower-mqtt monitor [OPTIONS]
```

**Options:**

*   `--config`, `-c` (`Path`): Configuration file to use.
*   `--interval`, `-i` (`int`): Update interval in seconds (default: `5`).
*   `--duration`, `-d` (`int`): Monitor duration in seconds.
*   `--json` (`bool`): Output monitoring data as JSON.

**Examples:**

```bash
# Monitor every 5 seconds indefinitely
flowerpower-mqtt monitor

# Monitor for 300 seconds (5 minutes)
flowerpower-mqtt monitor --duration 300

# Output real-time data as JSON
flowerpower-mqtt monitor --json
```

### `flowerpower-mqtt list-subscriptions`

Lists all active MQTT subscriptions.

```bash
flowerpower-mqtt list-subscriptions [OPTIONS]
```

**Options:**

*   `--config`, `-c` (`Path`): Configuration file to use.
*   `--active` (`bool`): Show only subscriptions with messages received.
*   `--json` (`bool`): Output subscriptions as JSON.

**Examples:**

```bash
flowerpower-mqtt list-subscriptions
flowerpower-mqtt list-subscriptions --active
flowerpower-mqtt list-subscriptions --json
```

## Configuration Commands (`flowerpower-mqtt config`)

A sub-command group for managing configuration files.

### `flowerpower-mqtt config create`

Creates a new configuration file.

```bash
flowerpower-mqtt config create [OPTIONS]
```

**Options:**

*   `--output`, `-o` (`Path`): Output file path (default: `mqtt_config.yml`).
*   `--interactive`, `-i` (`bool`): Start an interactive configuration wizard.
*   `--job-queue` (`bool`): Include job queue configuration in the new file.

**Examples:**

```bash
# Create a default config file
flowerpower-mqtt config create

# Create interactively
flowerpower-mqtt config create --interactive

# Create with job queue enabled and custom output path
flowerpower-mqtt config create --job-queue --output production_config.yml
```

### `flowerpower-mqtt config validate`

Validates an existing configuration file.

```bash
flowerpower-mqtt config validate CONFIG_FILE
```

**Arguments:**

*   `CONFIG_FILE` (`Path`): Path to the configuration file to validate.

**Examples:**

```bash
flowerpower-mqtt config validate my_mqtt_config.yml
```

### `flowerpower-mqtt config show`

Displays the content of a configuration file.

```bash
flowerpower-mqtt config show [OPTIONS]
```

**Options:**

*   `--config`, `-c` (`Path`): Configuration file to show.
*   `--format` (`str`): Output format (`yaml` or `json`) (default: `yaml`).

**Examples:**

```bash
flowerpower-mqtt config show
flowerpower-mqtt config show --config production_config.yml --format json
```

### `flowerpower-mqtt config edit`

Opens a configuration file in your default editor (`$EDITOR`).

```bash
flowerpower-mqtt config edit [OPTIONS]
```

**Options:**

*   `--config`, `-c` (`Path`): Configuration file to edit.
*   `--editor` (`str`): Specify a different editor to use.

**Examples:**

```bash
flowerpower-mqtt config edit
flowerpower-mqtt config edit --editor nano my_mqtt_config.yml
```

## Job Queue Commands (`flowerpower-mqtt jobs`)

A sub-command group for managing RQ job queues.

### `flowerpower-mqtt jobs status`

Shows the status of the job queue.

```bash
flowerpower-mqtt jobs status [OPTIONS]
```

**Options:**

*   `--config`, `-c` (`Path`): Configuration file to use.
*   `--json` (`bool`): Output status as JSON.

**Examples:**

```bash
flowerpower-mqtt jobs status
flowerpower-mqtt jobs status --json
```

### `flowerpower-mqtt jobs worker`

Manages RQ workers (start, stop, status).

```bash
flowerpower-mqtt jobs worker ACTION [OPTIONS]
```

**Arguments:**

*   `ACTION` (`str`): Worker action (`start`, `stop`, or `status`).

**Options:**

*   `--count`, `-c` (`int`): Number of workers to start (default: `1`).
*   `--config`, `-c` (`Path`): Configuration file to use.

**Examples:**

```bash
# Get status of running workers
flowerpower-mqtt jobs worker status

# Start 2 RQ workers (note: this command only prints the command to run manually)
flowerpower-mqtt jobs worker start --count 2

# Stop running workers
flowerpower-mqtt jobs worker stop
```