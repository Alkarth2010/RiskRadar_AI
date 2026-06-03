from pydantic import BaseModel
from typing import List


class InvestigationAlert(BaseModel):
    transaction_id: str
    customer_id: str

    amount: float
    location: str

    severity: str

    triggered_rules: List[str]

    new_device: bool = False
    velocity_count: int = 0
    geographic_anomaly: bool = False