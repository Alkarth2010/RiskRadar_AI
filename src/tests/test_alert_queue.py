from src.fraud.alert_generator import (
    generate_alerts
)

alerts = generate_alerts()

print("\nALERT QUEUE\n")

for alert in alerts[:20]:

    print(
        f"{alert.severity:6}"
        f" | {alert.transaction_id}"
        f" | {', '.join(alert.triggered_rules)}"
    )
    