"""Reusable tools -> data -> intelligence orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.evidence import EvidenceBundle, EvidenceStore, FindingInput


@dataclass(frozen=True)
class PipelineResult:
    bundle: EvidenceBundle
    short_summary: str


class CollectionPipeline:
    def __init__(self, evidence_store: EvidenceStore) -> None:
        self._evidence_store = evidence_store

    def collect(
        self,
        *,
        collector: str,
        target: str,
        command: Iterable[str],
        raw_data: str | bytes,
        findings: Iterable[FindingInput],
        summary: str,
    ) -> PipelineResult:
        bundle = self._evidence_store.save(
            collector=collector,
            target=target,
            command=command,
            raw_data=raw_data,
            findings=findings,
        )
        return PipelineResult(bundle=bundle, short_summary=summary)