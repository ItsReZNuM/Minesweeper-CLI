"""Minesweeper board engine and gameplay mechanics."""

import random
from enum import Enum, auto
from typing import List, Tuple, Set, Optional
from minesweeper_cli.cell import Cell


class GameStatus(Enum):
    """Lifecycle states of a Minesweeper game."""
    READY = auto()      # Board created, first move not yet taken
    PLAYING = auto()    # Game active, timer ticking
    WON = auto()        # All non-mine cells revealed
    LOST = auto()       # Mine triggered


class Board:
    """Core Minesweeper game board."""

    def __init__(self, width: int, height: int, num_mines: int) -> None:
        if width < 1 or height < 1:
            raise ValueError("Board dimensions must be at least 1x1")
        total_cells = width * height
        if num_mines < 0 or num_mines >= total_cells:
            raise ValueError(f"Mines ({num_mines}) must be between 0 and {total_cells - 1}")

        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.grid: List[List[Cell]] = [[Cell() for _ in range(width)] for _ in range(height)]
        self.status = GameStatus.READY
        self.first_move = True
        self.revealed_count = 0
        self.flagged_count = 0
        self.exploded_pos: Optional[Tuple[int, int]] = None

    def in_bounds(self, x: int, y: int) -> bool:
        """Check if grid coordinates (x=column, y=row) are within board bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Cell:
        """Get cell at coordinates (x, y)."""
        if not self.in_bounds(x, y):
            raise IndexError(f"Coordinates ({x}, {y}) out of bounds")
        return self.grid[y][x]

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Return list of (nx, ny) coordinates for all valid adjacent neighbors."""
        neighbors = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    neighbors.append((nx, ny))
        return neighbors

    def place_mines(self, safe_x: int, safe_y: int) -> None:
        """Generate mines with first-move protection ensuring safe_x, safe_y is safe."""
        # Prefer guaranteeing safe_x, safe_y and its 8 neighbors have no mines if space permits
        forbidden: Set[Tuple[int, int]] = {(safe_x, safe_y)}
        neighbors = self.get_neighbors(safe_x, safe_y)
        total_cells = self.width * self.height

        if total_cells - (len(neighbors) + 1) >= self.num_mines:
            forbidden.update(neighbors)

        candidates = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in forbidden
        ]

        # If candidates are fewer than required mines (dense custom board), fall back to only safe cell
        if len(candidates) < self.num_mines:
            candidates = [
                (x, y)
                for y in range(self.height)
                for x in range(self.width)
                if (x, y) != (safe_x, safe_y)
            ]

        mine_coords = set(random.sample(candidates, self.num_mines))

        for x, y in mine_coords:
            self.grid[y][x].is_mine = True

        # Calculate neighbor mine counts for each cell
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].is_mine:
                    continue
                count = sum(1 for nx, ny in self.get_neighbors(x, y) if self.grid[ny][nx].is_mine)
                self.grid[y][x].adjacent_mines = count

    def reveal(self, x: int, y: int) -> bool:
        """Reveal cell at (x, y). Returns True if action succeeded."""
        if not self.in_bounds(x, y) or self.status in (GameStatus.WON, GameStatus.LOST):
            return False

        cell = self.grid[y][x]
        if not cell.can_reveal:
            return False

        # First move protection: generate mine layout ensuring first reveal is safe
        if self.first_move:
            self.place_mines(x, y)
            self.first_move = False
            self.status = GameStatus.PLAYING

        if cell.is_mine:
            cell.is_exploded = True
            self.exploded_pos = (x, y)
            self.status = GameStatus.LOST
            self._reveal_all_mines()
            return True

        # Flood fill reveal
        self._flood_reveal(x, y)
        self._check_win_condition()
        return True

    def _flood_reveal(self, start_x: int, start_y: int) -> None:
        """Breadth-first search expanding zero-neighbor cells and boundary numbers."""
        queue: List[Tuple[int, int]] = [(start_x, start_y)]
        visited: Set[Tuple[int, int]] = set()

        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            cell = self.grid[cy][cx]
            if cell.is_mine:
                continue

            if not cell.is_revealed and not cell.is_flagged:
                cell.is_revealed = True
                self.revealed_count += 1

                if cell.adjacent_mines == 0:
                    for nx, ny in self.get_neighbors(cx, cy):
                        if (nx, ny) not in visited:
                            neighbor_cell = self.grid[ny][nx]
                            if not neighbor_cell.is_revealed and not neighbor_cell.is_flagged and not neighbor_cell.is_mine:
                                queue.append((nx, ny))

    def chord_reveal(self, x: int, y: int) -> bool:
        """Reveal surrounding unflagged cells if flagged neighbor count matches cell number."""
        if not self.in_bounds(x, y) or self.status != GameStatus.PLAYING:
            return False

        cell = self.grid[y][x]
        if not cell.is_revealed or cell.adjacent_mines == 0:
            return False

        neighbors = self.get_neighbors(x, y)
        flagged_neighbors = sum(1 for nx, ny in neighbors if self.grid[ny][nx].is_flagged)

        if flagged_neighbors != cell.adjacent_mines:
            return False

        any_revealed = False
        for nx, ny in neighbors:
            n_cell = self.grid[ny][nx]
            if not n_cell.is_revealed and not n_cell.is_flagged:
                if n_cell.is_mine:
                    n_cell.is_exploded = True
                    self.exploded_pos = (nx, ny)
                    self.status = GameStatus.LOST
                    self._reveal_all_mines()
                    return True
                self._flood_reveal(nx, ny)
                any_revealed = True

        self._check_win_condition()
        return any_revealed

    def toggle_flag(self, x: int, y: int) -> bool:
        """Toggle flag marker on hidden cell (x, y)."""
        if not self.in_bounds(x, y) or self.status in (GameStatus.WON, GameStatus.LOST):
            return False

        cell = self.grid[y][x]
        if cell.is_revealed:
            return False

        if cell.is_flagged:
            cell.is_flagged = False
            self.flagged_count -= 1
        else:
            cell.is_flagged = True
            self.flagged_count += 1

        return True

    def _check_win_condition(self) -> None:
        """Check if all non-mine cells have been opened."""
        total_cells = self.width * self.height
        non_mine_cells = total_cells - self.num_mines
        if self.revealed_count == non_mine_cells and self.status != GameStatus.LOST:
            self.status = GameStatus.WON
            # Auto-flag remaining hidden mines for polished display
            for y in range(self.height):
                for x in range(self.width):
                    c = self.grid[y][x]
                    if c.is_mine and not c.is_flagged:
                        c.is_flagged = True
                        self.flagged_count += 1

    def _reveal_all_mines(self) -> None:
        """Expose mine positions on game loss."""
        for y in range(self.height):
            for x in range(self.width):
                c = self.grid[y][x]
                if c.is_mine:
                    c.is_revealed = True

    @property
    def remaining_flags(self) -> int:
        """Count of flags remaining relative to total mines."""
        return self.num_mines - self.flagged_count
