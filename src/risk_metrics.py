
def calculate_risk_metrics(kyc_case: dict) -> dict:
    """Calculate objective KYC transaction metrics."""

    expected = kyc_case["expected_transaction_volume"]["monthly_volume_chf"]
    actual = kyc_case["actual_transaction_summary"]["monthly_volume_chf"]

    if expected <= 0:
        raise ValueError("Expected monthly volume must be greater than zero.")

    variance_chf = actual - expected
    variance_pct = (variance_chf / expected) * 100

    expected_countries = set(
        kyc_case["expected_transaction_volume"]["expected_countries"]
    )
    observed_countries = set(
        kyc_case["actual_transaction_summary"]["observed_countries"]
    )

    unexpected_countries = sorted(
        observed_countries - expected_countries
    )

    return {
        "expected_monthly_volume_chf": expected,
        "actual_monthly_volume_chf": actual,
        "volume_variance_chf": variance_chf,
        "volume_variance_pct": round(variance_pct, 2),
        "unexpected_countries": unexpected_countries,
    }
