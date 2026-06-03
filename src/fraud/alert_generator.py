from collections import defaultdict
from datetime import timedelta

from src.utils.data_loader import load_transactions
from src.fraud.alert_models import InvestigationAlert


MIN_HISTORY = 5
HIGH_VALUE_MULTIPLIER = 3
GLOBAL_HIGH_VALUE_THRESHOLD = 2500
VELOCITY_WINDOW_MINUTES = 30
VELOCITY_THRESHOLD = 3


def determine_severity(triggered_rules):

    count = len(triggered_rules)

    if count >= 3:
        return "HIGH"

    if count == 2:
        return "MEDIUM"

    return "LOW"


def generate_alerts():

    df = load_transactions()

    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    customer_transactions = defaultdict(list)
    customer_devices = defaultdict(set)
    customer_locations = defaultdict(set)

    alerts = []

    for _, row in df.iterrows():

        customer_id = row["customer_id"]
        transaction_id = row["transaction_id"]

        amount = float(row["amount"])
        location = row["location"]
        device = row["device"]
        timestamp = row["timestamp"]

        triggered_rules = []

        # ----------------------------------
        # HIGH VALUE
        # ----------------------------------

        prior_transactions = customer_transactions[
            customer_id
        ]

        if len(prior_transactions) >= MIN_HISTORY:

            avg_amount = (
                sum(
                    tx["amount"]
                    for tx in prior_transactions
                )
                / len(prior_transactions)
            )

            if amount > (
                avg_amount *
                HIGH_VALUE_MULTIPLIER
            ):
                triggered_rules.append(
                    "High Value Transaction"
                )

        else:

            if amount > GLOBAL_HIGH_VALUE_THRESHOLD:

                triggered_rules.append(
                    "High Value Transaction"
                )

        # ----------------------------------
        # NEW DEVICE
        # ----------------------------------

        new_device = False

        if (
            len(customer_devices[customer_id]) >= 2
            and device
            not in customer_devices[
                customer_id
            ]
        ):
            new_device = True

            triggered_rules.append(
                "New Device"
            )

        # ----------------------------------
        # GEO ANOMALY
        # ----------------------------------

        geographic_anomaly = False

        if (
            len(customer_locations[
                customer_id
            ]) >= 3
            and location
            not in customer_locations[
                customer_id
            ]
        ):
            geographic_anomaly = True

            triggered_rules.append(
                "Geographic Anomaly"
            )

        # ----------------------------------
        # VELOCITY
        # ----------------------------------

        velocity_count = 0

        for tx in prior_transactions:

            if (
                timestamp - tx["timestamp"]
            ) <= timedelta(
                minutes=VELOCITY_WINDOW_MINUTES
            ):
                velocity_count += 1

        if velocity_count >= VELOCITY_THRESHOLD:

            triggered_rules.append(
                "Velocity Spike"
            )

        # ----------------------------------
        # CREATE ALERT
        # ----------------------------------

        if triggered_rules:

            severity = determine_severity(
                triggered_rules
            )

            alerts.append(
                InvestigationAlert(
                    transaction_id=transaction_id,
                    customer_id=customer_id,
                    amount=amount,
                    location=location,
                    severity=severity,
                    triggered_rules=triggered_rules,
                    new_device=new_device,
                    velocity_count=velocity_count,
                    geographic_anomaly=geographic_anomaly
                )
            )

        # ----------------------------------
        # UPDATE HISTORY
        # ----------------------------------

        customer_transactions[
            customer_id
        ].append(
            {
                "amount": amount,
                "timestamp": timestamp
            }
        )

        customer_devices[
            customer_id
        ].add(device)

        customer_locations[
            customer_id
        ].add(location)

    return alerts