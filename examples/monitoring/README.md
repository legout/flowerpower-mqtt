# Monitoring and Statistics Example

An example demonstrating how to monitor plugin performance, track statistics, and manage subscriptions dynamically.

## Description

This example shows comprehensive monitoring capabilities including real-time statistics tracking, performance metrics, and dynamic subscription management. It demonstrates how to monitor message processing rates, error rates, and subscription health.

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
uv run python monitoring.py
```

**Jupyter Notebook:**
1. Start Jupyter Lab:
   ```bash
   uv run jupyter lab
   ```
2. Open `monitoring.ipynb` in your browser and run the cells.

**Marimo Notebook:**
This example works particularly well as a Marimo notebook for interactive monitoring:
```bash
uv run marimo run monitoring.py