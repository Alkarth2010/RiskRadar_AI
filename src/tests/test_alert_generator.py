from src.fraud.alert_generator import (
    generate_alerts
)

alerts = generate_alerts()

print(
    f"\nGenerated Alerts: {len(alerts)}\n"
)

from collections import Counter

rule_counter = Counter()

for alert in alerts:
    for rule in alert.triggered_rules:
        rule_counter[rule] += 1

print("\nRule Distribution\n")

for rule, count in rule_counter.items():
    print(f"{rule}: {count}")