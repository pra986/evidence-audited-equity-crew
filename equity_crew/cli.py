from __future__ import annotations

import argparse
from pathlib import Path

from .engine import EvidenceAuditedEquityCrew
from .models import CandidateCompany, DatedEvidence


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Evidence-Audited Equity Crew demo.")
    parser.add_argument("--as-of", default="2026-11-19", help="As-of date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default="output", help="Artifact output directory")
    args = parser.parse_args()

    demo_candidates = [
        CandidateCompany(
            ticker="NOVA",
            name="Nova Compute Corp",
            sector="Technology",
            as_of_date=args.as_of,
            metrics={"revenue_growth": 0.24, "pe_ratio": None, "free_cash_flow": 120.5},
            evidence=[
                DatedEvidence(
                    claim="Cloud revenue grew 24% YoY",
                    source="10-Q Filing",
                    as_of_date=args.as_of,
                    stance="bullish",
                ),
                DatedEvidence(
                    claim="Margin compression noted in guidance",
                    source="Earnings Call",
                    as_of_date=args.as_of,
                    stance="bearish",
                ),
            ],
        )
    ]

    crew = EvidenceAuditedEquityCrew(as_of_date=args.as_of)
    report = crew.run(demo_candidates, Path(args.output_dir))
    print(f"Status: {report.status} | Selected: {report.selected_ticker}")


if __name__ == "__main__":
    main()
