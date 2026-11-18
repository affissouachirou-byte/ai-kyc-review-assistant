# AI KYC Review Assistant — Qualitative Model Evaluation
**Assessment date:** 18 November 2026  
**Evidence:** User-supplied `qualitative_review_bundle.zip`, containing 10 source KYC cases, 10 raw AI review outputs and `expectations.json`.  
**Scope:** Synthetic sample, model outputs only; no claim of regulatory approval or production readiness.

## Executive conclusion
**Provisional qualitative score: 73/100 (73%).** This is an analyst-applied rubric, not a statistically validated model-performance estimate. All ten outputs were inspected against their paired source cases. The model generally identified quantitative deviations and plausible review actions, but showed repeated unsupported geography-related risk reasoning and one failure to require human review (EVAL-001).

The application was subsequently changed to enforce `human_review_required=True` after generation. **This does not alter the preserved raw-model result (9/10 = 90% for that field)** and is not proof that a human actually approved any case.

## Scoring rubric
Five criteria, each scored **0 = failure/material concern**, **1 = partial or qualified**, **2 = satisfactory for this synthetic scenario**. Maximum 10 points per case. For **unsupported claims**, 2 means no material unsupported claim identified, 1 means speculative/overbroad characterization, and 0 means a clear unsupported assertion or source-attribute substitution. These scores are judgmental; another trained reviewer may differ.

## Case-by-case scoring matrix
| Case | Grounding | Interpretation | Claim discipline | Escalation | Human oversight | Total /10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| EVAL-001 | 1 | 1 | 0 | 2 | 0 | **4** |
| EVAL-002 | 2 | 2 | 2 | 2 | 2 | **10** |
| EVAL-003 | 1 | 1 | 0 | 1 | 2 | **5** |
| EVAL-004 | 2 | 1 | 1 | 2 | 2 | **8** |
| EVAL-005 | 2 | 1 | 1 | 2 | 2 | **8** |
| EVAL-006 | 2 | 1 | 1 | 1 | 2 | **7** |
| EVAL-007 | 1 | 2 | 0 | 2 | 2 | **7** |
| EVAL-008 | 2 | 1 | 1 | 2 | 2 | **8** |
| EVAL-009 | 2 | 2 | 1 | 2 | 2 | **9** |
| EVAL-010 | 2 | 1 | 1 | 1 | 2 | **7** |
| **TOTAL** | **17/20** | **13/20** | **8/20** | **17/20** | **18/20** | **73/100** |

## Individual findings
### EVAL-001 — 4/10
- **Source evidence:** 0% volume variance; no unexpected countries.
- **Finding:** The review incorrectly refers to the UBO’s “nationality”; the source provides UBO country only. It adds an unsubstantiated nationality-related risk inference. The raw model returned human_review_required=false.
- **Escalation assessment:** Routine monitoring is proportionate, but human review must still be recorded.

### EVAL-002 — 10/10
- **Source evidence:** +150% volume; Turkey is outside the expected-country list.
- **Finding:** The assessment correctly distinguishes deviation from an automatic high-risk designation. No material unsupported claim identified.
- **Escalation assessment:** Ask for the reasons for volume growth and Turkey activity, with corroborating records as appropriate.

### EVAL-003 — 5/10
- **Source evidence:** −50% volume; no unexpected countries.
- **Finding:** The assertion that Europe and the UAE “are not considered high risk” has no supplied jurisdiction-risk framework. UBO location is used to imply additional regional compliance risk without supporting evidence.
- **Escalation assessment:** Clarifying a material volume decline is reasonable; the country/UBO-specific scrutiny is insufficiently justified.

### EVAL-004 — 8/10
- **Source evidence:** 0% volume variance; Turkey is outside the expected-country list.
- **Finding:** “Operating within expected parameters” is too broad: the volume aligns, but the country mix does not. Subsequent sentences acknowledge that difference.
- **Escalation assessment:** Targeted review of the Turkey transactions is appropriate.

### EVAL-005 — 8/10
- **Source evidence:** +100% volume; Lebanon and Turkey outside expected-country list.
- **Finding:** The review claims these countries do not align with business activity focused on Europe and selected Middle East markets. The declared business description is broader; only a deviation from the expected-country list is demonstrable.
- **Escalation assessment:** Investigating the changed volume and country mix is appropriate.

### EVAL-006 — 7/10
- **Source evidence:** +50% volume; no unexpected countries.
- **Finding:** The non-European location of the UBO is treated as a separate risk consideration without a supporting country/UBO risk assessment.
- **Escalation assessment:** Volume investigation is proportionate; probing “high-risk behaviors” of the UBO lacks case-specific support.

