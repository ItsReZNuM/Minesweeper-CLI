"""Safe, cross-platform persistence layer using platformdirs with atomic writes."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional
from platformdirs import user_data_dir
from minesweeper_cli.config import APP_SLUG, AUTHOR


class StorageManager:
    """Handles loading and saving configuration and records safely."""

    def __init__(self, custom_dir: Optional[Path] = None) -> None:
        if custom_dir is not None:
            self.data_dir = Path(custom_dir)
        else:
            self.data_dir = Path(user_data_dir(appname=APP_SLUG, appauthor="ItsReZNuM"))
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Create storage directory if not present."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Fallback to local user home directory if OS permission fails
            fallback = Path.home() / f".{APP_SLUG}"
            fallback.mkdir(parents=True, exist_ok=True)
            self.data_dir = fallback

    def get_file_path(self, filename: str) -> Path:
        """Return full path for a file in the data directory."""
        return self.data_dir / filename

    def load_json(self, filename: str, default: Any) -> Any:
        """Safely load JSON data. Returns default on missing or corrupted file."""
        file_path = self.get_file_path(filename)
        if not file_path.exists():
            return default

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Backup corrupted file to prevent silent complete data loss
            try:
                bak_path = file_path.with_suffix(".bak")
                if file_path.exists():
                    os.replace(file_path, bak_path)
            except OSError:
                pass
            return default

    def save_json(self, filename: str, data: Any) -> bool:
        """Safely write JSON using atomic replace to prevent corrupt files on abort."""
        file_path = self.get_file_path(filename)
        self._ensure_dir()

        try:
            # Write to a temp file in the same directory so os.replace is atomic across filesystems
            with tempfile.NamedTemporaryFile(
                "w",
                dir=str(self.data_dir),
                delete=False,
                encoding="utf-8"
            ) as tf:
                json.dump(data, tf, indent=2, ensure_ascii=False)
                temp_name = tf.name

            os.replace(temp_name, file_path)
            return True
        except OSError:
            if "temp_name" in locals() and os.path.exists(temp_name):
                try:
                    os.remove(temp_name)
                except OSError:
                    pass
            return False


# Global default storage instance
default_storage = StorageManager()
