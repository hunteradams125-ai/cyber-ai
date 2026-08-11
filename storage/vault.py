"""Credential vault primitives. Passwords are encrypted, never logged or displayed by default."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime

from cryptography.fernet import Fernet

from storage.sqlite_store import SQLiteStore


@dataclass(frozen=True)
class Credential:
    username: str
    email: str
    password: str
    service: str
    host: str = ""
    notes: str = ""


class CredentialVault:
    def __init__(self, store: SQLiteStore, key: bytes | None = None) -> None:
        configured_key = key or os.environ.get("CYBER_AI_VAULT_KEY", "").encode("ascii")
        if not configured_key:
            raise ValueError(
                "CYBER_AI_VAULT_KEY is not set. Refusing to create or open the credential vault."
            )
        self._store = store
        self._cipher = Fernet(configured_key)

    def add(self, credential: Credential) -> int:
        with self._store.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO credentials(
                    username, email, password_ciphertext, service, host, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    credential.username,
                    credential.email,
                    self._cipher.encrypt(credential.password.encode("utf-8")).decode("ascii"),
                    credential.service,
                    credential.host,
                    credential.notes,
                    datetime.now(UTC).isoformat(),
                ),
            )
            return int(cursor.lastrowid)

    def list_safe(self) -> list[dict[str, str | int]]:
        with self._store.connection() as connection:
            rows = connection.execute(
                "SELECT id, username, email, service, host, notes, created_at "
                "FROM credentials ORDER BY service"
            ).fetchall()
        return [dict(row) for row in rows]

    def reveal(self, credential_id: int) -> str:
        with self._store.connection() as connection:
            row = connection.execute(
                "SELECT password_ciphertext FROM credentials WHERE id = ?", (credential_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Credential {credential_id} does not exist")
        return self._cipher.decrypt(row["password_ciphertext"].encode("ascii")).decode("utf-8")