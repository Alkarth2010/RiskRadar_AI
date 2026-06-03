from pydantic import BaseModel
from typing import List, Optional


class FraudAlert(BaseModel):
    transaction_id: str
    amount: float
    country: str
    new_device: bool
    transactions_last_10min: int
    merchant_category: Optional[str] = None
    triggered_rules: Optional[list[str]] = None


class InvestigationResult(BaseModel):
    risk_score: str

    risk_reasoning: str

    triggered_policies: List[str]

    investigation_summary: str

    recommended_action: str

    sources: List[str]

    action_reason: str

    error: str = ""