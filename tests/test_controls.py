"""Unit tests for controls, key normalization, and conflict validation."""

from minesweeper_cli.controls import (
    DEFAULT_KEY_BINDINGS,
    ALL_ACTIONS,
    ACTION_UP,
    ACTION_DOWN,
    ACTION_REVEAL,
    ACTION_FLAG,
    normalize_key,
    validate_key_bindings,
    get_action_for_key,
)


def test_default_key_bindings_validity():
    """Ensure default controls pass validation without conflicts."""
    valid, err = validate_key_bindings(DEFAULT_KEY_BINDINGS)
    assert valid is True
    assert err is None


def test_key_normalization():
    """Verify normalization of whitespace, casing, and special keys."""
    assert normalize_key("  W  ") == "w"
    assert normalize_key("\r") == "enter"
    assert normalize_key("\n") == "enter"
    assert normalize_key(" ") == "space"
    assert normalize_key("\x1b") == "escape"
    assert normalize_key("ESC") == "escape"


def test_conflict_detection():
    """Ensure binding the same key to two actions is rejected."""
    bad_bindings = dict(DEFAULT_KEY_BINDINGS)
    # Assign 'w' (which is in UP) to DOWN as well
    bad_bindings[ACTION_DOWN] = ["w"]
    valid, err = validate_key_bindings(bad_bindings)
    assert valid is False
    assert err is not None
    assert "conflicts" in err


def test_missing_action_detection():
    """Ensure every action must have at least one assigned key."""
    incomplete = dict(DEFAULT_KEY_BINDINGS)
    incomplete[ACTION_FLAG] = []
    valid, err = validate_key_bindings(incomplete)
    assert valid is False
    assert err is not None
    assert "must have at least one key" in err


def test_action_resolution():
    """Verify keys map to correct actions."""
    assert get_action_for_key("w", DEFAULT_KEY_BINDINGS) == ACTION_UP
    assert get_action_for_key("W", DEFAULT_KEY_BINDINGS) == ACTION_UP
    assert get_action_for_key("enter", DEFAULT_KEY_BINDINGS) == ACTION_REVEAL
    assert get_action_for_key("\r", DEFAULT_KEY_BINDINGS) == ACTION_REVEAL
    assert get_action_for_key("f", DEFAULT_KEY_BINDINGS) == ACTION_FLAG
    assert get_action_for_key("unknown_key", DEFAULT_KEY_BINDINGS) is None
