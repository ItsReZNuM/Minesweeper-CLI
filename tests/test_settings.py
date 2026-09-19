"""Unit tests for Settings and SettingsManager."""

import json
from pathlib import Path
from minesweeper_cli.persistence import StorageManager
from minesweeper_cli.settings import Settings, SettingsManager
from minesweeper_cli.controls import DEFAULT_KEY_BINDINGS, ACTION_UP


def test_settings_serialization():
    """Verify dictionary conversion round-trip."""
    s = Settings(theme="matrix", show_timer=False, show_coords=False)
    data = s.to_dict()
    assert data["theme"] == "matrix"
    assert data["show_timer"] is False
    assert data["show_coords"] is False

    loaded = Settings.from_dict(data)
    assert loaded.theme == "matrix"
    assert loaded.show_timer is False
    assert loaded.show_coords is False


def test_settings_invalid_dict_fallback():
    """Ensure invalid dictionary yields safe defaults."""
    loaded = Settings.from_dict({"key_bindings": "not_a_dict"})
    assert loaded.theme == "classic"
    assert loaded.key_bindings == DEFAULT_KEY_BINDINGS


def test_settings_manager_save_and_load(tmp_path: Path):
    """Test saving to and loading from custom temporary directory."""
    storage = StorageManager(custom_dir=tmp_path)
    manager = SettingsManager(storage=storage)

    manager.settings.theme = "nord"
    manager.settings.show_timer = False
    manager.save()

    # Re-instantiate from the same storage
    manager2 = SettingsManager(storage=storage)
    assert manager2.settings.theme == "nord"
    assert manager2.settings.show_timer is False


def test_settings_corrupted_file_recovery(tmp_path: Path):
    """Ensure corrupted JSON file does not crash and restores defaults."""
    storage = StorageManager(custom_dir=tmp_path)
    file_path = storage.get_file_path("settings.json")
    file_path.write_text("{ corrupt json !!", encoding="utf-8")

    manager = SettingsManager(storage=storage)
    assert manager.settings.theme == "classic"


def test_settings_resets(tmp_path: Path):
    """Test reset_key_bindings and reset_to_defaults."""
    storage = StorageManager(custom_dir=tmp_path)
    manager = SettingsManager(storage=storage)

    manager.settings.theme = "cyberpunk"
    manager.settings.key_bindings[ACTION_UP] = ["i"]
    manager.save()

    manager.reset_key_bindings()
    assert manager.settings.key_bindings[ACTION_UP] == DEFAULT_KEY_BINDINGS[ACTION_UP]
    assert manager.settings.theme == "cyberpunk"

    manager.reset_to_defaults()
    assert manager.settings.theme == "classic"
