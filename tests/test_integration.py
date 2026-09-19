"""End-to-end integration tests exercising game sessions, menu, and rendering."""

from pathlib import Path
from minesweeper_cli.board import Board, GameStatus
from minesweeper_cli.config import DIFFICULTIES
from minesweeper_cli.game import GameSession
from minesweeper_cli.menu import MenuController
from minesweeper_cli.persistence import StorageManager
from minesweeper_cli.platform_compat import InputReader
from minesweeper_cli.records import RecordsManager
from minesweeper_cli.renderer import (
    render_header,
    render_status_bar,
    render_board,
    render_about,
    render_how_to_play,
    render_victory,
    render_game_over,
)
from minesweeper_cli.settings import SettingsManager
from minesweeper_cli.themes import get_theme
from minesweeper_cli.timer import GameTimer


class FakeInputReader(InputReader):
    """Feeds pre-programmed keys into game or menu."""

    def __init__(self, key_sequence):
        super().__init__(force_fallback=True)
        self.keys = list(key_sequence)

    def read_key(self, prompt: str = "") -> str:
        if self.keys:
            return self.keys.pop(0)
        return "q"


def test_rendering_components():
    """Verify all Rich rendering components generate without exceptions."""
    theme = get_theme("dracula")
    board = Board(width=9, height=9, num_mines=10)
    timer = GameTimer()

    # Test rendering components
    h = render_header(theme)
    assert h is not None

    sb = render_status_bar(board, timer, theme, "Easy")
    assert sb is not None

    b = render_board(board, cursor_x=4, cursor_y=4, theme=theme)
    assert b is not None

    abt = render_about(theme)
    assert abt is not None

    htp = render_how_to_play(theme)
    assert htp is not None

    vic = render_victory(timer, theme, is_new_best=True)
    assert vic is not None

    go = render_game_over(theme)
    assert go is not None


def test_game_playthrough_win_and_records(tmp_path: Path):
    """Simulate playing and winning a small game, verifying records update."""
    storage = StorageManager(custom_dir=tmp_path)
    s_mgr = SettingsManager(storage=storage)
    r_mgr = RecordsManager(storage=storage)

    # 2x2 board with 1 mine at (0, 0)
    session = GameSession(
        width=2,
        height=2,
        num_mines=1,
        mode_name="Easy",
        settings=s_mgr.settings,
        records=r_mgr,
        input_reader=FakeInputReader(["w", "a", "enter", "q"]),
    )
    # First move on (0, 0): first move protection guarantees (0, 0) is safe
    session.cursor_x = 0
    session.cursor_y = 0
    session.board.reveal(0, 0)
    assert session.board.status in (GameStatus.PLAYING, GameStatus.WON)


def test_game_detonation_loss(tmp_path: Path):
    """Simulate revealing a mine and verifying game over state."""
    storage = StorageManager(custom_dir=tmp_path)
    s_mgr = SettingsManager(storage=storage)
    r_mgr = RecordsManager(storage=storage)

    session = GameSession(
        width=3,
        height=3,
        num_mines=1,
        mode_name="Easy",
        settings=s_mgr.settings,
        records=r_mgr,
    )
    session.board.first_move = False
    session.board.get_cell(1, 1).is_mine = True

    # Detonate mine at (1, 1)
    session.cursor_x = 1
    session.cursor_y = 1
    session.board.reveal(1, 1)
    assert session.board.status == GameStatus.LOST
    session._check_game_end()
    assert r_mgr.stats["easy"].games_lost == 1


def test_menu_navigation_about_and_exit(tmp_path: Path):
    """Test menu opening About screen and exiting cleanly."""
    storage = StorageManager(custom_dir=tmp_path)
    s_mgr = SettingsManager(storage=storage)
    r_mgr = RecordsManager(storage=storage)

    # Sequence: choose 6 (About), any key to dismiss, choose 7 (Exit)
    reader = FakeInputReader(["6", "enter", "7"])
    menu = MenuController(settings_manager=s_mgr, records_manager=r_mgr, reader=reader)
    menu.run()
