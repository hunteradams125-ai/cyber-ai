"""Development-mode fixtures that stand in for Android collection adapters."""

from __future__ import annotations

import json
from pathlib import Path


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "data" / "fixtures"


def load_text(name: str) -> str:
    return (FIXTURE_ROOT / name).read_text(encoding="utf-8")


def load_json(name: str) -> list[dict[str, object]]:
    return json.loads(load_text(name))