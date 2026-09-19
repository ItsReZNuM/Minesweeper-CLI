"""Main menu, settings manager, custom board configuration, and navigation."""

from typing import List, Optional, Tuple
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.box import SQUARE, ROUNDED, DOUBLE

from minesweeper_cli.config import (
    APP_NAME,
    DIFFICULTIES,
    MIN_BOARD_WIDTH,
    MAX_BOARD_WIDTH,
    MIN_BOARD_HEIGHT,
    MAX_BOARD_HEIGHT,
    MIN_MINES_COUNT,
)
from minesweeper_cli.controls import (
    ALL_ACTIONS,
    ACTION_LABELS,
    validate_key_bindings,
    normalize_key,
)
from minesweeper_cli.game import GameSession
from minesweeper_cli.platform_compat import InputReader
from minesweeper_cli.records import RecordsManager
from minesweeper_cli.renderer import (
    render_header,
    render_about,
    render_how_to_play,
)
from minesweeper_cli.settings import SettingsManager
from minesweeper_cli.themes import THEMES, get_theme

console = Console()


class MenuController:
    """Controls menu navigation, configuration dialogs, and game launches."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        records_manager: RecordsManager,
        reader: Optional[InputReader] = None,
    ) -> None:
        self.settings_mgr = settings_manager
        self.records_mgr = records_manager
        self.reader = reader or InputReader()

    @property
    def theme(self):
        return get_theme(self.settings_mgr.settings.theme)

    def run(self) -> None:
        """Main loop displaying the top-level menu."""
        menu_items = [
            "Start Game",
            "Custom Game",
            "Settings",
            "Records & Stats",
            "How to Play",
            "About the Creator",
            "Exit",
        ]
        selected_idx = 0

        while True:
            console.clear()
            console.print(render_header(self.theme))

            # Render styled menu panel
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column(justify="left")

            for i, item in enumerate(menu_items):
                prefix = "▶ " if i == selected_idx else "  "
                num_str = f"[{i + 1}] "
                line = Text()
                line.append(prefix, style=f"bold {self.theme.accent_style}")
                line.append(num_str, style="dim")
                line.append(item, style=self.theme.menu_selected if i == selected_idx else self.theme.menu_normal)
                table.add_row(line)

            panel = Panel(
                Align.center(table),
                title=f"[bold {self.theme.accent_style}]Main Menu[/]",
                subtitle="[dim]Use [W/S] or [Up/Down] to navigate • [Enter] to select • [1-7] Direct[/dim]",
                border_style=self.theme.border_style,
                box=SQUARE,
                padding=(1, 4),
            )
            console.print(panel)

            key = self.reader.read_key("Select [1-7 or Enter] > ")

            # Navigation
            if key in ("w", "up"):
                selected_idx = (selected_idx - 1) % len(menu_items)
            elif key in ("s", "down"):
                selected_idx = (selected_idx + 1) % len(menu_items)
            elif key.isdigit() and 1 <= int(key) <= len(menu_items):
                selected_idx = int(key) - 1
                if self._execute_menu_choice(selected_idx):
                    break
            elif key in ("enter", "space"):
                if self._execute_menu_choice(selected_idx):
                    break
            elif key in ("q", "escape"):
                break

    def _execute_menu_choice(self, index: int) -> bool:
        """Dispatch action for selected main menu option. Returns True if exiting."""
        if index == 0:
            self.menu_difficulty()
        elif index == 1:
            self.menu_custom_game()
        elif index == 2:
            self.menu_settings()
        elif index == 3:
            self.menu_records()
        elif index == 4:
            self.menu_how_to_play()
        elif index == 5:
            self.menu_about()
        elif index == 6:
            return True
        return False

    def menu_difficulty(self) -> None:
        """Prompt user to select a predefined difficulty preset."""
        diff_keys = list(DIFFICULTIES.keys())
        options = [DIFFICULTIES[k] for k in diff_keys]
        selected = 0

        while True:
            console.clear()
            console.print(render_header(self.theme))

            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column()

            for i, diff in enumerate(options):
                prefix = "▶ " if i == selected else "  "
                line = Text()
                line.append(prefix, style=f"bold {self.theme.accent_style}")
                line.append(f"[{i + 1}] ", style="dim")
                line.append(f"{diff.name:<8} ", style=self.theme.menu_selected if i == selected else "bold white")
                line.append(f"({diff.width}x{diff.height}, {diff.mines} mines) - {diff.description}", style="dim")
                table.add_row(line)

            # Back option
            back_idx = len(options)
            prefix = "▶ " if selected == back_idx else "  "
            b_line = Text()
            b_line.append(prefix, style=f"bold {self.theme.accent_style}")
            b_line.append(f"[{back_idx + 1}] Back to Main Menu", style=self.theme.menu_selected if selected == back_idx else "dim")
            table.add_row(b_line)

            panel = Panel(
                Align.center(table),
                title=f"[bold {self.theme.accent_style}]Select Difficulty[/]",
                subtitle="[dim]Navigate: [W/S] or [Up/Down] • Select: [Enter][/dim]",
                border_style=self.theme.border_style,
                box=SQUARE,
                padding=(1, 4),
            )
            console.print(panel)

            key = self.reader.read_key("Choice > ")
            total_choices = len(options) + 1

            if key in ("w", "up"):
                selected = (selected - 1) % total_choices
            elif key in ("s", "down"):
                selected = (selected + 1) % total_choices
            elif key.isdigit() and 1 <= int(key) <= total_choices:
                selected = int(key) - 1
                if selected == len(options):
                    return
                chosen = options[selected]
                self.launch_game(chosen.width, chosen.height, chosen.mines, chosen.name)
                return
            elif key in ("enter", "space"):
                if selected == len(options):
                    return
                chosen = options[selected]
                self.launch_game(chosen.width, chosen.height, chosen.mines, chosen.name)
                return
            elif key in ("q", "escape"):
                return

    def menu_custom_game(self) -> None:
        """Prompt and validate custom board dimensions."""
        console.clear()
        console.print(render_header(self.theme))

        info_text = Text()
        info_text.append("CUSTOM BOARD CONFIGURATION\n\n", style=f"bold {self.theme.accent_style}")
        info_text.append(f"• Width:  {MIN_BOARD_WIDTH} to {MAX_BOARD_WIDTH}\n", style="white")
        info_text.append(f"• Height: {MIN_BOARD_HEIGHT} to {MAX_BOARD_HEIGHT}\n", style="white")
        info_text.append("• Mines:  1 up to (Width * Height - 1)\n\n", style="white")
        info_text.append("Type 'c' at any prompt to cancel.\n", style="dim italic")

        panel = Panel(
            Align.center(info_text),
            title=f"[bold {self.theme.accent_style}]Custom Game[/]",
            border_style=self.theme.border_style,
            box=SQUARE,
            padding=(1, 3),
        )
        console.print(panel)

        try:
            # Width input
            while True:
                w_str = Prompt.ask("Enter board width", default="20").strip()
                if w_str.lower() in ("c", "cancel", "q"):
                    return
                if w_str.isdigit() and MIN_BOARD_WIDTH <= int(w_str) <= MAX_BOARD_WIDTH:
                    width = int(w_str)
                    break
                console.print(f"[red]Width must be an integer between {MIN_BOARD_WIDTH} and {MAX_BOARD_WIDTH}[/]")

            # Height input
            while True:
                h_str = Prompt.ask("Enter board height", default="15").strip()
                if h_str.lower() in ("c", "cancel", "q"):
                    return
                if h_str.isdigit() and MIN_BOARD_HEIGHT <= int(h_str) <= MAX_BOARD_HEIGHT:
                    height = int(h_str)
                    break
                console.print(f"[red]Height must be an integer between {MIN_BOARD_HEIGHT} and {MAX_BOARD_HEIGHT}[/]")

            # Mines input
            max_mines = (width * height) - 1
            default_mines = max(1, (width * height) // 6)
            while True:
                m_str = Prompt.ask("Enter mine count", default=str(default_mines)).strip()
                if m_str.lower() in ("c", "cancel", "q"):
                    return
                if m_str.isdigit() and MIN_MINES_COUNT <= int(m_str) <= max_mines:
                    mines = int(m_str)
                    break
                console.print(f"[red]Mines must be an integer between {MIN_MINES_COUNT} and {max_mines}[/]")

        except (KeyboardInterrupt, EOFError):
            return

        self.launch_game(width, height, mines, "Custom", custom_config=(width, height, mines))

    def launch_game(
        self,
        width: int,
        height: int,
        mines: int,
        mode_name: str,
        custom_config: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        """Start an interactive game session."""
        session = GameSession(
            width=width,
            height=height,
            num_mines=mines,
            mode_name=mode_name,
            settings=self.settings_mgr.settings,
            records=self.records_mgr,
            custom_config=custom_config,
            input_reader=self.reader,
        )
        session.run()

    def menu_settings(self) -> None:
        """Settings configuration menu."""
        while True:
            console.clear()
            console.print(render_header(self.theme))

            settings = self.settings_mgr.settings
            items = [
                f"Theme: [bold cyan]{THEMES[settings.theme].display_name}[/]",
                f"Key Bindings: [dim](Customize controls)[/]",
                f"Show Timer: {'[bold green]ON[/]' if settings.show_timer else '[bold red]OFF[/]'}",
                f"Show Coordinates: {'[bold green]ON[/]' if settings.show_coords else '[bold red]OFF[/]'}",
                f"Compact Mode: {'[bold green]ON[/]' if settings.compact_mode else '[bold red]OFF[/]'}",
                "Reset Key Bindings to Defaults",
                "Reset All Settings to Defaults",
                "Reset All Records (Clear Stats)",
                "Back to Main Menu",
            ]

            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column()
            for i, it in enumerate(items):
                num_str = f"[{i + 1}] "
                line = Text.from_markup(f"[dim]{num_str}[/]{it}")
                table.add_row(line)

            panel = Panel(
                Align.center(table),
                title=f"[bold {self.theme.accent_style}]Settings[/]",
                subtitle="[dim]Select option [1-9] • [Q] Back[/dim]",
                border_style=self.theme.border_style,
                box=SQUARE,
                padding=(1, 4),
            )
            console.print(panel)

            key = self.reader.read_key("Choice [1-9] > ")
            if key in ("1", "t"):
                self._change_theme()
            elif key in ("2", "k"):
                self._customize_keys()
            elif key == "3":
                settings.show_timer = not settings.show_timer
                self.settings_mgr.save()
            elif key == "4":
                settings.show_coords = not settings.show_coords
                self.settings_mgr.save()
            elif key == "5":
                settings.compact_mode = not settings.compact_mode
                self.settings_mgr.save()
            elif key == "6":
                self.settings_mgr.reset_key_bindings()
                console.print("[green]Key bindings reset to default![/]")
                self.reader.read_key("Press any key to continue...")
            elif key == "7":
                if Confirm.ask("Reset all settings to factory default?", default=False):
                    self.settings_mgr.reset_to_defaults()
                    console.print("[green]Settings reset to defaults![/]")
                    self.reader.read_key("Press any key to continue...")
            elif key == "8":
                if Confirm.ask("Clear all best times and game records?", default=False):
                    self.records_mgr.reset_all_records()
                    console.print("[green]Records cleared![/]")
                    self.reader.read_key("Press any key to continue...")
            elif key in ("9", "q", "escape", "backspace"):
                break

    def _change_theme(self) -> None:
        """Theme selector dialog."""
        theme_keys = list(THEMES.keys())
        console.clear()
        console.print(render_header(self.theme))

        table = Table(show_header=True, box=ROUNDED, border_style=self.theme.border_style)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Theme", style="bold")
        table.add_column("Description")

        current = self.settings_mgr.settings.theme
        for i, k in enumerate(theme_keys):
            th = THEMES[k]
            mark = " (active)" if k == current else ""
            table.add_row(str(i + 1), f"{th.display_name}{mark}", th.description)

        panel = Panel(
            Align.center(table),
            title="[bold]Select Theme[/]",
            subtitle="[dim]Enter number [1-7] or [Q] to Cancel[/dim]",
            border_style=self.theme.border_style,
            box=SQUARE,
            padding=(1, 3),
        )
        console.print(panel)

        key = self.reader.read_key("Select Theme > ")
        if key.isdigit() and 1 <= int(key) <= len(theme_keys):
            chosen = theme_keys[int(key) - 1]
            self.settings_mgr.settings.theme = chosen
            self.settings_mgr.save()

    def _customize_keys(self) -> None:
        """Interactive key rebinding dialog with conflict detection."""
        console.clear()
        console.print(render_header(self.theme))

        table = Table(show_header=True, box=ROUNDED, border_style=self.theme.border_style)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Action", style="bold")
        table.add_column("Current Keys", style="cyan")

        bindings = self.settings_mgr.settings.key_bindings
        for i, act in enumerate(ALL_ACTIONS):
            keys = ", ".join(bindings.get(act, []))
            table.add_row(str(i + 1), ACTION_LABELS.get(act, act), keys)

        panel = Panel(
            Align.center(table),
            title="[bold]Key Bindings[/]",
            subtitle="[dim]Select action number [1-9] to edit, or [Q] to return[/dim]",
            border_style=self.theme.border_style,
            box=SQUARE,
            padding=(1, 3),
        )
        console.print(panel)

        key = self.reader.read_key("Edit Action [1-9/Q] > ")
        if key.isdigit() and 1 <= int(key) <= len(ALL_ACTIONS):
            target_act = ALL_ACTIONS[int(key) - 1]
            act_name = ACTION_LABELS.get(target_act, target_act)
            console.print(f"\nEnter new comma-separated keys for [bold cyan]{act_name}[/]:")
            new_input = Prompt.ask("Keys (e.g. 'w, up' or 'enter, space')").strip()
            if not new_input:
                return

            new_keys = [k.strip() for k in new_input.split(",") if k.strip()]
            if not new_keys:
                console.print("[red]No keys entered.[/]")
                self.reader.read_key()
                return

            # Test validation
            test_bindings = dict(bindings)
            test_bindings[target_act] = new_keys
            valid, err = validate_key_bindings(test_bindings)
            if not valid:
                console.print(f"[red]Error: {err}[/]")
                self.reader.read_key("Press any key to continue...")
                return

            self.settings_mgr.settings.key_bindings = test_bindings
            self.settings_mgr.save()
            console.print(f"[green]Successfully updated keys for {act_name}![/]")
            self.reader.read_key("Press any key to continue...")

    def menu_records(self) -> None:
        """Display predefined difficulty records and custom game statistics."""
        console.clear()
        console.print(render_header(self.theme))

        # Predefined difficulty records table
        table = Table(
            title="🏆 Predefined Difficulty Leaderboard",
            box=ROUNDED,
            border_style=self.theme.border_style,
            header_style="bold bright_cyan",
        )
        table.add_column("Difficulty", style="bold")
        table.add_column("Dimensions", justify="center", style="dim")
        table.add_column("Mines", justify="center")
        table.add_column("Best Time", justify="right", style="bold bright_yellow")
        table.add_column("Won", justify="right", style="green")
        table.add_column("Lost", justify="right", style="red")
        table.add_column("Win %", justify="right", style="bright_white")
        table.add_column("Last Played", justify="center", style="dim")

        for key, diff in DIFFICULTIES.items():
            stat = self.records_mgr.stats.get(key)
            if stat:
                b_time = f"{stat.best_time:.1f}s" if stat.best_time is not None else "--"
                won = stat.games_won
                lost = stat.games_lost
                total = stat.games_played
                win_pct = f"{(won / total * 100):.0f}%" if total > 0 else "0%"
                last = stat.last_played or "--"
            else:
                b_time = "--"
                won, lost = 0, 0
                win_pct = "0%"
                last = "--"

            table.add_row(
                diff.name,
                f"{diff.width}x{diff.height}",
                str(diff.mines),
                b_time,
                str(won),
                str(lost),
                win_pct,
                last,
            )

        # Custom stats table if any exists
        custom_elements = [table]
        if self.records_mgr.custom_stats:
            c_table = Table(
                title="🎯 Custom Games History",
                box=ROUNDED,
                border_style=self.theme.border_style,
                header_style="bold magenta",
            )
            c_table.add_column("Config", style="bold")
            c_table.add_column("Best Time", justify="right", style="bold yellow")
            c_table.add_column("Won / Played", justify="center")
            c_table.add_column("Last Played", justify="center", style="dim")

            for cfg_key, cstat in self.records_mgr.custom_stats.items():
                b_time = f"{cstat['best_time']:.1f}s" if cstat.get("best_time") else "--"
                wp = f"{cstat.get('games_won', 0)} / {cstat.get('games_played', 0)}"
                last = cstat.get("last_played", "--")
                c_table.add_row(cfg_key, b_time, wp, last)

            custom_elements.append(c_table)

        group = Group(*custom_elements)
        panel = Panel(
            Align.center(group),
            title=f"[bold {self.theme.accent_style}]Player Records[/]",
            subtitle="[dim]Press any key to return to Main Menu[/dim]",
            border_style=self.theme.border_style,
            box=SQUARE,
            padding=(1, 3),
        )
        console.print(panel)
        self.reader.read_key()

    def menu_how_to_play(self) -> None:
        """Display How to Play guide."""
        console.clear()
        console.print(render_header(self.theme))
        console.print(render_how_to_play(self.theme))
        self.reader.read_key()

    def menu_about(self) -> None:
        """Display About the Creator screen."""
        console.clear()
        console.print(render_header(self.theme))
        console.print(render_about(self.theme))
        self.reader.read_key()
