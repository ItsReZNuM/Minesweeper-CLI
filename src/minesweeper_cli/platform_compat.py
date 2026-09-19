"""Cross-platform input reader, fallback mode, and terminal sizing utilities."""

import os
import shutil
import sys
from typing import Optional, Tuple

try:
    import readchar
    import readchar.key as rkey
    HAS_READCHAR = True
except ImportError:
    HAS_READCHAR = False
    rkey = None


def get_terminal_size(default_cols: int = 80, default_lines: int = 24) -> Tuple[int, int]:
    """Return current terminal dimensions (columns, lines)."""
    try:
        size = shutil.get_terminal_size(fallback=(default_cols, default_lines))
        return size.columns, size.lines
    except Exception:
        return default_cols, default_lines


class InputReader:
    """Reads keyboard input across platforms with seamless fallback to Enter-based prompts."""

    def __init__(self, force_fallback: bool = False) -> None:
        self.fallback_mode = force_fallback or not HAS_READCHAR or not sys.stdin.isatty()
        self._key_map = {}
        if HAS_READCHAR and rkey:
            self._key_map = {
                rkey.UP: "up",
                rkey.DOWN: "down",
                rkey.LEFT: "left",
                rkey.RIGHT: "right",
                rkey.ENTER: "enter",
                rkey.SPACE: "space",
                rkey.ESC: "escape",
                rkey.BACKSPACE: "backspace",
            }
            # Also map alternative enter forms if defined
            if hasattr(rkey, "CR"):
                self._key_map[rkey.CR] = "enter"
            if hasattr(rkey, "LF"):
                self._key_map[rkey.LF] = "enter"

    def read_key(self, prompt: str = "") -> str:
        """Read a single action key or fallback to typed line."""
        if not self.fallback_mode and HAS_READCHAR:
            try:
                raw = readchar.readkey()
                if raw in self._key_map:
                    return self._key_map[raw]
                if len(raw) == 1:
                    return raw.lower()
                return raw.lower()
            except (KeyboardInterrupt, EOFError):
                return "q"
            except Exception:
                # If single-key reading fails in the current terminal, switch to fallback mode
                self.fallback_mode = True

        # Fallback Enter-based input mode
        try:
            display_prompt = prompt or "Command (WASD/Enter/F/C/R/Q) > "
            val = input(display_prompt).strip()
            return val.lower() if val else "enter"
        except (KeyboardInterrupt, EOFError):
            return "q"
