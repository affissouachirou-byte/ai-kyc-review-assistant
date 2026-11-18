REQUIRED_FIELDS = [
    "customer_id",
    "customer_name",
    "country",
    "customer_type",
    "risk_rating",
    "declared_activity",
    "expected_transaction_volume",
    "actual_transaction_summary",
    "ubo_information",
    "adverse_media_summary",
    "missing_information",
]


VALID_RISK_RATINGS = {"Low", "Medium", "High"}


def validate_kyc_case(case_data: dict) -> dict:
    """
    Validate that the KYC case contains the required fields
    and acceptable values.
    """

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if field not in case_data
    ]

    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    empty_fields = [
        field
        for field in REQUIRED_FIELDS
        if case_data.get(field) in [None, "", []]
        and field != "missing_information"
    ]

    if empty_fields:
        raise ValueError(f"Empty required fields: {empty_fields}")

    risk_rating = case_data["risk_rating"]

    if risk_rating not in VALID_RISK_RATINGS:
        raise ValueError(
            f"Invalid risk rating: {risk_rating}. "
            f"Expected one of: {VALID_RISK_RATINGS}"
        )

    return case_data