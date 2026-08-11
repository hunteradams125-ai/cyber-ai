"""Small parsers kept independent from collection and display."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PortObservation:
    port: int
    protocol: str
    state: str
    service: str


_PORT_LINE = re.compile(r"^(?P<port>\d+)/(?:tcp|udp)\s+(?P<state>\S+)\s+(?P<service>\S+)", re.IGNORECASE)


def parse_nmap_like_output(raw: str) -> list[PortObservation]:
    observations: list[PortObservation] = []
    for line in raw.splitlines():
        match = _PORT_LINE.match(line.strip())
        if match:
            observations.append(
                PortObservation(
                    port=int(match.group("port")),
                    protocol=line.split("/", 1)[1].split()[0].lower(),
                    state=match.group("state").upper(),
                    service=match.group("service"),
                )
            )
    return observations