"""Unit tests for RecordsManager and player statistics."""

from pathlib import Path
from minesweeper_cli.persistence import StorageManager
from minesweeper_cli.records import RecordsManager


def test_records_tracking_and_new_best(tmp_path: Path):
    """Test updating records and detecting new best completion times."""
    storage = StorageManager(custom_dir=tmp_path)
    records = RecordsManager(storage=storage)

    # Record first win on Easy (45.5s)
    is_best = records.record_game(mode="easy", won=True, elapsed_seconds=45.5)
    assert is_best is True
    stat = records.stats["easy"]
    assert stat.games_won == 1
    assert stat.games_played == 1
    assert stat.best_time == 45.5

    # Record slower win on Easy (60.0s)
    is_best_2 = records.record_game(mode="easy", won=True, elapsed_seconds=60.0)
    assert is_best_2 is False
    assert stat.best_time == 45.5
    assert stat.games_won == 2
    assert stat.games_played == 2

    # Record faster win on Easy (30.2s)
    is_best_3 = records.record_game(mode="easy", won=True, elapsed_seconds=30.2)
    assert is_best_3 is True
    assert stat.best_time == 30.2
    assert stat.games_won == 3


def test_records_losses(tmp_path: Path):
    """Ensure losses increment loss count without updating best time."""
    storage = StorageManager(custom_dir=tmp_path)
    records = RecordsManager(storage=storage)

    records.record_game(mode="hard", won=False, elapsed_seconds=12.0)
    stat = records.stats["hard"]
    assert stat.games_lost == 1
    assert stat.games_won == 0
    assert stat.games_played == 1
    assert stat.best_time is None


def test_custom_game_records(tmp_path: Path):
    """Verify custom games are isolated from predefined difficulties."""
    storage = StorageManager(custom_dir=tmp_path)
    records = RecordsManager(storage=storage)

    custom_cfg = (20, 15, 30)
    is_best = records.record_game(mode="custom", won=True, elapsed_seconds=95.0, custom_config=custom_cfg)
    assert is_best is True
    key = "20x15_30m"
    assert key in records.custom_stats
    cstat = records.custom_stats[key]
    assert cstat["best_time"] == 95.0
    assert cstat["games_won"] == 1


def test_records_persistence_and_reset(tmp_path: Path):
    """Test reload from storage and resetting records."""
    storage = StorageManager(custom_dir=tmp_path)
    records = RecordsManager(storage=storage)

    records.record_game(mode="medium", won=True, elapsed_seconds=120.0)

    # Reload in new instance
    records2 = RecordsManager(storage=storage)
    assert records2.stats["medium"].best_time == 120.0
    assert records2.stats["medium"].games_won == 1

    # Reset all records
    records2.reset_all_records()
    assert records2.stats["medium"].best_time is None
    assert records2.stats["medium"].games_won == 0
    assert len(records2.custom_stats) == 0
