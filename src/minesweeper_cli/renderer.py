"""Terminal UI rendering components using Rich."""

import shutil
from typing import List, Optional, Tuple
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.box import SQUARE, ROUNDED, SIMPLE, DOUBLE

from minesweeper_cli.board import Board, GameStatus
from minesweeper_cli.config import (
    APP_NAME,
    AUTHOR,
    GITHUB_PROFILE,
    GITHUB_REPO,
    TELEGRAM,
    INSTAGRAM,
    TERMINAL_DEFAULT,
)
from minesweeper_cli.themes import Theme, get_theme
from minesweeper_cli.timer import GameTimer

console = Console()


def render_header(theme: Theme) -> Panel:
    """Render top application banner."""
    text = Text()
    text.append("💣 ", style="bold red")
    text.append(APP_NAME.upper(), style=f"bold {theme.accent_style}")
    text.append(" 💣", style="bold red")
    return Panel(
        Align.center(text),
        border_style=theme.border_style,
        box=SQUARE,
        padding=(0, 1),
    )


def render_status_bar(
    board: Board,
    timer: GameTimer,
    theme: Theme,
    difficulty_name: str,
    compact: bool = False,
) -> Panel:
    """Render game status bar showing flags, remaining mines, timer, and difficulty."""
    status_text = Text()

    # Difficulty indicator
    status_text.append(f" {difficulty_name} ", style=f"bold black on {theme.accent_style}")
    status_text.append("  ")

    # Mines & Flags
    status_text.append("💣 Mines: ", style="bold white")
    status_text.append(f"{board.num_mines} ", style="bold bright_yellow")

    status_text.append("🚩 Flags: ", style="bold white")
    status_text.append(f"{board.flagged_count} ", style="bold bright_cyan")

    rem = board.remaining_flags
    rem_style = "bold bright_green" if rem >= 0 else "bold bright_red"
    status_text.append("Left: ", style="bold white")
    status_text.append(f"{rem:<3} ", style=rem_style)

    # Timer
    status_text.append("⏱️ Time: ", style="bold white")
    status_text.append(f"{timer.formatted()} ", style="bold bright_white")

    if not compact:
        controls_hint = Text("\n[W/A/S/D] Move • [Enter/Space] Open • [F] Flag • [C] Chord • [R] Restart • [Q] Menu", style="dim italic")
        content = Group(Align.center(status_text), Align.center(controls_hint))
    else:
        content = Align.center(status_text)

    return Panel(
        content,
        border_style=theme.border_style,
        box=SQUARE,
        padding=(0, 0),
    )


def render_board(
    board: Board,
    cursor_x: int,
    cursor_y: int,
    theme: Theme,
    show_coords: bool = True,
    compact: bool = False,
    viewport: Optional[Tuple[int, int, int, int]] = None,
) -> Panel:
    """Render Minesweeper grid with cursor highlight and cell states."""
    # Determine visible coordinate range based on viewport (min_x, max_x, min_y, max_y)
    if viewport:
        min_x, max_x, min_y, max_y = viewport
    else:
        min_x, max_x, min_y, max_y = 0, board.width, 0, board.height

    visible_w = max_x - min_x
    visible_h = max_y - min_y

    table = Table(
        show_header=False,
        show_edge=False,
        pad_edge=False,
        box=None,
        padding=(0, 0),
        collapse_padding=True,
    )

    # Add coordinate column if enabled
    if show_coords:
        table.add_column("row_num", justify="right", style="dim", no_wrap=True)

    for _ in range(visible_w):
        table.add_column(justify="center", no_wrap=True)

    # Header row for column coordinates
    if show_coords:
        header_cells = [Text("   ", style="dim")]
        for x in range(min_x, max_x):
            header_cells.append(Text(f"{x % 100:2d} ", style="dim cyan"))
        table.add_row(*header_cells)

    for y in range(min_y, max_y):
        row_items = []
        if show_coords:
            row_items.append(Text(f"{y:2d} │", style="dim cyan"))

        for x in range(min_x, max_x):
            cell = board.get_cell(x, y)
            is_cursor = (x == cursor_x and y == cursor_y)
            cell_text = Text()

            if cell.is_flagged:
                if board.status == GameStatus.LOST and not cell.is_mine:
                    # Incorrect flag placement
                    char = theme.wrong_flag_symbol
                    style = theme.wrong_flag_style
                else:
                    char = theme.flag_symbol
                    style = theme.flag_style
            elif cell.is_revealed:
                if cell.is_mine:
                    if cell.is_exploded:
                        char = theme.exploded_symbol
                        style = theme.exploded_style
                    else:
                        char = theme.mine_symbol
                        style = theme.mine_style
                elif cell.adjacent_mines > 0:
                    char = str(cell.adjacent_mines)
                    style = theme.number_styles.get(cell.adjacent_mines, "bold white")
                else:
                    char = " "
                    style = theme.cell_revealed
            else:
                char = theme.hidden_symbol
                style = theme.cell_hidden

            # Format cell with cursor highlight
            if is_cursor:
                cursor_repr = f"[{char}]" if not compact else f">{char}<"
                cell_text.append(cursor_repr, style=theme.cell_cursor)
            else:
                cell_repr = f" {char} " if not compact else f" {char}"
                cell_text.append(cell_repr, style=style)

            row_items.append(cell_text)

        table.add_row(*row_items)

    footer_note = ""
    if visible_w < board.width or visible_h < board.height:
        footer_note = f" (Showing {min_x+1}-{max_x} of {board.width} col, {min_y+1}-{max_y} of {board.height} row) "

    return Panel(
        Align.center(table),
        title=f"[bold {theme.accent_style}]Minesweeper Board{footer_note}[/]",
        border_style=theme.border_style,
        box=SQUARE,
        padding=(0, 1),
    )


