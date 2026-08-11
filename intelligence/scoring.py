"""Conservative severity vocabulary and explanations."""

from __future__ import annotations

from dataclasses import dataclass


SEVERITIES = ("INFO", "LOW", "REVIEW", "MEDIUM", "HIGH")


@dataclass(frozen=True)
class RiskAssessment:
    severity: str
    confidence: float
    explanation: str


def assess_baseline_status(*, known: bool, changed: bool, corroborating_signals: int = 0) -> RiskAssessment:
    if known and not changed:
        return RiskAssessment("INFO", 1.0, "The observation matches an existing baseline.")
    if changed and corroborating_signals >= 2:
        return RiskAssessment(
            "REVIEW",
            0.65,
            "The item differs from baseline and has corroborating observations; review is recommended.",
        )
    if changed:
        return RiskAssessment("LOW", 0.55, "The item differs from baseline, but one observation alone is not proof of malicious activity.")
    return RiskAssessment("INFO", 0.5, "The item has no baseline history yet; record it before drawing conclusions.")