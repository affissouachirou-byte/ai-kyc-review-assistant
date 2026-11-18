import json
from pathlib import Path


def load_kyc_case(file_path: str) -> dict:
    """
    Load a KYC case from a JSON file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"KYC case file not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        case_data = json.load(file)

    return case_data