"""User settings manager with persistence and fallback recovery."""

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from minesweeper_cli.controls import DEFAULT_KEY_BINDINGS, validate_key_bindings
from minesweeper_cli.persistence import StorageManager, default_storage

SETTINGS_FILENAME = "settings.json"


@dataclass
class Settings:
    """Configurable player preferences."""
    theme: str = "classic"
    key_bindings: Dict[str, List[str]] = field(
        default_factory=lambda: copy.deepcopy(DEFAULT_KEY_BINDINGS)
    )
    show_timer: bool = True
    show_coords: bool = True
    compact_mode: bool = False
    use_unicode: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize settings to JSON-compatible dictionary."""
        return {
            "theme": self.theme,
            "key_bindings": self.key_bindings,
            "show_timer": self.show_timer,
            "show_coords": self.show_coords,
            "compact_mode": self.compact_mode,
            "use_unicode": self.use_unicode,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """Instantiate Settings from dictionary with safe fallbacks."""
        if not isinstance(data, dict):
            return cls()

        theme = str(data.get("theme", "classic"))
        raw_keys = data.get("key_bindings")
        if isinstance(raw_keys, dict):
            is_valid, _ = validate_key_bindings(raw_keys)
            key_bindings = raw_keys if is_valid else copy.deepcopy(DEFAULT_KEY_BINDINGS)
        else:
            key_bindings = copy.deepcopy(DEFAULT_KEY_BINDINGS)

        return cls(
            theme=theme,
            key_bindings=key_bindings,
            show_timer=bool(data.get("show_timer", True)),
            show_coords=bool(data.get("show_coords", True)),
            compact_mode=bool(data.get("compact_mode", False)),
            use_unicode=bool(data.get("use_unicode", True)),
        )


class SettingsManager:
    """Manages loading, updating, and saving user settings."""

    def __init__(self, storage: Optional[StorageManager] = None) -> None:
        self.storage = storage or default_storage
        self.settings = self.load()

    def load(self) -> Settings:
        """Load settings from disk or return default settings."""
        data = self.storage.load_json(SETTINGS_FILENAME, default=None)
        if data is None:
            settings = Settings()
            self.save(settings)
            return settings
        return Settings.from_dict(data)

    def save(self, settings: Optional[Settings] = None) -> bool:
        """Persist current or provided settings to disk."""
        if settings is not None:
            self.settings = settings
        return self.storage.save_json(SETTINGS_FILENAME, self.settings.to_dict())

    def reset_to_defaults(self) -> None:
        """Reset all configuration to factory defaults and persist."""
        self.settings = Settings()
        self.save()

    def reset_key_bindings(self) -> None:
        """Reset only key bindings to factory defaults."""
        self.settings.key_bindings = copy.deepcopy(DEFAULT_KEY_BINDINGS)
        self.save()
