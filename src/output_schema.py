from pydantic import BaseModel
from typing import List


class KYCReviewOutput(BaseModel):
    customer_id: str
    customer_name: str
    risk_summary: str
    key_risk_indicators: List[str]
    missing_information: List[str]
    recommended_action: str
    rationale: str
    human_review_required: bool