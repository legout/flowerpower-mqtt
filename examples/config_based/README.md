# Configuration-Based Example

An example demonstrating how to use YAML configuration files for managing complex MQTT setups.

## Description

This example shows how to use configuration files to manage complex MQTT setups with multiple subscriptions, different QoS levels, and execution modes. It demonstrates loading plugins from YAML files and programmatically adding additional subscriptions.

## How to Run

### Prerequisites

- Python 3.11+
- `uv` package manager
- Docker (for MQTT broker)

### 1. Start Services

Start the MQTT broker using Docker:

```bash
docker-compose up -d mqtt
```

### 2. Install Dependencies

Install the required Python packages:

```bash
uv pip install -e ../..
uv pip install .
```

### 3. Run the Example

**Python Script:**
```bash
uv run python config_based.py
```

**Jupyter Notebook:**
1. Start Jupyter Lab:
   ```bash
   uv run jupyter lab
   ```
2. Open `config_based.ipynb` in your browser and run the cells.

**Marimo Notebook (if applicable):**
```bash
uv run marimo run config_based.py