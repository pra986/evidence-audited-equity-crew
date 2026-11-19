# Evidence-Audited Equity Crew (Project 20)

> **RESEARCH ONLY - NOT INVESTMENT ADVICE.** Generated for educational, evaluation, and workflow-auditing purposes.

Role-based CrewAI equity research workflow with dated search evidence, explicit `UNAVAILABLE` financial metric flags, and rubric-scored decision artifacts.

## Architecture

The pipeline pairs a four-role CrewAI research crew with a deterministic auditing engine (`EvidenceAuditedEquityCrew`):

1. **Trend Discovery Analyst** — Identifies candidate companies and sector catalysts (`trending_companies.json`).
2. **Financial Evidence Auditor** — Verifies `as_of_date` bounds on all `DatedEvidence` items and flags any missing financial metric as `UNAVAILABLE` rather than fabricating estimates.
3. **Contradiction & Rubric Scorer** — Surfaces opposing bullish/bearish evidence and computes transparent scores (`research_report.json`).
4. **Decision Memo Writer** — Produces the final `decision.md` report with explicit `UNAVAILABLE` flags, surfaced contradictions, and a mandatory research-only disclaimer.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for component diagrams and failure-mode controls.

## 6-Stage Workflow

1. **As-Of Date & Scope Gate**: Establishes the cutoff `as_of_date` so no post-cutoff evidence leaks into historical or point-in-time evaluations.
2. **Candidate Discovery**: Captures candidate tickers, sectors, and catalysts into `trending_companies.json`.
3. **Dated Evidence Audit**: Drops evidence with `published_date > as_of_date` and records `stale_evidence_dropped`.
4. **Financial Metric Verification**: Checks required metrics (`pe_ratio`, `revenue_growth_pct`, `operating_margin_pct`, `debt_to_equity`); missing or `None` values are explicitly marked `UNAVAILABLE`.
5. **Contradiction Detection & Rubric Scoring**: Flags opposing `bullish` and `bearish` evidence stances and scores candidates on catalyst strength (0-40), financial completeness (0-40), and evidence balance (0-20).
6. **Decision Artifact Generation**: Emits `trending_companies.json`, `research_report.json`, and `decision.md`, each stamped with the research-only disclaimer.

## Data Contract

- **Inputs** (`equity_crew/models.py`):
  - `DatedEvidence`: `source_title`, `source_url`, `published_date`, `stance` (`bullish` | `bearish` | `neutral`), `summary`
  - `CandidateCompany`: `ticker`, `name`, `sector`, `catalyst`, `metrics`, `evidence`
- **Outputs**:
  - `trending_companies.json`: Audited candidate universe with `as_of_date` and disclaimer.
  - `research_report.json`: Full `EquityDecisionReport` with `metrics_status`, `unavailable_metrics`, `contradictions`, `rubric` breakdown, and `selected_ticker`.
  - `decision.md`: Human-readable investment research memo surfacing `UNAVAILABLE` metrics, contradictions, and rubric scores.

## Production Controls

- **Empty Candidate Termination**: If zero candidates are supplied, the crew terminates cleanly with `status="terminated_empty_candidates"`, `selected_ticker=null`, and valid output artifacts.
- **No Hallucinated Metrics**: Missing financial fields are never backfilled or guessed; they are explicitly flagged `UNAVAILABLE` and penalized in `financial_completeness`.
- **Point-in-Time Evidence Enforcement**: Evidence dated after `as_of_date` is excluded from scoring.
- **Contradiction Surfacing**: Conflicting bullish and bearish evidence is explicitly highlighted in `decision.md`.
- **Research-Only Disclaimer**: Embedded in all three output artifacts.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run unit tests
pytest -q

# Run CLI demo
python -m equity_crew.cli --as-of 2026-11-19 --output-dir artifacts
```

## Attribution

Pinned attribution: Adapted and hardened from [`ed-donner/agents`](https://github.com/ed-donner/agents) (`3_crewai/reference/stock_picker`).
 and rubric-scored decision artifacts.
