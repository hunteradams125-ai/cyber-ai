"""The collection-to-evidence pipeline."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from storage.sqlite_store import SQLiteStore


@dataclass(frozen=True)
class FindingInput:
    title: str
    summary: str
    severity: str = "INFO"
    confidence: float = 1.0


@dataclass(frozen=True)
class EvidenceBundle:
    evidence_id: str
    raw_path: Path
    sha256: str
    finding_ids: tuple[str, ...]


class EvidenceStore:
    """Stores raw evidence separately and indexes its metadata in SQLite."""

    def __init__(self, store: SQLiteStore, evidence_root: Path) -> None:
        self._store = store
        self._evidence_root = evidence_root
        self._evidence_root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        *,
        collector: str,
        target: str,
        command: Iterable[str],
        raw_data: str | bytes,
        findings: Iterable[FindingInput] = (),
    ) -> EvidenceBundle:
        evidence_id = f"ev-{uuid.uuid4().hex[:16]}"
        timestamp = datetime.now(UTC)
        raw_bytes = raw_data.encode("utf-8") if isinstance(raw_data, str) else raw_data
        digest = hashlib.sha256(raw_bytes).hexdigest()
        file_name = f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}-{evidence_id}.raw"
        raw_path = self._evidence_root / file_name
        raw_path.write_bytes(raw_bytes)

        finding_inputs = tuple(findings)
        finding_ids = tuple(
            f"finding-{uuid.uuid4().hex[:16]}" for _ in finding_inputs
        )
        # Insert the parent first so SQLite's foreign-key constraint is satisfied.
        self._store.add_evidence(
            evidence_id=evidence_id,
            collected_at=timestamp.isoformat(),
            collector=collector,
            target=target,
            command_json=json.dumps(list(command), ensure_ascii=False),
            sha256=digest,
            finding_ids_json=json.dumps(finding_ids),
            raw_path=str(raw_path),
        )

        for finding_id, finding in zip(finding_ids, finding_inputs):
            self._store.add_finding(
                finding_id=finding_id,
                evidence_id=evidence_id,
                title=finding.title,
                summary=finding.summary,
                severity=finding.severity,
                confidence=max(0.0, min(1.0, finding.confidence)),
                created_at=timestamp.isoformat(),
            )
        return EvidenceBundle(evidence_id, raw_path, digest, finding_ids)