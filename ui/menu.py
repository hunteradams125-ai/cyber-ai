"""Interactive Phase 1 menu and thin UI orchestration."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from centers.recon import ReconCenter
from collectors.tool_detection import detect_optional_tools
from core.authorization import AuthorizedTarget, AuthorizationManager
from storage.sqlite_store import SQLiteStore
from ui.terminal import show_banner, show_menu


class MainMenu:
    def __init__(
        self,
        *,
        console: Console,
        store: SQLiteStore,
        authorization: AuthorizationManager,
        recon: ReconCenter,
    ) -> None:
        self.console = console
        self.store = store
        self.authorization = authorization
        self.recon = recon

    def run(self) -> None:
        while True:
            self.console.clear()
            show_banner(self.console)
            show_menu(self.console)
            choice = self.console.input("\n[accent]SELECT[/accent] > ").strip()
            if choice == "00":
                self.console.print("[muted]Session closed. Raw evidence remains on disk.[/muted]")
                return
            actions = {
                "01": self.dashboard,
                "02": self.recon_center,
                "03": self.phase_notice,
                "04": self.phase_notice,
                "05": self.phase_notice,
                "06": self.phase_notice,
                "07": self.phase_notice,
                "08": self.raw_evidence,
                "09": self.phase_notice,
                "10": self.settings,
            }
            action = actions.get(choice)
            if action is None:
                self.console.print("[danger]Choose one of the listed options.[/danger]")
                self.console.input("Press Enter to continue...")
            else:
                action()

    def dashboard(self) -> None:
        counts = self.store.counts()
        self.console.print("\n[danger]SECURITY DASHBOARD[/danger]")
        table = Table(show_header=True, header_style="accent")
        table.add_column("STRUCTURED AREA")
        table.add_column("COUNT", justify="right")
        for label, key in (
            ("Evidence records", "evidence"),
            ("Important findings", "findings"),
            ("Incidents", "incidents"),
            ("Baseline items", "baselines"),
            ("Memory observations", "memory_events"),
        ):
            table.add_row(label, str(counts[key]))
        self.console.print(table)
        self.console.input("\nPress Enter to continue...")

    def recon_center(self) -> None:
        self.console.print("\n[danger]RECON CENTER[/danger]")
        target = self.console.input("Authorized target label (for example, lab.local): ").strip()
        if not target:
            return
        if not self.authorization.is_authorized(target):
            self.console.print(
                "[danger]No authorization record exists. No collection will run.[/danger]"
            )
            confirm = self.console.input("Type AUTHORIZE to record your permission and scope: ").strip()
            if confirm != "AUTHORIZE":
                self.console.print("[muted]Authorization declined.[/muted]")
                self.console.input("Press Enter to continue...")
                return
            scope = self.console.input("Scope (what you are allowed to assess): ").strip()
            notes = self.console.input("Notes (optional): ").strip()
            try:
                self.authorization.authorize(AuthorizedTarget(target, scope, notes))
            except ValueError as error:
                self.console.print(f"[danger]{error}[/danger]")
                self.console.input("Press Enter to continue...")
                return
        try:
            result = self.recon.collect_development_observation(target)
        except (PermissionError, RuntimeError) as error:
            self.console.print(f"[danger]{error}[/danger]")
        else:
            self.console.print(f"[success]{result.short_summary}[/success]")
            self.console.print(f"Evidence ID: [accent]{result.bundle.evidence_id}[/accent]")
            self.console.print(f"SHA-256: [muted]{result.bundle.sha256}[/muted]")
        self.console.input("\nPress Enter to continue...")

    def raw_evidence(self) -> None:
        self.console.print("\n[danger]RAW EVIDENCE[/danger]")
        rows = self.store.recent_evidence()
        if not rows:
            self.console.print("[muted]No evidence has been collected yet.[/muted]")
        else:
            table = Table(show_header=True, header_style="accent")
            table.add_column("ID")
            table.add_column("COLLECTOR")
            table.add_column("TARGET")
            table.add_column("SHA-256")
            for row in rows:
                table.add_row(row["id"], row["collector"], row["target"], row["sha256"][:16] + "…")
            self.console.print(table)
            self.console.print("[muted]Open the stored path directly to inspect full command output.[/muted]")
        self.console.input("\nPress Enter to continue...")

    def settings(self) -> None:
        self.console.print("\n[danger]SETTINGS[/danger]")
        tools = detect_optional_tools()
        for tool, available in tools.items():
            status = "[success]AVAILABLE[/success]" if available else "[muted]NOT INSTALLED[/muted]"
            self.console.print(f"{tool:>8}: {status}")
        self.console.input("\nPress Enter to continue...")

    def phase_notice(self) -> None:
        self.console.print(
            "\n[muted]This center is reserved for a later phase. Phase 1 keeps the "
            "storage, authorization, and evidence foundations ready.[/muted]"
        )
        self.console.input("Press Enter to continue...")