# AI KYC Review Assistant — Evaluation and Assurance Report

**Document status:** Portfolio prototype evaluation (not a production certification)  
**Version:** 1.0 draft  
**Date:** 18 November 2026  
**Scope:** Synthetic KYC evaluation, application-level controls and known implementation limitations

## 1. Executive summary

The AI KYC Review Assistant is a Python-based, human-in-the-loop prototype for generating structured KYC review assessments from synthetic customer information. Its pipeline combines input validation, deterministic transaction analytics, OpenAI structured generation, basic evidence checks, an auditable JSON envelope, and controlled fallback for transient API failures.

**Observed evidence:** The Python 3.11 regression suite passed **19/19 tests**. Ten synthetic evaluation cases were submitted to the OpenAI-backed assessment flow and all ten generated result files. An automated scorecard reported 100% for several narrow, machine-checked measures but **90% raw-model compliance with the requirement that human review be indicated**. The failing case was **EVAL-001**. The application was subsequently updated to set `human_review_required = True` deterministically, and the existing 19 tests still passed.

**Conclusion:** This is a functionally tested **portfolio-ready candidate**, subject to final documentation and reproducibility checks. It is **not verified production-ready for use with real bank customer data**.

## 2. Scope and architecture

```text
Synthetic KYC input JSON
  → Case loading and input validation
  → Deterministic analytics (volume variance, unexpected countries)
  → Prompt builder
  → OpenAI structured response (Pydantic schema)
      ↳ on classified transient API failure: deterministic fallback
      ↳ on configuration/response/unexpected failure: stop with nonzero exit
  → Application-enforced mandatory human-review flag
  → Evidence checks (limited, rule-based)
  → Output envelope (review ID, model, generation mode, timestamp,
     prompt version, SHA-256 of validated source data)
  → JSON save with overwrite protection + operational logging
```

The mandatory review flag is a control **indicator**, not an implemented approval workflow. The source hash is a fingerprint, not tamper-evident or immutable storage.

## 3. Functional and regression test results

| Evidence | Observed result | Interpretation |
|---|---:|---|
| Automated regression suite, Python 3.11 virtual environment | **19/19 passed** | Tested code paths pass; does not establish complete coverage |
| Isolated mocked API-success and transient-failure workflows | Passed | Correctly exercises these simulated paths |
| Critical failures: configuration, invalid response, unexpected error | Passed | Simulated errors stop without saving a fallback review |
| Deterministic metric checks | Passed | Known volume/country examples computed correctly |
| Audit fields, source-data hash stability/change | Passed | Metadata and canonical hashing behave as tested |
| Save refusal on existing output | Passed | Tested non-overwrite behavior; not complete storage security |
| Mandatory review flag | Existing tests passed after update | The code enforces the flag; dedicated raw-false-to-final-true regression assertion is advisable |

**Test caveat:** Some checks use mocked responses, some are narrow regex-based rules, and the logging test does not exercise real secret-bearing exception paths. The suite is not a security penetration test or regulatory validation.

## 4. Synthetic AI evaluation — 10 cases

The evaluation runner completed ten API-backed assessments (EVAL-001 through EVAL-010), with **10 completed / 0 failed**. The score script produced:

| Measure | Reported score | Precisely what was measured |
|---|---:|---|
| Customer identity | **100%** | Exact match of returned customer ID to case ID |
| Reference metrics integrity | **100%** | Stored deterministic metrics agree with precomputed expectations; **not an AI reasoning score** |
| Transaction variance mention | **100%** | Expected percentage string appears when applicable; not full semantic correctness |
| Unexpected-country mention | **100%** | Expected country names appear in assessment when applicable; not a complete false-positive check |
| Documented missing information | **100%** | Exact list match for supplied missing-information items |
| Raw-model human-review compliance | **90%** | `human_review_required` is `true` in 9 of 10 unmodified AI responses |

These results are **descriptive for this specific 10-case synthetic sample**. They are not reliable population-level accuracy estimates or evidence of readiness for regulated decision-making.

### EVAL-002 — Example qualitative assessment

The output identified: expected CHF 500,000 monthly, observed CHF 1,250,000, a **+150% variance**, and Turkey as an observed country outside the expected list. It did not automatically classify Turkey as high risk; it recommended human investigation. Its UBO ownership statement was supported by the supplied synthetic case. This is one favorable qualitative example, not a substitute for reviewing all 10 assessments.

### EVAL-001 — Governance defect and mitigation

