from src.fraud.models import FraudAlert
from src.fraud.alert_models import InvestigationAlert


def convert_to_workflow_alert(
    alert: InvestigationAlert
):

    return FraudAlert(
        transaction_id=alert.transaction_id,
        amount=alert.amount,
        country=alert.location,
        new_device=alert.new_device,
        transactions_last_10min=alert.velocity_count,
        triggered_rules=alert.triggered_rules
    )