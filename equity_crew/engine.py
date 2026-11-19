from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .models import CandidateCompany, EquityDecisionReport

DISCLAIMER = "RESEARCH ONLY: Not financial advice. Missing metrics are marked UNAVAILABLE."
REQUIRED_METRICS = ("revenue_growth", "pe_ratio", "free_cash_flow")


class EvidenceAuditedEquityCrew:
    """Audited equity research crew with as-of date checks and explicit UNAVAILABLE flags."""

    def __init__(self, as_of_date: str) -> None:
        self.as_of_date = as_of_date

    def run(self, candidates: List[CandidateCompany], output_dir: Path) -> EquityDecisionReport:
        output_dir.mkdir(parents=True, exist_ok=True)
        trending_payload: Dict[str, Any] = {
            "as_of_date": self.as_of_date,
            "disclaimer": DISCLAIMER,
            "candidates": [c.model_dump() for c in candidates],
        }
        (output_dir / "trending_companies.json").write_text(
            json.dumps(trending_payload, indent=2), encoding="utf-8"
        )

        if not candidates:
            report = EquityDecisionReport(
                as_of_date=self.as_of_date,
                status="NO_CANDIDATES",
                rationale="No trending candidates found; terminated early.",
            )
            self._write_outputs(output_dir, [], report)
            return report

        audited: List[Dict[str, Any]] = []
        scores: Dict[str, float] = {}
        all_unavailable: List[str] = []
        contradictions: List[str] = []

        for company in candidates:
            valid_ev = [e for e in company.evidence if e.as_of_date <= self.as_of_date]
            stances = {e.stance for e in valid_ev}
            if "bullish" in stances and "bearish" in stances:
                contradictions.append(
                    f"{company.ticker}: conflicting bullish and bearish evidence as of {self.as_of_date}"
                )

            metrics_out: Dict[str, Any] = {}
            missing_count = 0
            for key in REQUIRED_METRICS:
                val = company.metrics.get(key)
                if val is None:
                    metrics_out[key] = "UNAVAILABLE"
                    all_unavailable.append(f"{company.ticker}.{key}")
                    missing_count += 1
                else:
                    metrics_out[key] = val

            score = round(len(valid_ev) * 2.0 - missing_count * 1.5, 2)
            scores[company.ticker] = score
            audited.append(
                {
                    "ticker": company.ticker,
                    "name": company.name,
                    "as_of_date": self.as_of_date,
                    "metrics": metrics_out,
                    "evidence": [e.model_dump() for e in valid_ev],
                    "rubric_score": score,
                }
            )

        best_ticker = max(scores, key=lambda t: scores[t])
        report = EquityDecisionReport(
            as_of_date=self.as_of_date,
            status="COMPLETED",
            selected_ticker=best_ticker,
            rubric_scores=scores,
            unavailable_metrics=all_unavailable,
            contradictions=contradictions,
            rationale=f"Selected {best_ticker} with rubric score {scores[best_ticker]}.",
        )
        self._write_outputs(output_dir, audited, report)
        return report

    def _write_outputs(
        self, output_dir: Path, audited: List[Dict[str, Any]], report: EquityDecisionReport
    ) -> None:
        research_payload = {
            "as_of_date": self.as_of_date,
            "disclaimer": DISCLAIMER,
            "status": report.status,
            "companies": audited,
        }
        (output_dir / "research_report.json").write_text(
            json.dumps(research_payload, indent=2), encoding="utf-8"
        )

        lines = [
            f"# Equity Research Decision ({self.as_of_date})",
            "",
            f"> {DISCLAIMER}",
            "",
            f"- **Status:** {report.status}",
            f"- **Selected Ticker:** {report.selected_ticker or 'NONE'}",
            f"- **Rationale:** {report.rationale}",
            "",
            "## Rubric Scores",
        ]
        for ticker, score in report.rubric_scores.items():
            lines.append(f"- {ticker}: {score}")
        lines.extend(["", "## Unavailable Metrics"])
        if report.unavailable_metrics:
            lines.extend(f"- {item}: UNAVAILABLE" for item in report.unavailable_metrics)
        else:
            lines.append("- None")
        lines.extend(["", "## Contradictory Evidence"])
        if report.contradictions:
            lines.extend(f"- {c}" for c in report.contradictions)
        else:
            lines.append("- None")

        (output_dir / "decision.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
