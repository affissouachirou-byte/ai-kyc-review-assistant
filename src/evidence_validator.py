
import json
import re
from pathlib import Path


def validate_ai_evidence(case_data: dict, review: dict) -> dict:
    """
    Flag selected unsupported AI claims.
    Preserve the original assessment.
    """

    findings = []
    assessment = review["kyc_review"]

    assessment_text = " ".join([
        str(assessment.get("risk_summary", "")),
        " ".join(
            str(x) for x in
            assessment.get("key_risk_indicators", [])
        ),
        str(assessment.get("rationale", "")),
        str(assessment.get("recommended_action", "")),
    ])

    text = assessment_text.casefold()

    ubo = case_data.get("ubo_information", {})
    ubo_country = str(
        ubo.get("ubo_country", "")
    ).casefold()

    classifications = case_data.get(
        "jurisdiction_risk_classifications"
    )

    # 1. Detect unsupported nationality inference
    nationality_documented = bool(
        ubo.get("nationality")
        or ubo.get("citizenship")
    )

    if (
        not nationality_documented
        and re.search(r"\bnationalit(?:y|ies)\b|\bcitizenship\b", text)
    ):
        findings.append({
            "check": "UNSUPPORTED_NATIONALITY",
            "status": "FLAG",
            "message": (
                "AI refers to nationality or citizenship "
                "without corresponding source evidence."
            ),
        })

    # 2. Detect selected unsupported jurisdiction classifications
    classification_claim = bool(
        re.search(
            r"\bhigh[- ]risk jurisdiction\b"
            r"|\blow[- ]risk jurisdiction\b"
            r"|\bnot considered high risk\b"
            r"|\bclassified as (?:high|low)[- ]risk\b",
            text,
        )
    )

    if classification_claim and not classifications:
        findings.append({
            "check": "UBO_COUNTRY_RISK",
            "status": "FLAG",
            "message": (
                "Jurisdiction risk characterization requires "
                "an approved, documented classification."
            ),
        })

    # 3. Detect speculative geopolitical risk reasoning
    geopolitical_claim = bool(
        re.search(
            r"\bgeopolitical (?:risk|exposure|considerations)\b"
            r"|\bregional risks?\b",
            text,
        )
    )

    if geopolitical_claim and not classifications:
        findings.append({
            "check": "UNSUPPORTED_GEOGRAPHIC_INFERENCE",
            "status": "FLAG",
            "message": (
                "Geopolitical or regional risk reasoning "
                "requires supporting case evidence."
            ),
        })

    # 4. Detect unsupported transactional-diversity concerns
    expected_countries = set(
        case_data["expected_transaction_volume"][
            "expected_countries"
        ]
    )
    observed_countries = set(
        case_data["actual_transaction_summary"][
            "observed_countries"
        ]
    )

    if (
        observed_countries.issubset(expected_countries)
        and "lack of transactional diversity" in text
    ):
        findings.append({
            "check": "UNSUPPORTED_DIVERSITY_RISK",
            "status": "FLAG",
            "message": (
                "Operating in a subset of expected countries "
                "is not, by itself, a risk indicator."
            ),
        })

    # 5. Flag inconsistent human review requirement
    if assessment.get("human_review_required") is not True:
        findings.append({
            "check": "HUMAN_REVIEW",
            "status": "FLAG",
            "message": (
                "The KYC assessment must require human review."
            ),
        })

    # 6. Clarify missing information
    if not assessment.get("missing_information", []):
        findings.append({
            "check": "MISSING_INFORMATION",
            "status": "INFO",
            "message": (
                "No missing information reported. "
                "Additional investigation needs should "
                "be tracked separately."
            ),
        })

    has_flags = any(
        item["status"] == "FLAG"
        for item in findings
    )

    return {
        "validation_status": (
            "REVIEW_REQUIRED"
            if has_flags
            else "PASSED_WITH_LIMITED_CHECKS"
        ),
        "findings": findings,
        "checks_performed": 6,
        "human_review_required": True,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]

    case_data = json.loads(
        (root / "data/kyc_case_001.json").read_text(
            encoding="utf-8"
        )
    )

    review = json.loads(
        (root / "outputs/kyc_review_001.json").read_text(
            encoding="utf-8"
        )
    )

    print(json.dumps(
        validate_ai_evidence(case_data, review),
        indent=2,
    ))
