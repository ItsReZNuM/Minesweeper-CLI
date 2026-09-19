# Contributing to Minesweeper CLI

Thank you for your interest in contributing to Minesweeper CLI! We welcome bug reports, feature suggestions, and pull requests.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ItsReZNuM/Minesweeper-CLI.git
   cd Minesweeper-CLI
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install the package in editable mode with development dependencies:**
   ```bash
   python -m pip install -e ".[dev]"
   ```

4. **Run the game:**
   ```bash
   minesweeper
   # or
   python -m minesweeper_cli
   ```

## Running Tests

Ensure all automated tests pass before submitting a pull request:
```bash
python -m pytest tests/ -v
```

## Packaging Verification

Check distribution builds:
```bash
python -m build
python -m twine check dist/*
```

## Code Guidelines

- Target **Python 3.10+**.
- Follow **PEP 8** style conventions.
- Maintain cross-platform compatibility (Windows, Linux, macOS, Android/Termux).
- Avoid unnecessary external dependencies.
- Keep comments concise and reserved for non-obvious algorithms or platform quirks.
- Write tests for new gameplay logic or CLI behaviors.

## Submitting Pull Requests

1. Create a feature branch: `git checkout -b feature/your-feature-name`.
2. Commit changes using clear, descriptive messages.
3. Push to your branch and open a Pull Request with a summary of changes.
