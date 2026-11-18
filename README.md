# AI KYC Review Assistant

**Status:** Evaluated portfolio prototype (not approved for production banking use)  
**Stack:** Python 3.11 · OpenAI Responses API · Pydantic · pytest  
**Data:** Synthetic KYC cases only

## Overview

A Python prototype that supports a human KYC reviewer by assessing synthetic customer information. It combines deterministic financial-crime analytics with an LLM-generated structured assessment, controlled fallback, limited evidence checks, and review metadata.

## Architecture

```text
Synthetic KYC JSON
  -> load_case.py / validate_case.py
  -> risk_metrics.py (volume difference, percentage variance, country deviations)
  -> prompt_builder.py (prompt v0.2)
  -> llm_client.py (structured Pydantic review)
       |-- classified transient API issue -> deterministic fallback
       `-- nonrecoverable failure -> fail closed
  -> main.py enforces human_review_required = True
  -> evidence_validator.py (limited rule-based flags)
  -> output_formatter.py (review ID, model, prompt version, UTC time, source hash)
  -> save_review.py (JSON save, rejects overwrite)
```

The `human_review_required` flag does **not** implement human approval. The SHA-256 source hash is a fingerprint, **not** tamper-proof storage. The evidence validator uses limited pattern matching, not comprehensive factual verification.

## Repository layout

```text
src/             Application source
src/main.py      Command-line entry point
tests/           Automated regression tests
data/            Synthetic sample KYC case
evaluation/      Synthetic scenarios, evaluation scripts and expectations
docs/            Evaluation report, limitations and architecture notes
requirements.txt
.gitignore
```

## Setup (Windows PowerShell)

Use Python 3.11. From the project root:

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\python.exe -m pip install -r requirements.txt
.\.venv311\Scripts\python.exe -m pytest tests/ -q
```

For live model generation, set `OPENAI_API_KEY` securely in your own environment. **Never commit keys or paste them into logs or documentation.** The application sends the synthetic KYC input to an external API; do not substitute real customer information without a separately approved privacy/security design.

The CLI uses fixed paths `data/kyc_case_001.json` and `outputs/kyc_review_001.json`. The saver intentionally **refuses to overwrite** an existing output. Run from a clean working folder or archive an existing synthetic output first; do not delete audit evidence casually.

```powershell
.\.venv311\Scripts\python.exe src/main.py
```

## Verified results

- **19/19** regression tests passed in the Python 3.11 virtual environment (user-reported run).
- **10/10** synthetic evaluations completed for prompt v0.1.
- Automated evaluation reported **90% raw-model human-review flag compliance** (EVAL-001 returned `false`). The application subsequently enforces `true` independently of the LLM.
- Analyst-applied v0.1 qualitative score **73/100**, a small-sample rubric judgment, **not** statistical model accuracy.
- Retrospective enhanced-validator review of v0.1 flagged **6/10** outputs; prompt v0.2 run flagged **1/10**, with the flagged EVAL-007 identified as a **negation false positive**. This is a *rule-based flag comparison*, not proof that model factual accuracy improved; nine v0.2 cases have not been qualitatively adjudicated here.

See `docs/EVALUATION_SUMMARY.md` for methodology and qualifications.

## Known limitations

- Ten evaluation cases are variations of one synthetic customer; coverage is narrow.
- Evidence validator can miss unsupported claims and flag harmless negations.
- Real human decision logging, access control, encryption, privacy review, monitoring, and independent operational validation are not established.
- Output files are local JSON, not governed immutable audit storage.

## Portfolio scope

Demonstrates LLM API integration, deterministic analytics, structured outputs, exception handling, synthetic model evaluation, and governance-aware application design. **It is a portfolio prototype, not a production-certified KYC system.**
