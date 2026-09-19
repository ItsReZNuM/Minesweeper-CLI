"""Command-line interface entrypoint and argument parser."""

import argparse
import sys
from typing import List, Optional

from minesweeper_cli import __version__
from minesweeper_cli.config import APP_NAME, DIFFICULTIES
from minesweeper_cli.menu import MenuController
from minesweeper_cli.records import RecordsManager
from minesweeper_cli.settings import SettingsManager
from minesweeper_cli.themes import THEMES


def create_parser() -> argparse.ArgumentParser:
    """Build command-line arguments parser."""
    parser = argparse.ArgumentParser(
        prog="minesweeper",
        description=f"{APP_NAME} - A modern, colorful terminal Minesweeper game written in Python.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{APP_NAME} {__version__}",
        help="Show version information and exit.",
    )

    parser.add_argument(
        "-d", "--difficulty",
        choices=["easy", "medium", "hard", "expert"],
        type=str.lower,
        help="Directly launch game with specified difficulty preset.",
    )

    parser.add_argument(
        "-c", "--custom",
        action="store_true",
        help="Directly open custom board setup dialog.",
    )

    parser.add_argument(
        "-t", "--theme",
        choices=list(THEMES.keys()),
        type=str.lower,
        help="Select visual color theme (classic, matrix, ocean, dracula, cyberpunk, nord, monochrome).",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI execution entrypoint."""
    parser = create_parser()
    args = parser.parse_args(argv)

    settings_mgr = SettingsManager()
    records_mgr = RecordsManager()

    if args.theme:
        settings_mgr.settings.theme = args.theme
        settings_mgr.save()

    menu = MenuController(settings_manager=settings_mgr, records_manager=records_mgr)

    try:
        if args.difficulty:
            chosen = DIFFICULTIES[args.difficulty]
            menu.launch_game(chosen.width, chosen.height, chosen.mines, chosen.name)
            return 0
        elif args.custom:
            menu.menu_custom_game()
            return 0
        else:
            menu.run()
            return 0
    except KeyboardInterrupt:
        sys.stdout.write("\nThanks for playing Minesweeper CLI!\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
