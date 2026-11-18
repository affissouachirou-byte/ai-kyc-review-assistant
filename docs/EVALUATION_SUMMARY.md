# AI KYC Review Assistant — Consolidated Evaluation

**Status:** Final portfolio consolidation | **Date:** 18 November 2026  
**Source basis:** User-supplied 10-case v0.1 evaluation bundle and recorded v0.2 execution/validator outputs. No new generation or independent deployment audit was performed for this document.

## Test baseline

**19/19 pytest tests passed** in the Python 3.11 virtual environment. Covered scenarios include input validation, arithmetic, fallback with simulated API failures, critical error stops, output metadata and non-overwrite behavior. These are not a comprehensive security or production qualification.

## Prompt v0.1 baseline

- 10/10 synthetic API-generated reviews completed.
- Automated scorecard: identity 100%; deterministic reference-metric consistency 100%; variance *mention* 100%; unexpected-country *mention* 100%; documented missing-information exact match 100%; raw-model human-review flag 90%.
- Independent of those automated checks, analyst-applied qualitative rubric: **73/100** over 10 reviews and five 0–2 criteria (factual grounding 17/20; risk interpretation 13/20; unsupported-claim discipline 8/20; escalation quality 17/20; human oversight 18/20).
- Main errors: unsupported UBO nationality/geographic risk inferences; one raw model `human_review_required: false` (EVAL-001); occasional overinterpretation of deviations.

The v0.1 score is **judgment-based**, not a validated performance estimate. The 100% reference-metrics score measures precomputed numbers, **not** model intelligence or accuracy.

## Prompt v0.2 — preliminary comparison

Prompt v0.2 explicitly prohibits inferring citizenship/nationality from UBO country, ungrounded country classifications and unsupported geopolitical conclusions. The application enforces the human-review flag after generation.

| Measure | v0.1 | v0.2 | Qualification |
|---|---:|---:|---|
| API evaluations completed | 10/10 | 10/10 | Reported execution counts |
| Cases flagged by enhanced regex validator | 6/10 | 1/10 | Detection flags; **not** hallucination frequency or accuracy |
| Human review, raw model | 9/10 true | Not scored across all 10 here | Must distinguish raw vs enforced flag |
| Qualitative rubric | 73/100 | Not yet scored | **Do not** claim a scored quality improvement |

The single v0.2 flag was **EVAL-007**. Its text explicitly said the UBO's country *does not infer any nationality or geopolitical risk*. The validator still flagged nationality and geopolitical terms because it lacked negation handling. That is a documented **false positive**. The output correctly reported a +300% transaction-volume difference, no unexpected countries and human review required. The remaining nine v0.2 outputs have not been manually reviewed for all substantive claims in this consolidation.

## Governance conclusion

The project demonstrates a useful distinction between (a) prompt instructions, (b) deterministic calculations and application-level enforcement, and (c) limited post-generation quality flags. None of these substitutes for a human KYC disposition or production assurance.

**Portfolio disposition:** Suitable for demonstration with limitations prominently disclosed.  
**Production disposition:** Not established; requires data-handling/security design, governed human approvals, comprehensive evaluation, deployment monitoring and independent controls testing.

## Documentation/versioning rules

- Keep original v0.1 evaluation outputs unchanged as the baseline.
- Keep v0.2 outputs separately; do not rewrite raw model flags.
- Identify prompt version in new outputs. Document validator limitations instead of repeatedly customizing rules to isolated phrases.
- Do not claim v0.2 quantitative model improvement from regex flag counts alone.
