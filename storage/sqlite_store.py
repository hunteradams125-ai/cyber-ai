"""SQLite persistence for structured observations and evidence metadata."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS authorized_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL UNIQUE,
    scope TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    authorized_at TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    collected_at TEXT NOT NULL,
    collector TEXT NOT NULL,
    target TEXT NOT NULL,
    command_json TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    structured_finding_ids_json TEXT NOT NULL,
    raw_path TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL,
    tool TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'INFO',
    confidence REAL NOT NULL DEFAULT 1.0,
    evidence_id TEXT REFERENCES evidence(id)
);
CREATE TABLE IF NOT EXISTS hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL UNIQUE,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'KNOWN'
);
CREATE TABLE IF NOT EXISTS ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    port INTEGER NOT NULL,
    protocol TEXT NOT NULL,
    state TEXT NOT NULL,
    service TEXT NOT NULL DEFAULT '',
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'KNOWN',
    UNIQUE(host_id, port, protocol)
);
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '',
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'KNOWN',
    UNIQUE(host_id, name, version)
);
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence REAL NOT NULL,
    explanation TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN',
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS baselines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    item_key TEXT NOT NULL,
    item_value TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    UNIQUE(category, item_key)
);
CREATE TABLE IF NOT EXISTS memory_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    item_key TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    times_seen INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL,
    details_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(category, item_key)
);
CREATE TABLE IF NOT EXISTS credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    password_ciphertext TEXT NOT NULL,
    service TEXT NOT NULL,
    host TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
"""


class SQLiteStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(SCHEMA)

    def add_authorized_target(
        self, *, target: str, scope: str, notes: str, authorized_at: str
    ) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO authorized_targets(target, scope, notes, authorized_at, active)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(target) DO UPDATE SET scope=excluded.scope,
                    notes=excluded.notes, authorized_at=excluded.authorized_at, active=1
                """,
                (target, scope, notes, authorized_at),
            )

    def is_authorized(self, target: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM authorized_targets WHERE target = ? AND active = 1",
                (target,),
            ).fetchone()
        return row is not None

    def list_authorized_targets(self) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return connection.execute(
                "SELECT target, scope, notes, authorized_at FROM authorized_targets "
                "WHERE active = 1 ORDER BY target"
            ).fetchall()

    def add_evidence(self, **values: str) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO evidence(
                    id, collected_at, collector, target, command_json, sha256,
                    structured_finding_ids_json, raw_path
                ) VALUES (:evidence_id, :collected_at, :collector, :target, :command_json,
                    :sha256, :finding_ids_json, :raw_path)
                """,
                values,
            )

    def add_finding(self, **values: str | float) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO findings(id, evidence_id, title, summary, severity, confidence, created_at)
                VALUES (:finding_id, :evidence_id, :title, :summary, :severity, :confidence, :created_at)
                """,
                values,
            )

    def recent_evidence(self, limit: int = 10) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return connection.execute(
                "SELECT id, collected_at, collector, target, sha256, raw_path "
                "FROM evidence ORDER BY collected_at DESC LIMIT ?",
                (max(1, min(limit, 100)),),
            ).fetchall()

    def counts(self) -> dict[str, int]:
        tables = ("evidence", "findings", "incidents", "baselines", "memory_events")
        with self.connection() as connection:
            return {
                table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in tables
            }