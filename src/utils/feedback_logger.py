import csv
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_LOG_PATH = PROJECT_ROOT / "data" / "feedback_log.csv"

FIELDNAMES = [
    "timestamp",
    "transaction_id",
    "customer_id",
    "alert_severity",
    "system_risk_score",
    "system_recommendation",
    "analyst_decision",
    "analyst_note",
    "triggered_rules",
    "triggered_policies",
    "sources",
]


def _format_list(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, list):
        return " | ".join(str(item) for item in value)

    return str(value)


def save_feedback(
    *,
    transaction_id: str,
    customer_id: str,
    alert_severity: str,
    system_risk_score: str,
    system_recommendation: str,
    analyst_decision: str,
    analyst_note: str,
    triggered_rules: list[str],
    triggered_policies: list[str],
    sources: list[str],
) -> Path:
    FEEDBACK_LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_exists = FEEDBACK_LOG_PATH.exists()

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "alert_severity": alert_severity,
        "system_risk_score": system_risk_score,
        "system_recommendation": system_recommendation,
        "analyst_decision": analyst_decision,
        "analyst_note": analyst_note,
        "triggered_rules": _format_list(triggered_rules),
        "triggered_policies": _format_list(triggered_policies),
        "sources": _format_list(sources),
    }

    with FEEDBACK_LOG_PATH.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as feedback_file:
        writer = csv.DictWriter(
            feedback_file,
            fieldnames=FIELDNAMES,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

    return FEEDBACK_LOG_PATH
