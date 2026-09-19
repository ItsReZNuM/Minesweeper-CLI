# Minesweeper CLI 💣

[![Tests & Lint](https://github.com/ItsReZNuM/Minesweeper-CLI/actions/workflows/tests.yml/badge.svg)](https://github.com/ItsReZNuM/Minesweeper-CLI/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-pep8-brightgreen.svg)](https://pep8.org/)

A modern, colorful, production-quality terminal Minesweeper game built in Python using [Rich](https://github.com/Textualize/rich). Designed for cross-platform play across Windows (CMD, PowerShell, Windows Terminal), Linux, macOS, SSH, and Android (Termux).

```text
┌────────────────────────────────────────────────────────────┐
│                    💣 MINESWEEPER CLI 💣                   │
├────────────────────────────────────────────────────────────┤
│  Medium   💣 Mines: 40  🚩 Flags: 12  Left: 28   ⏱️ 01:42   │
├────────────────────────────────────────────────────────────┤
│                     Minesweeper Board                      │
│     00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15        │
│  0 │ ·  ·  1  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■        │
│  1 │ 1  1  2  ■ [2] ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■        │
│  2 │ 0  0  1  ■  🚩 ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■        │
│  3 │ 0  0  1  1  2  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■        │
│  4 │ 1  1  0  0  1  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■        │
└────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- **First-Move Protection**: Your first clicked tile is guaranteed safe and opens up the initial clearing.
- **7 Visual Themes**: Classic, Ocean, Matrix, Dracula, Cyberpunk, Nord, and Monochrome.
- **Predefined Difficulties**:
  - **Easy**: 9x9 board with 10 mines
  - **Medium**: 16x16 board with 40 mines
  - **Hard**: 30x16 board with 99 mines
  - **Expert**: 30x24 board with 150 mines
- **Custom Board Mode**: Configure your own width (4–60), height (4–40), and mine density.
- **Chord Reveal**: Press `C` on a revealed number when all surrounding flags are placed to instantly open remaining neighbors.
- **Cross-Platform Single-Key Input**: Responsive single-key control (`readchar`) with automatic fallback to Enter-based command mode if raw terminal mode is unavailable.
- **Responsive Layout & Viewport Scrolling**: Auto-scrolls and pans around the cursor on small screens, preventing broken line wraps in mobile terminals like Termux.
- **Configurable Controls**: Remap any gameplay action with key conflict validation.
- **Persistent High Scores & Statistics**: Tracks completion best times, total games played, wins, losses, and custom configurations.
- **Zero Heavy Frameworks**: Pure Python with lightweight, high-performance terminal rendering.

---

## 🚀 Installation

### Local Development Installation (Current)

Clone the repository and install in editable mode:

```bash
git clone https://github.com/ItsReZNuM/Minesweeper-CLI.git
cd Minesweeper-CLI
python -m pip install -e .
```

You can now run the game directly:

```bash
minesweeper
```

Or run via module execution without PATH modification:

```bash
python -m minesweeper_cli
```

### PyPI Installation (Future Release)

Once published to PyPI:

```bash
pip install minesweeper-cli
minesweeper
```

> [!NOTE]
> **PyPI Namespace Advisory**: The package name `minesweeper-cli` is currently registered on PyPI (v1.0.3 by an independent third party). To publish to PyPI under this exact name, an ownership transfer request or PyPI PEP 541 claim is required. Alternatively, future releases may be distributed under a dedicated name such as `reznum-minesweeper` or `minesweeper-terminal`.

---

## 🎮 How to Play & Controls

Navigate the cursor over tiles, reveal safe cells, and flag suspected mines.

### Default Controls

| Action | Default Keys | Description |
| :--- | :--- | :--- |
| **Move Cursor** | `W` / `A` / `S` / `D` or `Arrow Keys` | Move cursor Up, Left, Down, Right |
| **Reveal Cell** | `Enter` or `Space` | Open hidden cell at cursor |
| **Toggle Flag** | `F` | Place or remove a flag on cursor |
| **Chord Reveal**| `C` | Open all adjacent unflagged cells |
| **Restart Game**| `R` | Reset and generate a fresh board |
| **Quit to Menu**| `Q` or `Esc` | Return to main menu |

### Fallback Command Mode

If running in non-interactive terminals, redirected streams, or legacy shells without raw input support:
- Type `w`, `a`, `s`, `d` to move.
- Type `r` to reveal or `f` to flag.
- Type direct coordinates: `r <x> <y>` to reveal cell `(x, y)` or `f <x> <y>` to flag `(x, y)`.
- Type `q` to return to the menu.

---

## ⚙️ Command-Line Arguments

Launch directly into specific game modes or themes:

```bash
# Display help and usage
minesweeper --help

# Display version
minesweeper --version

# Directly launch specific difficulty preset
minesweeper --difficulty easy
minesweeper --difficulty medium
minesweeper --difficulty hard
minesweeper --difficulty expert

# Directly open custom board configuration dialog
minesweeper --custom

# Select a visual theme on launch
minesweeper --theme matrix
```

---

## 🎨 Themes Showcase

Themes alter board colors, borders, menus, status indicators, and numbers 1–8:

1. **Classic**: Traditional Windows Minesweeper palette with bright primary numbers.
2. **Matrix**: Digital phosphor rain with emerald borders and hacker aesthetic.
3. **Ocean**: Deep blues, cyan reefs, and serene marine highlights.
4. **Dracula**: Modern dark mode with purple, pink, and vibrant accents.
5. **Cyberpunk**: High-voltage neon yellow, electric magenta, and neon cyan.
6. **Nord**: Cool arctic blues, slate gray, and pastel typography.
7. **Monochrome**: High-contrast grayscale suitable for any 8-color terminal or monochrome display.

You can switch themes in **Settings > Theme** or via `minesweeper --theme <name>`.

---

## 📱 Termux & Mobile Compatibility

Minesweeper CLI is built to run smoothly on Android via **Termux**:
- Viewport auto-centers around the cursor when boards are wider than the terminal.
- Supports compact rendering mode (`Settings > Compact Mode: ON` or auto-detected).
- Uses standard terminal character fallbacks if your mobile font lacks full Unicode emoji support.

To install on Termux:
```bash
pkg update && pkg install python git
git clone https://github.com/ItsReZNuM/Minesweeper-CLI.git
cd Minesweeper-CLI
pip install -e .
minesweeper
```

---

## 📁 Project Structure

```text
Minesweeper-CLI/
├── .github/
│   └── workflows/
│       ├── tests.yml        # CI test matrix (Python 3.10-3.13 on Linux/Win/macOS)
│       └── release.yml      # Release packaging automation
├── src/
│   └── minesweeper_cli/
│       ├── __init__.py      # Package version and metadata
│       ├── __main__.py      # python -m minesweeper_cli entrypoint
│       ├── board.py         # Pure engine logic, flood-fill, chords, win/loss
│       ├── cell.py          # Cell data structure and state
│       ├── cli.py           # Command-line argument parsing and dispatcher
│       ├── config.py        # Difficulty presets and application constants
│       ├── controls.py      # Action mappings, key normalization, conflict checks
│       ├── game.py          # Interactive game session and viewport scrolling
│       ├── menu.py          # Main menu, custom dialogs, settings, records
│       ├── persistence.py   # Atomic filesystem storage using platformdirs
│       ├── platform_compat.py # Cross-platform single-key reader & fallback
│       ├── records.py       # Best times and gameplay statistics tracker
│       ├── renderer.py      # Rich terminal UI components and styling
│       ├── settings.py      # User configuration and keybinding storage
│       ├── themes.py        # 7 distinct color themes
│       ├── timer.py         # Non-busy monotonic gameplay duration timer
│       └── py.typed         # PEP 561 type marker
├── tests/
│   ├── test_board.py        # Board generation, rules, chords, win/loss
│   ├── test_cli.py          # CLI flags and arguments
│   ├── test_controls.py     # Control mappings and conflict validation
│   ├── test_game.py         # Viewport calculation and command parser
│   ├── test_records.py      # Statistics, best times, custom records
│   └── test_settings.py     # Settings persistence and corrupted data recovery
├── CHANGELOG.md             # Semantic version history
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
├── MANIFEST.in              # Package manifest
├── pyproject.toml           # Modern PEP 517/621 packaging configuration
└── README.md
```

---

## 🧪 Testing

Run the automated test suite with `pytest`:

```bash
python -m pytest tests/ -v
```

---

## 📦 Building and Packaging

Build the source distribution and wheel:

```bash
python -m build
```

Verify the distribution packages:

```bash
python -m twine check dist/*
```

---

## 👤 Author

**Made with ❤️ by ItsReZNuM**

- **GitHub Profile**: [https://github.com/ItsReZNuM](https://github.com/ItsReZNuM)
- **Repository**: [https://github.com/ItsReZNuM/Minesweeper-CLI](https://github.com/ItsReZNuM/Minesweeper-CLI)
- **Telegram**: [https://t.me/ItsReZNuM](https://t.me/ItsReZNuM)
- **Instagram**: [https://instagram.com/rez.num](https://instagram.com/rez.num)

⭐ **Enjoying the game?** Please consider starring the repository on GitHub! It means a lot and supports future development.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