def render_victory(timer: GameTimer, theme: Theme, is_new_best: bool = False) -> Panel:
    """Render victory congratulations panel."""
    content = Text()
    content.append("\n🏆  VICTORY! ALL MINES CLEARED!  🏆\n\n", style="bold bright_green")
    content.append(f"Completion Time: {timer.formatted()}\n", style="bold bright_white")
    if is_new_best:
        content.append("⭐ NEW RECORD BEST TIME! ⭐\n", style="bold bright_yellow")
    content.append("\n[R] Play Again  •  [M] Main Menu  •  [Q] Exit\n", style="bold cyan")
    return Panel(
        Align.center(content),
        border_style="bright_green",
        box=DOUBLE,
        padding=(1, 2),
    )


def render_game_over(theme: Theme) -> Panel:
    """Render game over detonation banner."""
    content = Text()
    content.append("\n💥  GAME OVER! YOU DETONATED A MINE!  💥\n\n", style="bold bright_red")
    content.append("All mine positions and incorrect flags have been revealed.\n", style="dim white")
    content.append("\n[R] Try Again  •  [M] Main Menu  •  [Q] Exit\n", style="bold cyan")
    return Panel(
        Align.center(content),
        border_style="bright_red",
        box=DOUBLE,
        padding=(1, 2),
    )


def render_about(theme: Theme) -> Panel:
    """Render About the Creator card."""
    body = Text()
    body.append("A B O U T   T H E   C R E A T O R\n\n", style=f"bold {theme.accent_style}")
    body.append("Author: ", style="bold white")
    body.append(f"{AUTHOR}\n", style="bold bright_cyan")
    body.append("Version: ", style="bold white")
    body.append("v0.2.2\n", style="bold bright_yellow")
    body.append("GitHub: ", style="bold white")
    body.append(f"{GITHUB_PROFILE.replace('https://', '')}\n", style="underline cyan")
    body.append("Repository: ", style="bold white")
    body.append(f"{GITHUB_REPO.replace('https://', '')}\n", style="underline cyan")
    body.append("Telegram: ", style="bold white")
    body.append(f"{TELEGRAM.replace('https://', '')}\n", style="underline cyan")
    body.append("Instagram: ", style="bold white")
    body.append(f"{INSTAGRAM.replace('https://', '')}\n", style="underline cyan")
    body.append("Terminal: ", style="bold white")
    body.append(f"{TERMINAL_DEFAULT}\n\n", style="bright_white")

    body.append("⭐ Enjoying the game? Please consider starring the repository on GitHub!\n", style="bold bright_yellow")
    body.append("It means a lot and supports development.\n\n", style="italic white")
    body.append(f"Repository URL: {GITHUB_REPO}\n\n", style="bold underline bright_cyan")
    body.append("Press any key to return to Main Menu", style="dim")

    return Panel(
        Align.center(body),
        title=f"[bold {theme.accent_style}]About[/]",
        border_style=theme.border_style,
        box=SQUARE,
        padding=(1, 3),
    )


def render_how_to_play(theme: Theme) -> Panel:
    """Render concise gameplay rules and tips."""
    text = Text()
    text.append("HOW TO PLAY MINESWEEPER\n\n", style=f"bold {theme.accent_style}")
    text.append("1. Objective:\n", style="bold bright_white")
    text.append("   Uncover all cells on the board that do not contain a mine.\n\n", style="white")

    text.append("2. Numbers:\n", style="bold bright_white")
    text.append("   Revealed numbers indicate how many mines are directly adjacent (1 to 8).\n\n", style="white")

    text.append("3. First Move Protection:\n", style="bold bright_white")
    text.append("   Your first revealed cell is always guaranteed safe with an opening area.\n\n", style="white")

    text.append("4. Controls:\n", style="bold bright_white")
    text.append("   • Arrow Keys / WASD : Navigate cursor\n", style="cyan")
    text.append("   • Enter / Space     : Reveal selected cell\n", style="cyan")
    text.append("   • F                 : Place or remove a flag\n", style="cyan")
    text.append("   • C                 : Chord reveal (opens unflagged neighbors when flags match number)\n", style="cyan")
    text.append("   • R                 : Restart board\n", style="cyan")
    text.append("   • Q                 : Return to main menu\n\n", style="cyan")

    text.append("Press any key to return to Main Menu", style="dim")
    return Panel(
        Align.center(text),
        title=f"[bold {theme.accent_style}]Guide[/]",
        border_style=theme.border_style,
        box=SQUARE,
        padding=(1, 3),
    )
