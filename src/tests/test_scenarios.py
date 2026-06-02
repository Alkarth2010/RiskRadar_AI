from src.fraud.service import investigate_fraud_alert
from src.tests.sample_alerts import SAMPLE_ALERTS


for alert in SAMPLE_ALERTS:

    print("\n" + "=" * 80)
    print(f"Transaction: {alert.transaction_id}")
    print("=" * 80)

    result = investigate_fraud_alert(alert)

    print(f"Risk Score: {result.risk_score}")
    print(f"Action: {result.recommended_action}")

    print("\nTriggered Policies:")
    for policy in result.triggered_policies:
        print(f" - {policy}")

    print("\nAction Reason:")
    print(result.action_reason)

    print("\nSources:")
    for source in result.sources:
        print(f" - {source}")

    print("\nRisk Reasoning:")
    print(result.risk_reasoning)

    print("\nInvestigation Summary:")
    print(result.investigation_summary)   

    print("\n")
    