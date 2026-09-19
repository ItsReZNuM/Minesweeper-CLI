"""Minesweeper individual cell representation."""

from dataclasses import dataclass


@dataclass
class Cell:
    """Represents a single tile on the Minesweeper board."""
    is_mine: bool = False
    is_revealed: bool = False
    is_flagged: bool = False
    is_exploded: bool = False
    adjacent_mines: int = 0

    @property
    def is_hidden(self) -> bool:
        """Return True if the cell has not yet been opened."""
        return not self.is_revealed

    @property
    def can_reveal(self) -> bool:
        """A cell can only be revealed if it is hidden and not flagged."""
        return not self.is_revealed and not self.is_flagged

    def toggle_flag(self) -> bool:
        """Toggle flag status if hidden. Returns True if now flagged, False otherwise."""
        if self.is_revealed:
            return False
        self.is_flagged = not self.is_flagged
        return self.is_flagged
