"""Unit tests for GameSession and viewport calculation."""

from pathlib import Path
from minesweeper_cli.board import GameStatus
from minesweeper_cli.game import GameSession
from minesweeper_cli.persistence import StorageManager
from minesweeper_cli.platform_compat import InputReader
from minesweeper_cli.records import RecordsManager
from minesweeper_cli.settings import SettingsManager


def test_game_session_initialization(tmp_path: Path):
    """Test GameSession attributes and initial cursor position."""
    storage = StorageManager(custom_dir=tmp_path)
    s_mgr = SettingsManager(storage=storage)
    r_mgr = RecordsManager(storage=storage)

    session = GameSession(
        width=10,
        height=10,
        num_mines=15,
        mode_name="Custom",
        settings=s_mgr.settings,
        records=r_mgr,
    )
    assert session.width == 10
    assert session.height == 10
    assert session.num_mines == 15
    assert session.cursor_x == 5
    assert session.cursor_y == 5
    assert session.board.status == GameStatus.READY


def test_viewport_calculation_large_terminal(tmp_path: Path):
    """On a wide terminal, the entire board should be visible in viewport."""
    storage = StorageManager(custom_dir=tmp_path)
    s_mgr = SettingsManager(storage=storage)
    r_mgr = RecordsManager(storage=storage)

    session = GameSession(
        width=10,
        height=10,
        num_mines=10,
        mode_name="Test",
        settings=s_mgr.settings,
        records=r_mgr,
    )
    min_x, max_x, min_y, max_y = session._calculate_viewport(cols=120, lines=40)
    assert min_x == 0
    assert max_x == 10
    assert min_y == 0
    assert max_y == 10


def test_viewport_calculation_small_terminal(tmp_path: Path):
    """On a narrow terminal (e.g. mobile/Termux), viewport should slice around cursor."""
    storage = StorageManager(custom_dir=tmp_path)
    s_mgr = SettingsManager(storage=storage)
    r_mgr = RecordsManager(storage=storage)

    session = GameSession(
        width=30,
        height=20,
        num_mines=50,
        mode_name="Expert",
        settings=s_mgr.settings,
        records=r_mgr,
    )
    session.cursor_x = 15
    session.cursor_y = 10

    min_x, max_x, min_y, max_y = session._calculate_viewport(cols=40, lines=15)
    # Viewport width and height must be strictly less than board dimensions
    assert max_x - min_x < session.width
    assert max_y - min_y < session.height
    # Cursor should be contained within visible range
    assert min_x <= session.cursor_x < max_x
    assert min_y <= session.cursor_y < max_y


def test_fallback_command_parsing(tmp_path: Path):
    """Test parsing commands in line fallback mode."""
    storage = StorageManager(custom_dir=tmp_path)
    s_mgr = SettingsManager(storage=storage)
    r_mgr = RecordsManager(storage=storage)

    session = GameSession(
        width=10,
        height=10,
        num_mines=10,
        mode_name="Test",
        settings=s_mgr.settings,
        records=r_mgr,
    )
    # Coordinate command 'r 3 4' should reposition cursor and trigger reveal
    act = session._handle_fallback_command("r 3 4")
    assert act == "reveal"
    assert session.cursor_x == 3
    assert session.cursor_y == 4

    # Direct flag coordinate 'f 5 6'
    act2 = session._handle_fallback_command("f 5 6")
    assert act2 == "flag"
    assert session.cursor_x == 5
    assert session.cursor_y == 6
