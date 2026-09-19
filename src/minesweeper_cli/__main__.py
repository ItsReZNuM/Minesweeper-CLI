"""Main entrypoint when invoked as a module: python -m minesweeper_cli."""

import sys
from minesweeper_cli.cli import main

if __name__ == "__main__":
    sys.exit(main())
