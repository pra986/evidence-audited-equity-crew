import json
from pathlib import Path

from equity_crew.engine import EvidenceAuditedEquityCrew
from equity_crew.models import CandidateCompany, DatedEvidence


def test_empty_candidates_terminates(tmp_path: Path) -> None:
    crew = EvidenceAuditedEquityCrew(as_of_date="2026-11-19")
    report = crew.run([], tmp_path)
    assert report.status == "NO_CANDIDATES"
    assert (tmp_path / "trending_companies.json").exists()
    assert (tmp_path / "research_report.json").exists()
    assert (tmp_path / "decision.md").exists()


def test_missing_metric_marked_unavailable(tmp_path: Path) -> None:
    company = CandidateCompany(
        ticker="ACME",
        name="Acme Corp",
        as_of_date="2026-11-19",
        metrics={"revenue_growth": 0.15, "pe_ratio": None},
        evidence=[],
    )
    crew = EvidenceAuditedEquityCrew(as_of_date="2026-11-19")
    report = crew.run([company], tmp_path)
    assert "ACME.pe_ratio" in report.unavailable_metrics
    assert "ACME.free_cash_flow" in report.unavailable_metrics
    research = json.loads((tmp_path / "research_report.json").read_text())
    assert research["companies"][0]["metrics"]["pe_ratio"] == "UNAVAILABLE"
    assert research["companies"][0]["metrics"]["free_cash_flow"] == "UNAVAILABLE"


def test_contradictory_evidence_and_schema(tmp_path: Path) -> None:
    company = CandidateCompany(
        ticker="NOVA",
        name="Nova Compute",
        as_of_date="2026-11-19",
        metrics={"revenue_growth": 0.2, "pe_ratio": 25.0, "free_cash_flow": 50.0},
        evidence=[
            DatedEvidence(claim="Strong growth", source="10-Q", as_of_date="2026-11-19", stance="bullish"),
            DatedEvidence(claim="Margin risk", source="Call", as_of_date="2026-11-19", stance="bearish"),
            DatedEvidence(claim="Future leak", source="Rumor", as_of_date="2026-12-01", stance="bullish"),
        ],
    )
    crew = EvidenceAuditedEquityCrew(as_of_date="2026-11-19")
    report = crew.run([company], tmp_path)
    assert report.status == "COMPLETED"
    assert len(report.contradictions) == 1

    trending = json.loads((tmp_path / "trending_companies.json").read_text())
    research = json.loads((tmp_path / "research_report.json").read_text())
    decision = (tmp_path / "decision.md").read_text()

    assert "RESEARCH ONLY" in trending["disclaimer"]
    assert "RESEARCH ONLY" in research["disclaimer"]
    assert "RESEARCH ONLY" in decision
    assert "## Contradictory Evidence" in decision
    assert "NOVA: conflicting bullish and bearish evidence" in decision
    assert len(research["companies"][0]["evidence"]) == 2
