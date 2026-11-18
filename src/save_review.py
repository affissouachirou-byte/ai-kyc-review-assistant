
import json
import os
import tempfile
from pathlib import Path


def save_review(review: dict, output_path: str) -> None:
    """
    Save a KYC review atomically without overwriting
    an existing review.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        raise FileExistsError(
            f"Review already exists: {path}"
        )

    # Prepare JSON before writing
    content = json.dumps(review, indent=2)

    temp_path = None

    try:
        # Create a temporary file in the same directory
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".kyc_tmp_",
            suffix=".json",
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)

        # Create the final file without replacing an existing file
        os.link(temp_path, path)

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
