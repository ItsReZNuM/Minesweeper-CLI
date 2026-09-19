"""Interactive Minesweeper gameplay session manager."""

import os
from typing import Optional, Tuple
from rich.console import Console
from rich.live import Live

from minesweeper_cli.board import Board, GameStatus
from minesweeper_cli.controls import (
    ACTION_UP,
    ACTION_DOWN,
    ACTION_LEFT,
    ACTION_RIGHT,
    ACTION_REVEAL,
    ACTION_FLAG,
    ACTION_CHORD,
    ACTION_RESTART,
    ACTION_QUIT,
    get_action_for_key,
)
from minesweeper_cli.platform_compat import InputReader, get_terminal_size
from minesweeper_cli.records import RecordsManager
from minesweeper_cli.renderer import (
    render_header,
    render_status_bar,
    render_board,
    render_victory,
    render_game_over,
)
from minesweeper_cli.settings import Settings
from minesweeper_cli.themes import get_theme
from minesweeper_cli.timer import GameTimer

console = Console()


class GameSession:
    """Manages active game loop, viewport panning, and state transitions."""

    def __init__(
        self,
        width: int,
        height: int,
        num_mines: int,
        mode_name: str,
        settings: Settings,
        records: RecordsManager,
        custom_config: Optional[Tuple[int, int, int]] = None,
        input_reader: Optional[InputReader] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.mode_name = mode_name
        self.settings = settings
        self.records = records
        self.custom_config = custom_config
        self.theme = get_theme(settings.theme)
        self.reader = input_reader or InputReader()

        self.board = Board(width, height, num_mines)
        self.timer = GameTimer()
        self.cursor_x = width // 2
        self.cursor_y = height // 2
        self.is_new_best = False

    def _calculate_viewport(self, cols: int, lines: int) -> Tuple[int, int, int, int]:
        """Compute visible subgrid bounds to ensure clean display on small terminals and Termux."""
        cell_width = 2 if self.settings.compact_mode else 3
        margin_x = 8 if self.settings.show_coords else 4
        margin_y = 10  # headers, status bar, padding

        max_visible_w = max(4, (cols - margin_x) // cell_width)
        max_visible_h = max(4, lines - margin_y)

        if max_visible_w >= self.width and max_visible_h >= self.height:
            return 0, self.width, 0, self.height

        # Slide viewport to keep cursor centered
        half_w = max_visible_w // 2
        half_h = max_visible_h // 2

        min_x = max(0, min(self.cursor_x - half_w, self.width - max_visible_w))
        max_x = min(self.width, min_x + max_visible_w)

        min_y = max(0, min(self.cursor_y - half_h, self.height - max_visible_h))
        max_y = min(self.height, min_y + max_visible_h)

        return min_x, max_x, min_y, max_y

    def _draw_frame(self) -> None:
        """Clear and draw header, status bar, and board."""
        cols, lines = get_terminal_size()
        viewport = self._calculate_viewport(cols, lines)

        # Clear screen cleanly across platforms
        console.clear()
        console.print(render_header(self.theme))
        console.print(
            render_status_bar(
                board=self.board,
                timer=self.timer,
                theme=self.theme,
                difficulty_name=self.mode_name,
                compact=self.settings.compact_mode or cols < 60,
            )
        )
        console.print(
            render_board(
                board=self.board,
                cursor_x=self.cursor_x,
                cursor_y=self.cursor_y,
                theme=self.theme,
                show_coords=self.settings.show_coords,
                compact=self.settings.compact_mode or cols < 60,
                viewport=viewport,
            )
        )

    def _handle_fallback_command(self, cmd: str) -> Optional[str]:
        """Parse structured commands when running in Enter-based fallback mode."""
        parts = cmd.strip().split()
        if not parts:
            return ACTION_REVEAL

        action_word = parts[0].lower()

        # Check for coordinate syntax: 'r 3 4' or 'f 3 4' or 'm 3 4'
        if len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
            tx, ty = int(parts[1]), int(parts[2])
            if self.board.in_bounds(tx, ty):
                self.cursor_x, self.cursor_y = tx, ty
                if action_word in ("r", "reveal", "open"):
                    return ACTION_REVEAL
                if action_word in ("f", "flag"):
                    return ACTION_FLAG
                if action_word in ("m", "move", "goto"):
                    return None

        # Standard action resolution
        action = get_action_for_key(action_word, self.settings.key_bindings)
        if action:
            return action

        if action_word in ("q", "quit", "exit"):
            return ACTION_QUIT
        if action_word in ("r", "restart"):
            return ACTION_RESTART
        if action_word in ("f", "flag"):
            return ACTION_FLAG
        if action_word in ("c", "chord"):
            return ACTION_CHORD

        return None

    def run(self) -> None:
        """Run interactive game loop until player wins, loses, or quits to menu."""
        while True:
            self._draw_frame()

            # If game is finished, display end panel and await replay/menu decision
            if self.board.status in (GameStatus.WON, GameStatus.LOST):
                if self.board.status == GameStatus.WON:
                    console.print(render_victory(self.timer, self.theme, self.is_new_best))
                else:
                    console.print(render_game_over(self.theme))

                key = self.reader.read_key("Choice [R/M/Q] > ")
                if key in ("r", "restart"):
                    self.board = Board(self.width, self.height, self.num_mines)
                    self.timer.reset()
                    self.cursor_x = self.width // 2
                    self.cursor_y = self.height // 2
                    self.is_new_best = False
                    continue
                break

            # Read user input
            raw_input = self.reader.read_key("Action > " if self.reader.fallback_mode else "")

            if self.reader.fallback_mode:
                action = self._handle_fallback_command(raw_input)
            else:
                action = get_action_for_key(raw_input, self.settings.key_bindings)

            if action == ACTION_QUIT:
                break
            elif action == ACTION_RESTART:
                self.board = Board(self.width, self.height, self.num_mines)
                self.timer.reset()
                self.cursor_x = self.width // 2
                self.cursor_y = self.height // 2
                self.is_new_best = False
            elif action == ACTION_UP:
                self.cursor_y = max(0, self.cursor_y - 1)
            elif action == ACTION_DOWN:
                self.cursor_y = min(self.height - 1, self.cursor_y + 1)
            elif action == ACTION_LEFT:
                self.cursor_x = max(0, self.cursor_x - 1)
            elif action == ACTION_RIGHT:
                self.cursor_x = min(self.width - 1, self.cursor_x + 1)
            elif action == ACTION_FLAG:
                self.board.toggle_flag(self.cursor_x, self.cursor_y)
            elif action == ACTION_REVEAL:
                if self.board.status == GameStatus.READY:
                    self.timer.start()
                self.board.reveal(self.cursor_x, self.cursor_y)
                self._check_game_end()
            elif action == ACTION_CHORD:
                if self.board.status == GameStatus.PLAYING:
                    self.board.chord_reveal(self.cursor_x, self.cursor_y)
                    self._check_game_end()

    def _check_game_end(self) -> None:
        """Handle end-of-game transitions and persistence."""
        if self.board.status in (GameStatus.WON, GameStatus.LOST):
            final_time = self.timer.stop()
            mode_key = "custom" if self.custom_config else self.mode_name.lower()
            won = (self.board.status == GameStatus.WON)
            self.is_new_best = self.records.record_game(
                mode=mode_key,
                won=won,
                elapsed_seconds=final_time,
                custom_config=self.custom_config,
            )
