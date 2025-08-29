# Contributing

We welcome contributions to `flowerpower-mqtt`! Whether it's reporting a bug, suggesting a new feature, improving the documentation, or submitting code, your help is greatly appreciated.

Please take a moment to review this guide before making your first contribution.

## How to Contribute

1.  **Fork the Repository**: Start by forking the `flowerpower-mqtt` repository on GitHub.
2.  **Clone Your Fork**: Clone your forked repository to your local machine.
    ```bash
    git clone https://github.com/YOUR_USERNAME/flowerpower-mqtt.git
    cd flowerpower-mqtt
    ```
3.  **Install Development Dependencies**: Set up your development environment by installing the necessary dependencies.
    ```bash
    uv pip install -e ".[dev]"
    ```
4.  **Create a Feature Branch**: Create a new branch for your feature or bug fix. Use a descriptive name (e.g., `feature/add-new-cli-command`, `bugfix/fix-connection-error`).
    ```bash
    git checkout -b feature/your-feature-name
    ```
5.  **Make Your Changes**: Implement your feature or bug fix.
    *   Adhere to the existing code style.
    *   Write clear, concise, and well-documented code.
6.  **Add Tests**: Ensure your changes are covered by tests. If you're adding a new feature, write new tests for it. If you're fixing a bug, add a test that reproduces the bug and then passes with your fix.
7.  **Run the Test Suite**: Before submitting your changes, run the entire test suite to ensure nothing is broken.
    ```bash
    pytest
    ```
8.  **Type Checking**: Ensure your code passes type checks.
    ```bash
    mypy src/
    ```
9.  **Code Formatting and Linting**: Format your code and check for linting issues.
    ```bash
    black src/
    ruff check src/
    ```
10. **Commit Your Changes**: Commit your changes with a clear and descriptive commit message. Follow conventional commit guidelines if possible.
    ```bash
    git commit -m "feat: Add new awesome feature"
    ```
11. **Push to Your Fork**: Push your changes to your fork on GitHub.
    ```bash
    git push origin feature/your-feature-name
    ```
12. **Submit a Pull Request**: Open a pull request from your feature branch to the `main` branch of the original `flowerpower-mqtt` repository.
    *   Provide a clear title and description for your pull request.
    *   Reference any related issues.
    *   Be responsive to feedback from maintainers.

## Code Style and Quality

We use `black` for code formatting, `ruff` for linting, and `mypy` for type checking. Please ensure your contributions adhere to these standards.

## Reporting Bugs

If you find a bug, please open an issue on the GitHub issue tracker. When reporting a bug, please include:

*   A clear and concise description of the bug.
*   Steps to reproduce the behavior.
*   Expected behavior.
*   Actual behavior.
*   Any relevant error messages or stack traces.
*   Your operating system, Python version, and `flowerpower-mqtt` version.

## Feature Requests

We'd love to hear your ideas for new features! Please open an issue on the GitHub issue tracker to propose new features. Describe the problem you're trying to solve and how the new feature would help.

## Documentation Improvements

High-quality documentation is crucial. If you find errors, omissions, or areas that could be improved, please open an issue or submit a pull request with your changes.

Thank you for contributing to `flowerpower-mqtt`!