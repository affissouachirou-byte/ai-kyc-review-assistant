
import logging
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from risk_metrics import calculate_risk_metrics
from output_formatter import build_final_output
from save_review import save_review


def test_zero_expected_volume_rejected():
    case = {
        "expected_transaction_volume": {
            "monthly_volume_chf": 0,
            "expected_countries": ["Switzerland"],
        },
        "actual_transaction_summary": {
            "monthly_volume_chf": 100000,
            "observed_countries": ["Switzerland"],
        },
    }

    with pytest.raises(ValueError):
        calculate_risk_metrics(case)


def test_audit_hash_does_not_expose_source_data():
    source = {
        "customer_id": "SYNTHETIC-001",
        "risk_rating": "High",
    }

    output = build_final_output(
        review={"human_review_required": True},
        generation_mode="ai",
        model_used="gpt-4o-mini",
        source_data=source,
    )

    metadata = output["review_metadata"]

    assert len(metadata["source_data_sha256"]) == 64
    assert "SYNTHETIC-001" not in str(metadata)


def test_output_save_failure_preserves_existing_review(tmp_path):
    output_path = tmp_path / "review.json"

    save_review({"version": 1}, str(output_path))

    with pytest.raises(FileExistsError):
        save_review({"version": 2}, str(output_path))

    assert '"version": 1' in output_path.read_text(
        encoding="utf-8"
    )


def test_audit_requires_human_review():
    output = build_final_output(
        review={
            "customer_id": "SYNTHETIC-001",
            "human_review_required": False,
        },
        generation_mode="ai",
        model_used="gpt-4o-mini",
    )

    assert output["review_metadata"]["human_review_required"] is True


def test_logging_does_not_expose_api_key(caplog, monkeypatch):
    synthetic_secret = "SYNTHETIC_SECRET_DO_NOT_LOG"

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        synthetic_secret,
    )

    with caplog.at_level(logging.INFO):
        logging.info("KYC processing completed")

    assert synthetic_secret not in caplog.text
