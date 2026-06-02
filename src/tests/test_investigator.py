from src.fraud.models import FraudAlert
from src.fraud.investigator import FraudInvestigator


alert = FraudAlert(
    transaction_id="TXN001",
    amount=250000,
    country="Russia",
    new_device=True,
    transactions_last_10min=15
)

investigator = FraudInvestigator()

result = investigator.investigate(alert)

print("\nRISK SCORE")
print(result["risk_score"])

print("\nPOLICIES")
print(result["triggered_policies"])

print("\nSOURCES")
print(result["sources"])

print("\nCONTEXT")
print(result["context"][:1000])