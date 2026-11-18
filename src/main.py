
import logging
from pathlib import Path

from load_case import load_kyc_case
from validate_case import validate_kyc_case
from review_generator import generate_kyc_review
from prompt_builder import build_kyc_review_prompt
from llm_client import (
    generate_ai_kyc_review,
    MODEL_NAME,
    KYCTransientError,
    KYCConfigurationError,
    KYCResponseError,
)
from save_review import save_review
from output_formatter import build_final_output
from evidence_validator import validate_ai_evidence


def configure_logging() -> None:
    """Configure application logging."""

    log_path = Path("logs/app.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def main() -> None:
    """Run the AI KYC Review Assistant."""

    configure_logging()

    input_path = "data/kyc_case_001.json"
    output_path = "outputs/kyc_review_001.json"

    try:
        logging.info("Application started.")

        # Load and validate the KYC case
        case_data = load_kyc_case(input_path)
        validated_case = validate_kyc_case(case_data)

        # Build prompt with deterministic risk metrics
        prompt = build_kyc_review_prompt(validated_case)

        # Generate AI assessment or controlled fallback
        try:
            ai_review = generate_ai_kyc_review(prompt)
            review_dict = ai_review.model_dump()

            generation_mode = "ai"
            model_used = MODEL_NAME

            logging.info("AI review generated.")

        except KYCTransientError:
            logging.warning(
                "Temporary AI failure. Deterministic fallback activated."
            )

            review_dict = generate_kyc_review(validated_case)
            generation_mode = "deterministic_fallback"
            model_used = "not_used_due_to_llm_error"

        except KYCConfigurationError:
            logging.error("AI configuration failure.")
            raise

        except KYCResponseError:
            logging.error("AI response validation failure.")
            raise

        # Mandatory human oversight
        if review_dict.get("human_review_required") is not True:
            logging.warning(
                "Human-review requirement enforced."
            )

        review_dict["human_review_required"] = True

        # Build auditable output
        final_output = build_final_output(
            review=review_dict,
            generation_mode=generation_mode,
            model_used=model_used,
            source_data=validated_case,
            prompt_version="v0.2",
        )

        # Evidence validation
        evidence_validation = validate_ai_evidence(
            case_data=validated_case,
            review=final_output,
        )

        final_output["evidence_validation"] = evidence_validation

        logging.info(
            "Evidence validation completed: %s",
            evidence_validation["validation_status"],
        )

        # Save final output
        save_review(final_output, output_path)

        logging.info("KYC review saved successfully.")

        print("KYC case loaded successfully.")
        print("Validation passed.")
        print("Prompt built successfully.")
        print(f"Generation mode: {generation_mode}")
        print(
            "Evidence validation: "
            f"{evidence_validation['validation_status']}"
        )
        print("Final auditable output built.")
        print(f"Review saved to: {output_path}")
        print("Log written to: logs/app.log")

    except Exception as error:
        logging.error(
            "Application failed. Error category: %s",
            type(error).__name__,
        )

        print("Application failed.")
        print("Check logs/app.log for the error category.")

        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
