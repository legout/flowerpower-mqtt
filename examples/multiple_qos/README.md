# Multiple QoS Levels Example

An example demonstrating how to use different QoS levels for different types of messages and use cases.

## Description

This example shows how to configure different QoS (Quality of Service) levels for various message types and use cases. It demonstrates QoS 0 (fire-and-forget), QoS 1 (at-least-once), and QoS 2 (exactly-once) delivery guarantees with appropriate execution modes.

## How to Run

### Prerequisites

- Python 3.11+
- `uv` package manager
- Docker (for MQTT broker and Redis)

### 1. Start Services

Start both MQTT broker and Redis using Docker:

```bash
docker-compose up -d mqtt redis
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
uv run python multiple_qos.py
```

**Jupyter Notebook:**
1. Start Jupyter Lab:
   ```bash
   uv run jupyter lab
   ```
2. Open `multiple_qos.ipynb` in your browser and run the cells.

**Marimo Notebook (if applicable):**
```bash
uv run marimo run multiple_qos.py