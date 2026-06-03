HIGH_RISK_COUNTRIES = {
    "Russia",
    "North Korea",
    "Iran"
}

POLICY_WEIGHTS = {
    "High_Value_Transaction_Policy": 30,
    "Geographic_Anomaly_Policy": 25,
    "Velocity_and_Burst_Detection_Policy": 25,
    "Device_and_Payment_Instrument_Policy": 20,
}

def calculate_risk(alert):

    score = 0

    triggered_policies = []

    rule_to_policy = {
        "High Value Transaction":
            "High_Value_Transaction_Policy",

        "New Device":
            "Device_and_Payment_Instrument_Policy",

        "Velocity Spike":
            "Velocity_and_Burst_Detection_Policy",

        "Geographic Anomaly":
            "Geographic_Anomaly_Policy"
    }

    if alert.triggered_rules:

        triggered_policies = [
            rule_to_policy[r]
            for r in alert.triggered_rules
            if r in rule_to_policy
        ]

        score = sum(
            POLICY_WEIGHTS[p]
            for p in triggered_policies
        )

        if score >= 70:
            risk_level = "HIGH"

        elif score >= 20:
            risk_level = "MEDIUM"

        else:
            risk_level = "LOW"

        return {
            "score": score,
            "risk_level": risk_level,
            "triggered_policies": list(
                set(triggered_policies)
            )
        }

    if alert.amount > 100000:
        triggered_policies.append(
            "High_Value_Transaction_Policy"
        )

    if alert.new_device:
        triggered_policies.append(
            "Device_and_Payment_Instrument_Policy"
        )

    if alert.transactions_last_10min > 10:
        triggered_policies.append(
            "Velocity_and_Burst_Detection_Policy"
        )

    if alert.country in HIGH_RISK_COUNTRIES:
        triggered_policies.append(
            "Geographic_Anomaly_Policy"
        )

    score = sum(
        POLICY_WEIGHTS[p]
        for p in triggered_policies
    )

    if score >= 70:
        risk_level = "HIGH"

    elif score >= 20:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "score": score,
        "risk_level": risk_level,
        "triggered_policies": list(
            set(triggered_policies)
        )
    }