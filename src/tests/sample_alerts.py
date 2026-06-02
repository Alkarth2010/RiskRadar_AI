from src.fraud.models import FraudAlert


HIGH_RISK_ALERT = FraudAlert(
    transaction_id="TXN001",
    amount=250000,
    country="Russia",
    new_device=True,
    transactions_last_10min=15,
    merchant_category="Cryptocurrency"
)


MEDIUM_RISK_ALERT = FraudAlert(
    transaction_id="TXN002",
    amount=75000,
    country="India",
    new_device=True,
    transactions_last_10min=5,
    merchant_category="Electronics"
)


LOW_RISK_ALERT = FraudAlert(
    transaction_id="TXN003",
    amount=5000,
    country="India",
    new_device=False,
    transactions_last_10min=1,
    merchant_category="Groceries"
)

IMPOSSIBLE_TRAVEL_ALERT = FraudAlert(
    transaction_id="TXN004",
    amount=120000,
    country="Russia",
    new_device=False,
    transactions_last_10min=2,
    merchant_category="Travel"
)

SAMPLE_ALERTS = [
    HIGH_RISK_ALERT,
    MEDIUM_RISK_ALERT,
    LOW_RISK_ALERT,
    IMPOSSIBLE_TRAVEL_ALERT
]