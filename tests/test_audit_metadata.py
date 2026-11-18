
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from output_formatter import build_final_output


def test_audit_metadata():
    source = {"customer_id": "CUST-001", "risk_rating": "Medium"}
    review = {"customer_id": "CUST-001", "human_review_required": True}

    first = build_final_output(
        review=review,
        generation_mode="ai",
        model_used="gpt-4o-mini",
        source_data=source,
        prompt_version="v0.1",
    )

    second = build_final_output(
        review=review,
        generation_mode="ai",
        model_used="gpt-4o-mini",
        source_data=source,
        prompt_version="v0.1",
    )

    metadata = first["review_metadata"]

    # Verify unique, valid review identifiers
    UUID(metadata["review_id"])
    assert metadata["review_id"] != second["review_metadata"]["review_id"]

    # Verify stable source fingerprint
    assert metadata["source_data_sha256"] == (
        second["review_metadata"]["source_data_sha256"]
    )
    assert len(metadata["source_data_sha256"]) == 64

    # Verify required audit fields
    assert metadata["generation_mode"] == "ai"
    assert metadata["model_used"] == "gpt-4o-mini"
    assert metadata["prompt_version"] == "v0.1"
    assert metadata["human_review_required"] is True


def test_source_change_modifies_hash():
    review = {"human_review_required": True}

    first = build_final_output(
        review=review,
        generation_mode="ai",
        model_used="gpt-4o-mini",
        source_data={"risk_rating": "Medium"},
    )

    second = build_final_output(
        review=review,
        generation_mode="ai",
        model_used="gpt-4o-mini",
        source_data={"risk_rating": "High"},
    )

    assert (
        first["review_metadata"]["source_data_sha256"]
        != second["review_metadata"]["source_data_sha256"]
    )
