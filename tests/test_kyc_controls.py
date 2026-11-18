
import sys
import unittest
from pathlib import Path

# Locate project modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from risk_metrics import calculate_risk_metrics
from evidence_validator import validate_ai_evidence


class TestKYCControls(unittest.TestCase):

    def setUp(self):
        """Create synthetic KYC test data."""

        self.case_data = {
            "expected_transaction_volume": {
                "monthly_volume_chf": 500000,
                "expected_countries": [
                    "Switzerland", "Germany", "France"
                ],
            },
            "actual_transaction_summary": {
                "monthly_volume_chf": 1250000,
                "observed_countries": [
                    "Switzerland", "Germany", "Turkey"
                ],
            },
            "ubo_information": {
                "ubo_country": "Lebanon"
            },
            "missing_information": [],
        }

    def test_risk_metrics(self):
        """Verify deterministic calculations."""

        result = calculate_risk_metrics(self.case_data)

        self.assertEqual(result["volume_variance_pct"], 150.0)
        self.assertEqual(result["volume_variance_chf"], 750000)
        self.assertEqual(result["unexpected_countries"], ["Turkey"])

    def test_unsupported_country_risk(self):
        """Verify detection of unsupported AI claims."""

        review = {
            "kyc_review": {
                "risk_summary": "",
                "key_risk_indicators": [
                    "Ownership by UBO from a high-risk jurisdiction (Lebanon)"
                ],
                "rationale": "",
                "missing_information": [],
            }
        }

        result = validate_ai_evidence(self.case_data, review)

        self.assertEqual(
            result["validation_status"],
            "REVIEW_REQUIRED"
        )

        self.assertTrue(
            any(
                finding["check"] == "UBO_COUNTRY_RISK"
                and finding["status"] == "FLAG"
                for finding in result["findings"]
            )
        )

    def test_human_review_required(self):
        """Verify human oversight remains mandatory."""

        review = {
            "kyc_review": {
                "risk_summary": "Transaction volume increased.",
                "key_risk_indicators": [],
                "rationale": "",
                "missing_information": [],
            }
        }

        result = validate_ai_evidence(self.case_data, review)

        self.assertTrue(result["human_review_required"])


if __name__ == "__main__":
    unittest.main()
