
import shutil
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import main as kyc_app


@pytest.fixture
def isolated_workspace(tmp_path, monkeypatch):
    """Use isolated synthetic data and output directories."""

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    shutil.copy2(
        PROJECT_ROOT / "data" / "kyc_case_001.json",
        data_dir / "kyc_case_001.json",
    )

    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize(
    "error_type",
    [
        kyc_app.KYCConfigurationError,
        kyc_app.KYCResponseError,
        RuntimeError,
    ],
    ids=[
        "invalid_api_configuration",
        "invalid_ai_response",
        "unexpected_programming_error",
    ],
)
def test_critical_errors_stop_without_fallback(
    isolated_workspace,
    monkeypatch,
    error_type,
):
    """Critical failures must stop without saving a review."""

    def simulate_failure(prompt):
        raise error_type("Synthetic failure")

    def unexpected_fallback(case_data):
        pytest.fail(
            "Deterministic fallback must not run "
            "for critical errors."
        )

    monkeypatch.setattr(
        kyc_app,
        "generate_ai_kyc_review",
        simulate_failure,
    )

    monkeypatch.setattr(
        kyc_app,
        "generate_kyc_review",
        unexpected_fallback,
    )

    # A critical failure should exit unsuccessfully.
    with pytest.raises(SystemExit) as exc:
        kyc_app.main()

    assert exc.value.code == 1

    # No review must be created after the failure.
    output_path = (
        isolated_workspace
        / "outputs"
        / "kyc_review_001.json"
    )

    assert not output_path.exists()
