
import sys
import json
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from save_review import save_review


def test_existing_review_cannot_be_overwritten(tmp_path):
    output_path = tmp_path / "review.json"

    # Save the original review
    save_review({"version": 1}, str(output_path))

    # Attempt to overwrite it
    with pytest.raises(FileExistsError):
        save_review({"version": 2}, str(output_path))

    # Verify original content remains unchanged
    saved_review = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert saved_review == {"version": 1}
