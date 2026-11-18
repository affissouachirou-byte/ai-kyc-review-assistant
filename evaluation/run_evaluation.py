
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prompt_builder import build_kyc_review_prompt
from llm_client import generate_ai_kyc_review
from risk_metrics import calculate_risk_metrics


def main():
    cases_dir = ROOT / "evaluation" / "cases"
    results_dir = ROOT / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    expectations = json.loads(
        (ROOT / "evaluation" / "expectations.json")
        .read_text(encoding="utf-8")
    )

    completed = 0
    failed = 0

    for case_path in sorted(cases_dir.glob("EVAL-*.json")):
        case = json.loads(case_path.read_text(encoding="utf-8"))
        case_id = case["customer_id"]
        output_path = results_dir / f"{case_id}_review.json"

        if output_path.exists():
            print(f"{case_id}: SKIPPED (result already exists)")
            continue

        try:
            metrics = calculate_risk_metrics(case)
            expected = expectations[case_id]

            # Verify the reference dataset before calling the LLM.
            if (
                metrics["volume_variance_pct"]
                != expected["expected_variance_pct"]
                or metrics["unexpected_countries"]
                != expected["unexpected_countries"]
            ):
                raise ValueError("Evaluation reference mismatch")

            prompt = build_kyc_review_prompt(case)
            ai_review = generate_ai_kyc_review(prompt)

            result = {
                "case_id": case_id,
                "verified_metrics": metrics,
                "expected_findings": expected,
                "ai_review": ai_review.model_dump(),
            }

            # Create a new file without replacing previous results.
            with output_path.open("x", encoding="utf-8") as file:
                json.dump(result, file, indent=2)

            completed += 1
            print(f"{case_id}: COMPLETED")

        except Exception as error:
            failed += 1
            print(f"{case_id}: FAILED ({type(error).__name__})")

    print(f"\nCompleted: {completed}")
    print(f"Failed: {failed}")
    print(f"Results directory: {results_dir}")


if __name__ == "__main__":
    main()
