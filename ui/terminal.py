"""Red-and-black terminal presentation helpers."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme


THEME = Theme(
    {
        "danger": "bold red",
        "accent": "bright_red",
        "muted": "dim",
        "success": "bold green",
    }
)


def create_console() -> Console:
    return Console(theme=THEME)


def show_banner(console: Console) -> None:
    console.print(
        Panel.fit(
            "[danger]C Y B E R   A I[/danger] [muted]v1.0[/muted]\n"
            "[muted]TOOLS → DATA → INTELLIGENCE[/muted]",
            border_style="red",
            padding=(1, 3),
        )
    )


def show_menu(console: Console) -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="accent", width=4)
    table.add_column(style="white")
    for number, label in (
        ("01", "SECURITY DASHBOARD"),
        ("02", "RECON CENTER"),
        ("03", "CYBER LAB"),
        ("04", "DEFENSE CENTER"),
        ("05", "PRIVACY CENTER"),
        ("06", "IDENTITY PROFILES"),
        ("07", "CREDENTIAL VAULT"),
        ("08", "RAW EVIDENCE"),
        ("09", "INTELLIGENCE MEMORY"),
        ("10", "SETTINGS"),
        ("00", "EXIT"),
    ):
        table.add_row(number, label)
    console.print(table)