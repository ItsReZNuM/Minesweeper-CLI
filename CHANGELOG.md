# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2026-09-19

### Fixed
- **Fixed Cell Dimension Stability**: Guaranteed fixed terminal display widths across all tile states (numbers, flags, mines, explosions) using locked table columns and `cell_len` padding, preventing board misalignment and distortion when placing flags or revealing mines.
- **Clean Terminal Exit**: Added automatic terminal clearing on quit/exit so game panels are not left sitting in the terminal buffer when returning to the shell prompt.
- **Single-Width Safe Glyphs**: Standardized theme symbols to clean, monospace-safe glyphs for flawless alignment across Windows CMD, PowerShell, Linux, and Termux.

## [0.2.2] - 2026-09-19

### Added
- Rich interactive Terminal User Interface (TUI) with responsive styling.
- 7 distinct color themes: Classic, Ocean, Matrix, Dracula, Cyberpunk, Nord, and Monochrome.
- Traditional Minesweeper engine with first-move protection guaranteeing a safe initial cell.
- Predefined difficulty levels: Easy (9x9), Medium (16x16), Hard (30x16), and Expert (30x24).
- Custom game mode with interactive dimension and mine count validation.
- Responsive board viewport scrolling for smaller terminals, phones, and Termux on Android.
- Cross-platform single-key input (`readchar`) with seamless fallback to line/command input mode.
- Fully customizable keybindings with collision validation and default reset.
- Persistent high scores, best completion times, and statistics per difficulty.
- Custom game statistics tracking.
- Dedicated "About the Creator" screen and comprehensive "How to Play" guide.
- CLI flags support: `--difficulty`, `--custom`, `--theme`, `--version`, and `--help`.
- Automated test suite covering board logic, game loop, persistence, settings, and CLI.
- GitHub Actions CI matrix for tests across Windows, Linux, and macOS.

## [0.2.0] - 2026-08-15
- Prototype terminal board rendering.
- Basic cell reveal and flag mechanics.

## [0.1.0] - 2026-07-01
- Initial core engine proof-of-concept.
