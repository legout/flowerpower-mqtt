# Asynchronous Processing with RQ

An example demonstrating asynchronous pipeline execution using RQ (Redis Queue) for background processing.

## Description

This example shows how to use the FlowerPower MQTT Plugin with RQ for scalable message processing. It demonstrates different execution modes (sync, async, mixed), QoS levels, and bulk subscriptions for handling high-volume MQTT messages.

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

**Note:** Make sure to start an RQ worker in a separate terminal before running the example:
```bash
rq worker mqtt_pipelines --url redis://localhost:6379
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
uv run python async_with_rq.py
```

**Jupyter Notebook:**
1. Start Jupyter Lab:
   ```bash
   uv run jupyter lab
   ```
2. Open `async_with_rq.ipynb` in your browser and run the cells.

**Marimo Notebook (if applicable):**
```bash
uv run marimo run async_with_rq.py