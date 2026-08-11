"""Application paths and runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Resolved paths for one CYBER AI installation."""

    home: Path
    database_path: Path
    evidence_path: Path
    log_path: Path
    development_mode: bool = False

    @classmethod
    def from_environment(cls) -> "Settings":
        project_root = Path(__file__).resolve().parents[1]
        configured_home = os.environ.get("CYBER_AI_HOME")
        home = Path(configured_home).expanduser() if configured_home else Path.home() / ".cyber-ai"
        return cls(
            home=home,
            database_path=home / "cyber_ai.sqlite3",
            evidence_path=home / "evidence",
            log_path=home / "logs" / "cyber_ai.log",
            development_mode=os.environ.get("CYBER_AI_DEV_MODE", "").lower()
            in {"1", "true", "yes", "on"},
        )

    def ensure_directories(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        self.evidence_path.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)