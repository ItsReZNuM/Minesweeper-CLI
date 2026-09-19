"""Visual theme definitions and style palettes for Rich UI rendering."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class Theme:
    """Defines color palette and visual styling across the application."""
    name: str
    display_name: str
    description: str
    border_style: str
    header_style: str
    accent_style: str
    menu_normal: str
    menu_selected: str
    status_bar: str
    cell_hidden: str
    cell_revealed: str
    cell_cursor: str
    flag_style: str
    mine_style: str
    exploded_style: str
    wrong_flag_style: str
    number_styles: Dict[int, str]
    flag_symbol: str = "⚑"
    mine_symbol: str = "*"
    exploded_symbol: str = "!"
    wrong_flag_symbol: str = "X"
    hidden_symbol: str = "■"


THEMES: Dict[str, Theme] = {
    "classic": Theme(
        name="classic",
        display_name="Classic",
        description="Retro Windows Minesweeper style with vibrant primary colors",
        border_style="bright_blue",
        header_style="bold bright_white on blue",
        accent_style="cyan",
        menu_normal="white",
        menu_selected="bold black on bright_cyan",
        status_bar="bold white on blue",
        cell_hidden="bright_black",
        cell_revealed="dim white",
        cell_cursor="bold black on bright_yellow",
        flag_style="bold bright_red",
        mine_style="bold bright_black",
        exploded_style="bold bright_white on red",
        wrong_flag_style="bold bright_red on yellow",
        number_styles={
            1: "bold bright_blue",
            2: "bold bright_green",
            3: "bold bright_red",
            4: "bold dark_blue",
            5: "bold red",
            6: "bold dark_cyan",
            7: "bold black",
            8: "bold bright_black",
        },
    ),
    "matrix": Theme(
        name="matrix",
        display_name="Matrix",
        description="Phosphor digital rain aesthetic with emerald accents",
        border_style="green",
        header_style="bold green on black",
        accent_style="bright_green",
        menu_normal="green",
        menu_selected="bold black on bright_green",
        status_bar="bold green on black",
        cell_hidden="dark_green",
        cell_revealed="green",
        cell_cursor="bold black on bright_green",
        flag_style="bold bright_white on green",
        mine_style="bold bright_green",
        exploded_style="bold bright_white on red",
        wrong_flag_style="bold bright_red",
        number_styles={
            1: "bright_green",
            2: "bold bright_green",
            3: "green",
            4: "bold green",
            5: "bright_white",
            6: "bold bright_white",
            7: "spring_green1",
            8: "spring_green2",
        },
        flag_symbol="▲",
        mine_symbol="☣",
        exploded_symbol="※",
        wrong_flag_symbol="ø",
        hidden_symbol="■",
    ),
    "ocean": Theme(
        name="ocean",
        display_name="Ocean",
        description="Calm deep marine blues and cyan reefs",
        border_style="cyan",
        header_style="bold bright_cyan on navy_blue",
        accent_style="bright_cyan",
        menu_normal="bright_cyan",
        menu_selected="bold navy_blue on bright_cyan",
        status_bar="bold white on dark_blue",
        cell_hidden="blue",
        cell_revealed="cyan",
        cell_cursor="bold black on bright_cyan",
        flag_style="bold bright_yellow",
        mine_style="bold bright_red",
        exploded_style="bold white on red",
        wrong_flag_style="bold bright_magenta",
        number_styles={
            1: "bold bright_cyan",
            2: "bold cyan",
            3: "bold bright_yellow",
            4: "bold bright_blue",
            5: "bold sky_blue1",
            6: "bold deep_sky_blue1",
            7: "bold turquoise2",
            8: "bold white",
        },
    ),
    "dracula": Theme(
        name="dracula",
        display_name="Dracula",
        description="Dark modern theme featuring purples, pinks, and cyans",
        border_style="purple",
        header_style="bold bright_white on purple",
        accent_style="bright_magenta",
        menu_normal="bright_white",
        menu_selected="bold black on bright_magenta",
        status_bar="bold bright_white on dark_magenta",
        cell_hidden="magenta",
        cell_revealed="bright_white",
        cell_cursor="bold black on bright_yellow",
        flag_style="bold bright_yellow",
        mine_style="bold bright_red",
        exploded_style="bold bright_white on red",
        wrong_flag_style="bold bright_red on yellow",
        number_styles={
            1: "bold bright_cyan",
            2: "bold bright_green",
            3: "bold bright_red",
            4: "bold bright_magenta",
            5: "bold bright_yellow",
            6: "bold dark_violet",
            7: "bold bright_white",
            8: "bold orange3",
        },
    ),
    "cyberpunk": Theme(
        name="cyberpunk",
        display_name="Cyberpunk",
        description="High-voltage neon yellow, hot magenta, and electric blue",
        border_style="bright_yellow",
        header_style="bold black on bright_yellow",
        accent_style="bright_magenta",
        menu_normal="bright_yellow",
        menu_selected="bold black on bright_magenta",
        status_bar="bold black on bright_yellow",
        cell_hidden="dark_goldenrod",
        cell_revealed="bright_white",
        cell_cursor="bold black on bright_magenta",
        flag_style="bold bright_cyan",
        mine_style="bold bright_red",
        exploded_style="bold bright_white on red",
        wrong_flag_style="bold bright_yellow on red",
        number_styles={
            1: "bold bright_cyan",
            2: "bold bright_green",
            3: "bold bright_yellow",
            4: "bold bright_magenta",
            5: "bold bright_red",
            6: "bold hot_pink",
            7: "bold light_coral",
            8: "bold white",
        },
    ),
    "nord": Theme(
        name="nord",
        display_name="Nord",
        description="Arctic, cool muted blues and pastel highlights",
        border_style="steel_blue",
        header_style="bold bright_white on steel_blue",
        accent_style="light_sky_blue1",
        menu_normal="white",
        menu_selected="bold black on light_sky_blue1",
        status_bar="bold white on steel_blue",
        cell_hidden="slate_blue",
        cell_revealed="bright_white",
        cell_cursor="bold black on light_cyan",
        flag_style="bold bright_red",
        mine_style="bold bright_black",
        exploded_style="bold white on red",
        wrong_flag_style="bold orange_red1",
        number_styles={
            1: "bold deep_sky_blue2",
            2: "bold medium_sea_green",
            3: "bold indian_red1",
            4: "bold slate_blue1",
            5: "bold salmon1",
            6: "bold turquoise4",
            7: "bold grey70",
            8: "bold grey93",
        },
    ),
    "monochrome": Theme(
        name="monochrome",
        display_name="Monochrome",
        description="Clean, timeless high-contrast grayscale for any terminal",
        border_style="white",
        header_style="bold white on black",
        accent_style="bright_white",
        menu_normal="white",
        menu_selected="bold black on white",
        status_bar="bold black on white",
        cell_hidden="bright_black",
        cell_revealed="white",
        cell_cursor="bold black on white",
        flag_style="bold bright_white",
        mine_style="bold bright_white",
        exploded_style="bold black on white",
        wrong_flag_style="bold white on bright_black",
        number_styles={
            1: "white",
            2: "bright_white",
            3: "bold white",
            4: "bold bright_white",
            5: "underline white",
            6: "underline bright_white",
            7: "bold underline white",
            8: "bold underline bright_white",
        },
        flag_symbol="P",
        mine_symbol="*",
        exploded_symbol="!",
        wrong_flag_symbol="X",
        hidden_symbol="#",
    ),
}


def get_theme(name: str) -> Theme:
    """Retrieve theme by identifier, defaulting to classic."""
    return THEMES.get(name.lower(), THEMES["classic"])
