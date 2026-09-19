"""Unit tests for CLI arguments parser and flags."""

import pytest
from minesweeper_cli import __version__
from minesweeper_cli.cli import create_parser


def test_cli_version(capsys):
    """Verify --version returns application name and version."""
    parser = create_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert f"Minesweeper CLI {__version__}" in captured.out


def test_cli_help(capsys):
    """Verify --help displays usage and available arguments."""
    parser = create_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "minesweeper" in captured.out
    assert "--difficulty" in captured.out
    assert "--custom" in captured.out
    assert "--theme" in captured.out


def test_cli_difficulty_argument():
    """Verify --difficulty parsing with valid and invalid options."""
    parser = create_parser()
    args = parser.parse_args(["--difficulty", "expert"])
    assert args.difficulty == "expert"

    with pytest.raises(SystemExit):
        parser.parse_args(["--difficulty", "invalid_level"])


def test_cli_theme_argument():
    """Verify --theme option parsing."""
    parser = create_parser()
    args = parser.parse_args(["--theme", "matrix"])
    assert args.theme == "matrix"

    with pytest.raises(SystemExit):
        parser.parse_args(["--theme", "nonexistent_theme"])


def test_cli_custom_flag():
    """Verify --custom boolean flag."""
    parser = create_parser()
    args = parser.parse_args(["--custom"])
    assert args.custom is True
