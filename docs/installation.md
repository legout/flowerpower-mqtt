# Installation

This section details how to install `flowerpower-mqtt` and its dependencies.

## Prerequisites

Before installing `flowerpower-mqtt`, ensure you have the following:

*   **Python**: Version 3.11 or higher.
*   **FlowerPower**: The core `flowerpower` library must be installed.
*   **Redis**: Required for job queue functionality (asynchronous processing). You'll need a running Redis instance accessible from where `flowerpower-mqtt` will operate.

## Recommended Installation (from PyPI)

`flowerpower-mqtt` is available on PyPI and can be installed using `uv pip` (recommended) or `pip`.

### Using `uv pip` (Recommended)

`uv` is a fast Python package installer and resolver. It's the recommended way to install `flowerpower-mqtt`.

```bash
uv pip install flowerpower-mqtt
```

### Using `pip`

If you prefer using `pip`, you can install `flowerpower-mqtt` directly:

```bash
pip install flowerpower-mqtt
```

After installation, the `flowerpower-mqtt` CLI command will be available in your environment.

## Development Installation

If you plan to contribute to `flowerpower-mqtt` or want to set up a development environment, follow these steps:

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/legout/flowerpower-mqtt.git
    cd flowerpower-mqtt
    ```

2.  **Install Development Dependencies**

    ```bash
    uv pip install -e ".[dev]"
    ```

    This command installs the core library in editable mode along with development-specific dependencies like `pytest`, `black`, `ruff`, and `mypy`.

## Shell Completion

The `flowerpower-mqtt` CLI supports shell completion for various shells (bash, zsh, fish, powershell). To enable it, follow the instructions provided by `typer` for your specific shell.

For example, for `bash`:

```bash
flowerpower-mqtt --install-completion bash
```

Remember to restart your shell or source your shell's RC file (e.g., `.bashrc`, `.zshrc`) after installation for the changes to take effect.