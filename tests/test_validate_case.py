import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from validate_case import validate_kyc_case


def build_valid_case() -> dict:
    return {
        "customer_id": "CUST-001",
        "customer_name": "Alpine Global Trading AG",
        "country": "Switzerland",
        "customer_type": "Corporate",
        "risk_rating": "Medium",
        "declared_activity": "Import and export of industrial equipment.",
        "expected_transaction_volume": {
            "monthly_volume_chf": 500000,
            "expected_countries": ["Switzerland", "Germany"],
        },
        "actual_transaction_summary": {
            "monthly_volume_chf": 750000,
            "observed_countries": ["Switzerland", "Germany"],
        },
        "ubo_information": {
            "ubo_name": "Karim Haddad",
            "ubo_country": "Lebanon",
            "ownership_percentage": 75,
        },
        "adverse_media_summary": "No confirmed adverse media identified.",
        "missing_information": [],
    }


def test_validate_kyc_case_passes_with_valid_case():
    valid_case = build_valid_case()

    result = validate_kyc_case(valid_case)

    assert result["customer_id"] == "CUST-001"
    assert result["risk_rating"] == "Medium"


def test_validate_kyc_case_fails_when_required_field_is_missing():
    invalid_case = build_valid_case()
    invalid_case.pop("risk_rating")

    with pytest.raises(ValueError, match="Missing required fields"):
        validate_kyc_case(invalid_case)


def test_validate_kyc_case_fails_with_invalid_risk_rating():
    invalid_case = build_valid_case()
    invalid_case["risk_rating"] = "Very High"

    with pytest.raises(ValueError, match="Invalid risk rating"):
        validate_kyc_case(invalid_case)