
import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import main as kyc_app


@pytest.fixture
def test_workspace(tmp_path, monkeypatch):
    """Create an isolated workspace with synthetic data."""

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    shutil.copy2(
        PROJECT_ROOT / "data" / "kyc_case_001.json",
        data_dir / "kyc_case_001.json",
    )

    monkeypatch.chdir(tmp_path)
    return tmp_path


def read_output(workspace):
    output_path = (
        workspace / "outputs" / "kyc_review_001.json"
    )

    assert output_path.exists()

    return json.loads(
        output_path.read_text(encoding="utf-8")
    )


def test_api_failure_triggers_fallback(
    test_workspace, monkeypatch
):
    """Verify the complete fallback workflow."""

    def simulate_api_failure(prompt):
        raise kyc_app.KYCTransientError(
        "Simulated temporary API failure"
    )

    monkeypatch.setattr(
        kyc_app,
        "generate_ai_kyc_review",
        simulate_api_failure,
    )

    kyc_app.main()

    result = read_output(test_workspace)

    assert (
        result["review_metadata"]["generation_mode"]
        == "deterministic_fallback"
    )

    assert result["review_metadata"]["human_review_required"] is True
    assert "kyc_review" in result
    assert "evidence_validation" in result


def test_successful_ai_workflow(
    test_workspace, monkeypatch
):
    """Verify the complete workflow using a mocked AI response."""

    synthetic_review = {
        "customer_id": "CUST-001",
        "customer_name": "Alpine Global Trading AG",
        "risk_summary": "Observed volume exceeds expected volume.",
        "key_risk_indicators": [
            "Transaction volume variance of 150%",
            "Turkey is outside expected transaction countries",
        ],
        "missing_information": [],
        "recommended_action": "Refer for human review.",
        "rationale": "Observed activity differs from declared expectations.",
        "human_review_required": True,
    }

    def simulate_ai_success(prompt):
        assert "150.0" in prompt
        return SimpleNamespace(
            model_dump=lambda: synthetic_review.copy()
        )

    monkeypatch.setattr(
        kyc_app,
        "generate_ai_kyc_review",
        simulate_ai_success,
    )

    kyc_app.main()

    result = read_output(test_workspace)

    assert result["review_metadata"]["generation_mode"] == "ai"
    assert result["review_metadata"]["human_review_required"] is True
    assert result["kyc_review"]["customer_id"] == "CUST-001"
    assert "evidence_validation" in result
