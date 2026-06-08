from src.fraud.alert_generator import (
    generate_alerts
)


def format_queue_priority(severity):
    return f"{severity}_PRIORITY"


alerts = generate_alerts()

print("\nALERT QUEUE\n")

for alert in alerts[:20]:

    print(
        f"{format_queue_priority(alert.severity):15}"
        f" | {alert.transaction_id}"
        f" | {', '.join(alert.triggered_rules)}"
    )
    