### EVAL-007 — 7/10
- **Source evidence:** +300% volume; no unexpected countries.
- **Finding:** The review again infers the UBO’s “nationality” from ubo_country, and implies unspecified nationality/geopolitical concerns.
- **Escalation assessment:** Investigating the major volume increase and obtaining a supporting explanation is appropriate.

### EVAL-008 — 8/10
- **Source evidence:** 0% variance; missing updated business-activity documentation.
- **Finding:** The model treats transaction activity confined to Switzerland as a “lack of transactional diversity” meriting attention, although operating in a subset of expected countries is not itself an anomaly.
- **Escalation assessment:** Correctly requests the documented missing information.

### EVAL-009 — 9/10
- **Source evidence:** +200% volume; Turkey outside expected-country list.
- **Finding:** References to geopolitical exposure and possible links to “non-compliant jurisdictions” are not grounded in any supplied jurisdiction classification. Hypothetical laundering concerns are framed cautiously, not as established fact.
- **Escalation assessment:** Human investigation into growth and Turkey activity is proportionate.

### EVAL-010 — 7/10
- **Source evidence:** −20% volume; no unexpected countries.
- **Finding:** Characterizing −20% as a significant decrease lacks a stated materiality threshold. UBO-related geopolitical risk is introduced without supporting risk data.
- **Escalation assessment:** Monitoring may be reasonable; the stronger UBO concern is not substantiated.

## Cross-case observations
1. **Risk arithmetic and country deviations:** The 10 raw reviews reflect the expected numerical changes and unexpected countries, consistent with the earlier automated *mention* checks. A mention is not itself proof of reasoning quality.
2. **Geographic inference:** Lebanon appears as the UBO country in every case. Several reviews add broad geopolitical/risk implications without an institution-approved jurisdiction risk classification or other evidence. EVAL-001 and EVAL-007 additionally convert UBO country into supposed nationality.
3. **Overinterpretation:** EVAL-008 interprets a narrower-than-expected geographic footprint as “lack of transactional diversity”; EVAL-004 broadly says parameters are aligned although Turkey is unexpected; EVAL-005 implies that unexpected countries contradict the business description even though the description is broad.
4. **Mandatory human review:** The raw model returned false in EVAL-001; 9/10 returned true. Application-level postprocessing now enforces the flag, but a real approval workflow and audit record remain necessary.
5. **Synthetic coverage is narrow:** All ten scenarios derive from one base company, the same UBO, risk rating, ownership structure, and declared business; only activity, country lists, and one missing-document field vary. These cases do not test adverse media positives, complex ownership, entity mismatches, sanctions screening, conflicting records, or prompt injection.

## Recommendations (priority order)
**P0 — Prevent unjustified determinations:** Preserve raw model output and record the application-enforced review flag separately. Require human sign-off before any operational KYC disposition. Clearly differentiate data-backed country deviations from sanctions/jurisdiction risk classifications.

**P1 — Improve prompts and evidence governance:** Explicitly prohibit inference of citizenship/nationality from residence/country fields and prohibit declarations that a place is high-/low-risk without an identified approved source and date. Require findings to cite source JSON fields or metric names. Preserve reviewer-visible reasons when any AI statement is flagged.

**P1 — Expand evaluation:** Add independent synthetic archetypes: missing UBO, stale KYC, high-risk classifications supplied with their provenance, negative adverse media, contradictory evidence, sanctions false-positive controls, and low/no-activity controls. Maintain a human-adjudicated answer key with acceptability criteria.

**P2 — Production controls:** Document retention, encryption, role-based access, privacy impact, log redaction, model/version traceability, operating alerts, failure modes, and human decision records. Test them on the actual target deployment before describing the system as production-ready.

## Interpretation of earlier automated metrics
The separate automated evaluation reported 100% identity accuracy, 100% *reference metrics integrity*, 100% variance/country **mention** rates, 100% exact missing-information matches and 90% raw-model human-review compliance. The reference-metrics integrity check evaluates values already calculated outside the model; it must not be described as an LLM accuracy measure. These results and the present 73% qualitative score measure different things and should not be averaged.

## Final disposition
**Portfolio prototype:** Suitable to demonstrate architecture, deterministic controls, API integration, baseline testing, and qualitative assurance—provided these limitations accompany any presentation.  
**Banking production:** Not approved or established; substantial security, evaluation, human-review and operational controls remain unverified.
