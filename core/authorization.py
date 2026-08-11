"""Explicit authorization gates for recon and lab targets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from storage.sqlite_store import SQLiteStore


@dataclass(frozen=True)
class AuthorizedTarget:
    target: str
    scope: str
    notes: str = ""


def normalize_target(target: str) -> str:
    return target.strip().lower().rstrip("/")


class AuthorizationManager:
    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def authorize(self, record: AuthorizedTarget) -> None:
        target = normalize_target(record.target)
        if not target:
            raise ValueError("Target cannot be empty")
        if not record.scope.strip():
            raise ValueError("Authorization scope cannot be empty")
        self._store.add_authorized_target(
            target=target,
            scope=record.scope.strip(),
            notes=record.notes.strip(),
            authorized_at=datetime.now(UTC).isoformat(),
        )

    def is_authorized(self, target: str) -> bool:
        return self._store.is_authorized(normalize_target(target))

    def require_authorized(self, target: str) -> None:
        if not self.is_authorized(target):
            raise PermissionError(
                "Target is not authorized. Add an explicit authorization record before collecting data."
            )