**Finding:** The raw model response returned `human_review_required = false` for EVAL-001, a case without a volume increase or unexpected countries. This violated the application's policy that every AI-generated KYC assessment be reviewed by a human, regardless of apparent risk level.

**Mitigation implemented:** After AI generation or fallback, the application executes a deterministic override setting `review_dict["human_review_required"] = True` before constructing the final audit envelope. The original raw evaluation output is preserved as evidence of the model behavior. The regression suite passed **19/19** after the change.

**Interpretation:** The application-level control reduces reliance on the model's recommendation for this requirement; it **does not** create a workflow recording reviewer identity, decision, approval time or rationale. The **90% raw-model figure must not be re-labelled as 100% model accuracy**.

## 5. Other observed risks and limits

1. **Evidence grounding:** Current evidence validation is a small set of rules. It can flag a specific unsupported geographic-risk wording, but cannot generally determine whether every assertion is supported by the source, applicable risk methodology or reliable evidence.
2. **Jurisdiction and sanctions:** A location being outside a customer's expected transaction pattern does not itself make that country prohibited or high-risk. Bank-approved country-risk methodologies and applicable sanctions rules would need separate controls and dated authoritative reference data.
3. **Escalation quality:** No formal adjudicated labels or rubric-based assessment have yet been collected across all ten cases. Recommendation quality is not quantitatively validated.
4. **Sensitive data:** Evaluation used synthetic data. Authorization, encryption at rest/in transit, retention, customer data minimization, processor governance and privacy assessments for real KYC records are not demonstrated.
5. **Operational resilience:** The fallback is appropriate only for selected transient failures. The project lacks verified production deployment, access control, monitoring/alerting, incident handling and recovery evidence.
6. **Audit integrity:** Review IDs, timestamps, generation mode, model name, prompt version and source SHA-256 are helpful but not immutable or digitally signed; storage access and lifecycle controls are not demonstrated.
7. **Dependency management:** Direct package versions were pinned and `pip check` passed. A complete lockfile, vulnerability scanning, CI checks and supported runtime patch policy remain unverified.
8. **Output naming:** The main application uses a fixed output filename and refuses overwrites. A production run strategy needs a unique, controlled output path per review or a governed record store.

## 6. Recommended release gates

### Portfolio v1.0 completion (development showcase)

- [x] Functional prototype with structured output and fallback
- [x] 19/19 recorded regression tests passed on Python 3.11
- [x] Ten synthetic LLM evaluations executed and scored
- [x] Raw-model governance failure documented, deterministic flag added
- [ ] Add a focused regression test showing raw `false` becomes `true` in **both** output fields
- [ ] Add rubric-based human scoring of all ten outputs for factual grounding and escalation quality
- [ ] Update README with clean setup/run/test/evaluation instructions and known limitations
- [ ] Demonstrate an end-to-end run using a new output path, given non-overwrite protection

### Additional gates before any real banking deployment

- [ ] Approve privacy/security and data-processing design for customer data
- [ ] Implement authenticated authorization and recorded human review/approval workflow
- [ ] Establish evidence provenance and approved risk/sanctions data controls
- [ ] Add representative labeled evaluation sets, adverse tests, release thresholds and monitoring
- [ ] Validate logging redaction, access restrictions, retention, encryption and audit integrity
- [ ] Implement supported deployment, CI/CD, secrets lifecycle, observability and incident recovery
- [ ] Complete independent model risk/compliance/security review and organizational sign-off

## 7. Proposed technical demonstration

Run the Python 3.11 environment tests, show one synthetic input, its deterministic metrics, the generated Pydantic-structured review, the evidence-validation status and source hash, and the human-review override. Show the EVAL-001 raw output as the concrete example of a model weakness mitigated by a deterministic application control. Present the 10-case scorecard with the narrow definitions above and make no claim of production certification.

## 8. Evidence basis and reproducibility

This report is based on terminal outputs, code snippets and score summaries supplied in the project conversation; the author has **not independently accessed the user's local Windows repository or all ten raw result files**. Scores and implementation claims should be rechecked against version-controlled source files and retained results before external publication.

Suggested local verification commands (from project root):

```powershell
.\.venv311\Scripts\python.exe -m pytest tests/ -v
.\.venv311\Scripts\python.exe evaluation/score_evaluations.py
Get-Content evaluation/evaluation_summary.json
```

**Release decision:** Candidate for final portfolio consolidation; **not approved or established as production-ready**.
