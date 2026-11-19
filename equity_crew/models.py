from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class DatedEvidence(BaseModel):
    claim: str
    source: str
    as_of_date: str
    stance: Literal["bullish", "bearish", "neutral"] = "neutral"


class CandidateCompany(BaseModel):
    ticker: str
    name: str
    sector: str = "Unknown"
    as_of_date: str
    metrics: Dict[str, Optional[float]] = Field(default_factory=dict)
    evidence: List[DatedEvidence] = Field(default_factory=list)


class EquityDecisionReport(BaseModel):
    as_of_date: str
    status: Literal["COMPLETED", "NO_CANDIDATES"]
    disclaimer: str = (
        "RESEARCH ONLY: Not financial advice. Missing metrics are marked UNAVAILABLE."
    )
    selected_ticker: Optional[str] = None
    rubric_scores: Dict[str, float] = Field(default_factory=dict)
    unavailable_metrics: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    rationale: str = ""
