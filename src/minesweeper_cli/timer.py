"""Gameplay timer tracking duration accurately without busy loops."""

import time
from typing import Optional


class GameTimer:
    """Timer tracking gameplay duration in seconds."""

    def __init__(self) -> None:
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._accumulated: float = 0.0
        self._running: bool = False

    def start(self) -> None:
        """Start or resume the timer."""
        if not self._running:
            self._start_time = time.monotonic()
            self._running = True

    def stop(self) -> float:
        """Stop the timer and return the final elapsed seconds."""
        if self._running and self._start_time is not None:
            self._accumulated += time.monotonic() - self._start_time
            self._running = False
            self._end_time = time.monotonic()
        return self.elapsed_seconds

    def reset(self) -> None:
        """Reset the timer to 0."""
        self._start_time = None
        self._end_time = None
        self._accumulated = 0.0
        self._running = False

    @property
    def is_running(self) -> bool:
        """Whether the timer is actively running."""
        return self._running

    @property
    def elapsed_seconds(self) -> float:
        """Total elapsed seconds."""
        if self._running and self._start_time is not None:
            return self._accumulated + (time.monotonic() - self._start_time)
        return self._accumulated

    def formatted(self) -> str:
        """Return formatted string MM:SS (or HH:MM:SS if over 1 hour)."""
        total = int(self.elapsed_seconds)
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
