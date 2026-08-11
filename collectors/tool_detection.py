"""Detection of optional commands available on Termux or development hosts."""

from __future__ import annotations

import shutil


OPTIONAL_TOOLS = ("nmap", "curl", "tor", "openssl")


def detect_optional_tools() -> dict[str, bool]:
    return {tool: shutil.which(tool) is not None for tool in OPTIONAL_TOOLS}