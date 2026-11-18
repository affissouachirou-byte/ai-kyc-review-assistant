
import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4


def build_final_output(
    review: dict,
    generation_mode: str,
    model_used: str,
    review_version: str = "v0.1",
    source_data: dict | None = None,
    prompt_version: str = "v0.1",
) -> dict:
    """
    Build structured KYC review output with audit metadata.
    """

    source_hash = None

    if source_data is not None:
        canonical_data = json.dumps(
            source_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        source_hash = hashlib.sha256(
            canonical_data.encode("utf-8")
        ).hexdigest()

    return {
        "review_metadata": {
            "review_id": str(uuid4()),
            "generation_mode": generation_mode,
            "model_used": model_used,
            "review_version": review_version,
            "prompt_version": prompt_version,
            "generated_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "source_data_sha256": source_hash,
            "human_review_required": True,
        },
        "kyc_review": review,
    }
