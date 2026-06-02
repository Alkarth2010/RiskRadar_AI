from src.fraud.models import FraudAlert
from src.fraud.risk_engine import calculate_risk


alert = FraudAlert(
    transaction_id="TXN001",
    amount=250000,
    country="Russia",
    new_device=True,
    transactions_last_10min=15
)

result = calculate_risk(alert)

print(result)