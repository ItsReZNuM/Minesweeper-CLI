"""Player records, best completion times, and gameplay statistics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, Any, Tuple
from minesweeper_cli.config import DIFFICULTIES
from minesweeper_cli.persistence import StorageManager, default_storage

RECORDS_FILENAME = "records.json"


@dataclass
class DifficultyStats:
    """Statistics for a specific difficulty level."""
    best_time: Optional[float] = None
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    last_played: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "best_time": self.best_time,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "games_lost": self.games_lost,
            "last_played": self.last_played,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DifficultyStats":
        if not isinstance(data, dict):
            return cls()
        best_time = data.get("best_time")
        if best_time is not None:
            try:
                best_time = float(best_time)
            except (ValueError, TypeError):
                best_time = None
        return cls(
            best_time=best_time,
            games_played=int(data.get("games_played", 0)),
            games_won=int(data.get("games_won", 0)),
            games_lost=int(data.get("games_lost", 0)),
            last_played=data.get("last_played"),
        )


class RecordsManager:
    """Manages player statistics and best completion times."""

    def __init__(self, storage: Optional[StorageManager] = None) -> None:
        self.storage = storage or default_storage
        self.stats: Dict[str, DifficultyStats] = {}
        self.custom_stats: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        """Load records from storage with fallbacks."""
        data = self.storage.load_json(RECORDS_FILENAME, default={})
        if not isinstance(data, dict):
            data = {}

        self.stats = {}
        for diff_key in DIFFICULTIES.keys():
            diff_data = data.get("difficulties", {}).get(diff_key, {})
            self.stats[diff_key] = DifficultyStats.from_dict(diff_data)

        self.custom_stats = data.get("custom", {})
        if not isinstance(self.custom_stats, dict):
            self.custom_stats = {}

    def save(self) -> bool:
        """Save records to disk."""
        data = {
            "difficulties": {k: v.to_dict() for k, v in self.stats.items()},
            "custom": self.custom_stats,
        }
        return self.storage.save_json(RECORDS_FILENAME, data)

    def record_game(
        self,
        mode: str,
        won: bool,
        elapsed_seconds: float,
        custom_config: Optional[Tuple[int, int, int]] = None,
    ) -> bool:
        """Record game result. Returns True if this completion set a new best time."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        is_new_best = False

        if mode in DIFFICULTIES:
            stat = self.stats.setdefault(mode, DifficultyStats())
            stat.games_played += 1
            stat.last_played = now_str
            if won:
                stat.games_won += 1
                if stat.best_time is None or elapsed_seconds < stat.best_time:
                    stat.best_time = round(elapsed_seconds, 2)
                    is_new_best = True
            else:
                stat.games_lost += 1
        elif mode == "custom" and custom_config:
            w, h, m = custom_config
            key = f"{w}x{h}_{m}m"
            cstat = self.custom_stats.setdefault(
                key,
                {
                    "width": w,
                    "height": h,
                    "mines": m,
                    "best_time": None,
                    "games_played": 0,
                    "games_won": 0,
                    "games_lost": 0,
                    "last_played": now_str,
                },
            )
            cstat["games_played"] += 1
            cstat["last_played"] = now_str
            if won:
                cstat["games_won"] += 1
                prev_best = cstat["best_time"]
                if prev_best is None or elapsed_seconds < prev_best:
                    cstat["best_time"] = round(elapsed_seconds, 2)
                    is_new_best = True
            else:
                cstat["games_lost"] += 1

        self.save()
        return is_new_best

    def reset_all_records(self) -> None:
        """Clear all stored player records and persist empty statistics."""
        self.stats = {k: DifficultyStats() for k in DIFFICULTIES.keys()}
        self.custom_stats = {}
        self.save()
