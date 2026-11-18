
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "evaluation"
RESULTS_DIR = EVAL_DIR / "results"


def normalize_items(items):
    return {
        str(item).strip().casefold()
        for item in items
    }


def assess_case(result):
    case_id = result["case_id"]
    expected = result["expected_findings"]
    metrics = result["verified_metrics"]
    review = result["ai_review"]

    summary = review.get("risk_summary", "")
    indicators = review.get("key_risk_indicators", [])
    rationale = review.get("rationale", "")

    assessment_text = " ".join([
        summary,
        " ".join(indicators),
        rationale,
    ])

    # 1. Customer identity
    identity_pass = review.get("customer_id") == case_id

    # 2. Transaction variance reporting
    variance = expected["expected_variance_pct"]

    if variance == 0:
        variance_status = "NOT_APPLICABLE"
    else:
        number = f"{abs(variance):g}"
        pattern = rf"(?<!\d){re.escape(number)}(?:\.0+)?\s*%"

        variance_status = (
            "MENTIONED"
            if re.search(pattern, assessment_text)
            else "NOT_MENTIONED"
        )

    # 3. Unexpected country identification
    unexpected = expected["unexpected_countries"]

    if unexpected:
        countries_mentioned = all(
            re.search(
                rf"\b{re.escape(country)}\b",
                assessment_text,
                flags=re.IGNORECASE,
            )
            for country in unexpected
        )

        country_status = (
            "MENTIONED"
            if countries_mentioned
            else "NOT_MENTIONED"
        )
    else:
        country_status = "NOT_APPLICABLE"

    # 4. Documented missing information
    expected_missing = normalize_items(
        expected["documented_missing_information"]
    )

    reported_missing = normalize_items(
        review.get("missing_information", [])
    )

    missing_info_pass = expected_missing == reported_missing

    # 5. Human review
    human_review_pass = (
        review.get("human_review_required") is True
    )

    # 6. Check consistency of reference metrics
    reference_pass = (
        metrics["volume_variance_pct"]
        == expected["expected_variance_pct"]
        and metrics["unexpected_countries"]
        == expected["unexpected_countries"]
    )

    # Exact, machine-checkable criteria
    objective_checks = [
        identity_pass,
        missing_info_pass,
        human_review_pass,
        reference_pass,
    ]

    objective_score = round(
        100 * sum(objective_checks) / len(objective_checks),
        1,
    )

    return {
        "case_id": case_id,
        "identity_pass": identity_pass,
        "reference_metrics_pass": reference_pass,
        "variance_status": variance_status,
        "unexpected_country_status": country_status,
        "missing_information_pass": missing_info_pass,
        "human_review_pass": human_review_pass,
        "objective_score_pct": objective_score,
        "qualitative_review_required": True,
    }


def main():
    assessments = []

    for path in sorted(RESULTS_DIR.glob("EVAL-*_review.json")):
        result = json.loads(
            path.read_text(encoding="utf-8")
        )
        assessments.append(assess_case(result))

    if not assessments:
        raise RuntimeError("No evaluation results found.")

    # Write detailed CSV
    csv_path = EVAL_DIR / "evaluation_scorecard.csv"

    with csv_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(assessments[0].keys()),
        )
        writer.writeheader()
        writer.writerows(assessments)

    def rate(key, expected_value=True):
        return round(
            100 * sum(
                row[key] == expected_value
                for row in assessments
            ) / len(assessments),
            1,
        )

    def mention_rate(key):
        applicable = [
            row for row in assessments
            if row[key] != "NOT_APPLICABLE"
        ]
        if not applicable:
            return None

        return round(
            100 * sum(
                row[key] == "MENTIONED"
                for row in applicable
            ) / len(applicable),
            1,
        )

    summary = {
        "cases_evaluated": len(assessments),
        "identity_accuracy_pct": rate("identity_pass"),
        "reference_metrics_integrity_pct": rate(
            "reference_metrics_pass"
        ),
        "variance_mention_rate_pct": mention_rate(
            "variance_status"
        ),
        "unexpected_country_mention_rate_pct": mention_rate(
            "unexpected_country_status"
        ),
        "missing_information_accuracy_pct": rate(
            "missing_information_pass"
        ),
        "human_review_compliance_pct": rate(
            "human_review_pass"
        ),
        "qualitative_assessment": "HUMAN_REVIEW_REQUIRED",
    }

    json_path = EVAL_DIR / "evaluation_summary.json"
    json_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print("\nFiles created:")
    print(csv_path)
    print(json_path)


if __name__ == "__main__":
    main()
