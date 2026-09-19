"""Unit tests for Minesweeper board engine and gameplay mechanics."""

import pytest
from minesweeper_cli.board import Board, GameStatus


def test_board_initialization():
    """Verify board creation and default status."""
    board = Board(width=9, height=9, num_mines=10)
    assert board.width == 9
    assert board.height == 9
    assert board.num_mines == 10
    assert board.status == GameStatus.READY
    assert board.first_move is True
    assert board.revealed_count == 0
    assert board.flagged_count == 0
    assert board.remaining_flags == 10


def test_board_invalid_initialization():
    """Verify exceptions on zero/negative dimensions or impossible mine counts."""
    with pytest.raises(ValueError):
        Board(width=0, height=5, num_mines=2)
    with pytest.raises(ValueError):
        Board(width=5, height=0, num_mines=2)
    with pytest.raises(ValueError):
        Board(width=5, height=5, num_mines=25)  # Can't have >= total cells
    with pytest.raises(ValueError):
        Board(width=5, height=5, num_mines=-1)


def test_bounds_checking():
    """Test in_bounds coordinate validator."""
    board = Board(width=5, height=8, num_mines=3)
    assert board.in_bounds(0, 0) is True
    assert board.in_bounds(4, 7) is True
    assert board.in_bounds(-1, 0) is False
    assert board.in_bounds(0, -1) is False
    assert board.in_bounds(5, 5) is False
    assert board.in_bounds(2, 8) is False


def test_first_move_protection():
    """Ensure first reveal is never a mine and places mines correctly."""
    board = Board(width=9, height=9, num_mines=10)
    start_x, start_y = 4, 4

    # First reveal should succeed
    success = board.reveal(start_x, start_y)
    assert success is True
    assert board.first_move is False
    assert board.status == GameStatus.PLAYING

    # Cell clicked must not be a mine
    cell = board.get_cell(start_x, start_y)
    assert cell.is_mine is False
    assert cell.is_revealed is True

    # Count total mines actually placed on board
    actual_mines = sum(
        1
        for y in range(board.height)
        for x in range(board.width)
        if board.get_cell(x, y).is_mine
    )
    assert actual_mines == 10


def test_neighbor_counting():
    """Test adjacent mine calculation with manually placed mines."""
    board = Board(width=3, height=3, num_mines=0)
    board.first_move = False
    board.status = GameStatus.PLAYING

    # Place a mine at (0, 0) and (2, 2)
    board.get_cell(0, 0).is_mine = True
    board.get_cell(2, 2).is_mine = True

    # Recalculate numbers
    for y in range(board.height):
        for x in range(board.width):
            if not board.get_cell(x, y).is_mine:
                count = sum(1 for nx, ny in board.get_neighbors(x, y) if board.get_cell(nx, ny).is_mine)
                board.get_cell(x, y).adjacent_mines = count

    # Center cell (1, 1) touches both mines
    assert board.get_cell(1, 1).adjacent_mines == 2
    # Cell (0, 1) touches (0, 0)
    assert board.get_cell(0, 1).adjacent_mines == 1
    # Cell (2, 0) touches neither
    assert board.get_cell(2, 0).adjacent_mines == 0


def test_flood_reveal():
    """Verify zero-neighbor cells expand recursively."""
    board = Board(width=5, height=5, num_mines=0)
    board.first_move = False
    board.status = GameStatus.PLAYING
    # No mines, so revealing any cell reveals the entire board
    board.reveal(2, 2)
    assert board.revealed_count == 25
    assert board.status == GameStatus.WON


def test_flag_functionality():
    """Test toggling flags, flag counters, and reveal protection."""
    board = Board(width=5, height=5, num_mines=3)
    board.first_move = False
    board.status = GameStatus.PLAYING

    # Flag cell (1, 1)
    assert board.toggle_flag(1, 1) is True
    assert board.get_cell(1, 1).is_flagged is True
    assert board.flagged_count == 1
    assert board.remaining_flags == 2

    # Attempting to reveal a flagged cell should fail and not reveal it
    assert board.reveal(1, 1) is False
    assert board.get_cell(1, 1).is_revealed is False

    # Unflag cell (1, 1)
    assert board.toggle_flag(1, 1) is True
    assert board.get_cell(1, 1).is_flagged is False
    assert board.flagged_count == 0
    assert board.remaining_flags == 3

    # Now cell can be revealed
    assert board.reveal(1, 1) is True
    assert board.get_cell(1, 1).is_revealed is True

    # Revealed cell cannot be flagged
    assert board.toggle_flag(1, 1) is False


def test_loss_condition():
    """Test detonating a mine transitions board to LOST and exposes mines."""
    board = Board(width=3, height=3, num_mines=1)
    board.first_move = False
    board.status = GameStatus.PLAYING
    mine_cell = board.get_cell(1, 1)
    mine_cell.is_mine = True

    # Reveal mine
    res = board.reveal(1, 1)
    assert res is True
    assert board.status == GameStatus.LOST
    assert mine_cell.is_exploded is True
    assert board.exploded_pos == (1, 1)
    assert mine_cell.is_revealed is True


def test_win_condition():
    """Test revealing all non-mine cells achieves WON state and auto-flags remaining mines."""
    board = Board(width=2, height=2, num_mines=1)
    board.first_move = False
    board.status = GameStatus.PLAYING
    board.get_cell(0, 0).is_mine = True
    board.get_cell(1, 0).adjacent_mines = 1
    board.get_cell(0, 1).adjacent_mines = 1
    board.get_cell(1, 1).adjacent_mines = 1

    # Reveal other 3 cells
    board.reveal(1, 0)
    board.reveal(0, 1)
    board.reveal(1, 1)

    assert board.status == GameStatus.WON
    # Check auto-flag on remaining mine
    assert board.get_cell(0, 0).is_flagged is True


def test_chord_reveal():
    """Test chord reveal opens unflagged neighbors when flags match adjacent count."""
    board = Board(width=3, height=3, num_mines=1)
    board.first_move = False
    board.status = GameStatus.PLAYING

    # Place mine at (0, 0)
    board.get_cell(0, 0).is_mine = True
    board.get_cell(1, 1).is_revealed = True
    board.get_cell(1, 1).adjacent_mines = 1

    # Flag the mine correctly
    board.toggle_flag(0, 0)

    # Chord reveal on (1, 1) should reveal all other 7 neighbors
    chords = board.chord_reveal(1, 1)
    assert chords is True
    for y in range(3):
        for x in range(3):
            if (x, y) != (0, 0):
                assert board.get_cell(x, y).is_revealed is True
