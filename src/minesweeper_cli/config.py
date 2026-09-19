"""Global configuration, difficulty presets, and branding metadata."""

from dataclasses import dataclass
from typing import Dict

APP_NAME = "Minesweeper CLI"
APP_SLUG = "minesweeper-cli"
AUTHOR = "Made with ❤️ by ItsReZNuM"
GITHUB_PROFILE = "https://github.com/ItsReZNuM"
GITHUB_REPO = "https://github.com/ItsReZNuM/Minesweeper-CLI"
TELEGRAM = "https://t.me/ItsReZNuM"
INSTAGRAM = "https://instagram.com/rez.num"
TERMINAL_DEFAULT = "Classic CMD"


@dataclass(frozen=True)
class DifficultyConfig:
    """Predefined difficulty configuration."""
    name: str
    width: int
    height: int
    mines: int
    description: str


DIFFICULTIES: Dict[str, DifficultyConfig] = {
    "easy": DifficultyConfig(
        name="Easy",
        width=9,
        height=9,
        mines=10,
        description="9x9 board with 10 mines (Beginner friendly)",
    ),
    "medium": DifficultyConfig(
        name="Medium",
        width=16,
        height=16,
        mines=40,
        description="16x16 board with 40 mines (Standard challenge)",
    ),
    "hard": DifficultyConfig(
        name="Hard",
        width=30,
        height=16,
        mines=99,
        description="30x16 board with 99 mines (Classic advanced)",
    ),
    "expert": DifficultyConfig(
        name="Expert",
        width=30,
        height=24,
        mines=150,
        description="30x24 board with 150 mines (Master challenge)",
    ),
}

# Custom mode boundary constraints
MIN_BOARD_WIDTH = 4
MAX_BOARD_WIDTH = 60
MIN_BOARD_HEIGHT = 4
MAX_BOARD_HEIGHT = 40
MIN_MINES_COUNT = 1
