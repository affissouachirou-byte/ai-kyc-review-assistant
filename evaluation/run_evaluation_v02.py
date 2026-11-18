
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prompt_builder import (
    build_kyc_review_prompt,
    PROMPT_VERSION,
)
from llm_client import generate_ai_kyc_review, MODEL_NAME
from risk_metrics import calculate_risk_metrics
from evidence_validator import validate_ai_evidence


def main():
    cases_dir = ROOT / "evaluation" / "cases"
    results_dir = ROOT / "evaluation" / "results_v02"
    results_dir.mkdir(parents=True, exist_ok=True)

    completed = 0
    failed = 0
    skipped = 0

    for case_path in sorted(cases_dir.glob("EVAL-*.json")):
        case = json.loads(
            case_path.read_text(encoding="utf-8")
        )

        case_id = case["customer_id"]
        output_path = results_dir / f"{case_id}_review.json"

        if output_path.exists():
            print(f"{case_id}: SKIPPED")
            skipped += 1
            continue

        try:
            metrics = calculate_risk_metrics(case)
            prompt = build_kyc_review_prompt(case)

            ai_review = generate_ai_kyc_review(prompt)
            raw_review = ai_review.model_dump()

            # Validate original model output before enforcement
            evidence_validation = validate_ai_evidence(
                case_data=case,
                review={"kyc_review": raw_review},
            )

            result = {
                "case_id": case_id,
                "prompt_version": PROMPT_VERSION,
                "model_used": MODEL_NAME,
                "generated_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "verified_metrics": metrics,
                "ai_review": raw_review,
                "evidence_validation": evidence_validation,
            }

            # Exclusive creation prevents overwriting
            with output_path.open("x", encoding="utf-8") as file:
                json.dump(result, file, indent=2)

            completed += 1

            status = evidence_validation["validation_status"]

            print(f"{case_id}: COMPLETED | {status}")

        except Exception as error:
            failed += 1
            print(
                f"{case_id}: FAILED "
                f"({type(error).__name__})"
            )

    print("\nEvaluation v0.2 completed.")
    print(f"Completed: {completed}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Results: {results_dir}")


if __name__ == "__main__":
    main()
