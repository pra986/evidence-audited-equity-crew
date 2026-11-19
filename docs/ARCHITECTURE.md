# Architecture: Evidence-Audited Equity Crew

## Overview
`evidence-audited-equity-crew` separates creative/discovery CrewAI agent roles from deterministic financial auditing and schema validation (`EvidenceAuditedEquityCrew`).

## CrewAI Roles
1. **Trend Discovery Analyst**: Identifies candidate equities and catalysts (`trending_companies.json`).
2. **Financial Evidence Auditor**: Validates `published_date <= as_of_date` and flags missing financial metrics as `UNAVAILABLE`.
3. **Contradiction & Rubric Scorer**: Detects opposing `bullish`/`bearish` stances and computes transparent rubric scores (`research_report.json`).
4. **Decision Memo Writer**: Renders `decision.md` with explicit `UNAVAILABLE` flags, contradictions, and the research-only disclaimer.

## Safeguards
- **Empty Candidate Termination**: Halts immediately with `status="terminated_empty_candidates"` and `selected_ticker=null`.
- **No Metric Fabrication**: Missing metrics in `("pe_ratio", "revenue_growth_pct", "operating_margin_pct", "debt_to_equity")` are marked `UNAVAILABLE`.
- **Point-in-Time Isolation**: Evidence with `published_date > as_of_date` is dropped and counted in `stale_evidence_dropped`.
- **Research-Only Disclaimer**: Included in `trending_companies.json`, `research_report.json`, and `decision.md`.
