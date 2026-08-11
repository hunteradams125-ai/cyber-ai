"""Authorized recon center foundation for Phase 1."""

from __future__ import annotations

from core.authorization import AuthorizationManager
from core.evidence import FindingInput
from core.pipeline import CollectionPipeline, PipelineResult
from collectors.fixtures import load_text


class ReconCenter:
    def __init__(
        self,
        authorization: AuthorizationManager,
        pipeline: CollectionPipeline,
        development_mode: bool,
    ) -> None:
        self._authorization = authorization
        self._pipeline = pipeline
        self._development_mode = development_mode

    def collect_development_observation(self, target: str) -> PipelineResult:
        self._authorization.require_authorized(target)
        if not self._development_mode:
            raise RuntimeError("Development fixtures are disabled. A real collector will be added in Phase 2.")
        raw = load_text("nmap_sample.txt")
        findings = (
            FindingInput(
                title="Development fixture loaded",
                summary="Nmap-shaped sample data was collected for pipeline verification.",
                severity="INFO",
                confidence=1.0,
            ),
        )
        return self._pipeline.collect(
            collector="recon.fixture",
            target=target,
            command=("fixture", "nmap_sample.txt"),
            raw_data=raw,
            findings=findings,
            summary="Development observation collected and indexed as raw evidence.",
        )