
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

source = json.loads(
    (ROOT / "data" / "kyc_case_001.json").read_text(
        encoding="utf-8"
    )
)

cases_dir = ROOT / "evaluation" / "cases"
cases_dir.mkdir(parents=True, exist_ok=True)

# Scenario ID, actual CHF, observed countries,
# expected variance %, unexpected countries
scenarios = [
    ("EVAL-001", 500000, ["Switzerland", "Germany"], 0, []),
    ("EVAL-002", 1250000, ["Switzerland", "Turkey"], 150, ["Turkey"]),
    ("EVAL-003", 250000, ["Switzerland"], -50, []),
    ("EVAL-004", 500000, ["Switzerland", "Turkey"], 0, ["Turkey"]),
    ("EVAL-005", 1000000, ["Turkey", "Lebanon"], 100, ["Lebanon", "Turkey"]),
    ("EVAL-006", 750000, ["Germany", "France"], 50, []),
    ("EVAL-007", 2000000, ["Switzerland"], 300, []),
    ("EVAL-008", 500000, ["Switzerland"], 0, []),
    ("EVAL-009", 1500000, ["France", "Turkey"], 200, ["Turkey"]),
    ("EVAL-010", 400000, ["Germany", "United Arab Emirates"], -20, []),
]

expectations = {}

for case_id, actual, countries, variance, unexpected in scenarios:
    case = copy.deepcopy(source)

    case["customer_id"] = case_id
    case["actual_transaction_summary"]["monthly_volume_chf"] = actual
    case["actual_transaction_summary"]["observed_countries"] = countries
    case["actual_transaction_summary"]["notable_change"] = (
        "Synthetic evaluation scenario; assess against expected activity."
    )

    if case_id == "EVAL-008":
        case["missing_information"] = [
            "Updated business activity documentation"
        ]

    case_path = cases_dir / f"{case_id}.json"

    case_path.write_text(
        json.dumps(case, indent=2),
        encoding="utf-8",
    )

    expectations[case_id] = {
        "expected_variance_pct": variance,
        "unexpected_countries": unexpected,
        "documented_missing_information": case["missing_information"],
    }

(ROOT / "evaluation" / "expectations.json").write_text(
    json.dumps(expectations, indent=2),
    encoding="utf-8",
)

print(f"Created {len(scenarios)} synthetic evaluation cases.")
print("Expected analytical findings saved.")
