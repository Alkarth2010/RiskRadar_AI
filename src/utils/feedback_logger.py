import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.utils.s3_storage import (
    build_s3_key,
    download_file,
    upload_file,
    use_s3_storage,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_LOG_PATH = PROJECT_ROOT / "data" / "feedback_log.csv"
S3_FEEDBACK_KEY = build_s3_key("data/feedback/feedback_log.csv")

FIELDNAMES = [
    "timestamp",
    "transaction_id",
    "customer_id",
    "queue_priority",
    "system_risk_score",
    "system_recommendation",
    "analyst_decision",
    "analyst_note",
    "triggered_rules",
    "triggered_policies",
    "sources",
]


def _format_queue_priority(value: str) -> str:
    if not value:
        return ""

    normalized = value.strip().upper()

    if normalized.endswith("_PRIORITY"):
        return normalized

    return f"{normalized}_PRIORITY"


def _format_list(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, list):
        return " | ".join(str(item) for item in value)

    return str(value)


def sync_feedback_from_s3() -> Path:
    if use_s3_storage():
        download_file(
            S3_FEEDBACK_KEY,
            FEEDBACK_LOG_PATH,
            required=False,
        )

    return FEEDBACK_LOG_PATH


def sync_feedback_to_s3() -> None:
    if use_s3_storage() and FEEDBACK_LOG_PATH.exists():
        upload_file(
            FEEDBACK_LOG_PATH,
            S3_FEEDBACK_KEY,
        )


def _migrate_feedback_log_if_needed() -> None:
    if not FEEDBACK_LOG_PATH.exists():
        return

    with FEEDBACK_LOG_PATH.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as feedback_file:
        reader = csv.DictReader(feedback_file)
        existing_fieldnames = reader.fieldnames or []

        if "alert_severity" not in existing_fieldnames:
            return

        rows = []

        for row in reader:
            row["queue_priority"] = _format_queue_priority(
                row.pop("alert_severity", "")
            )
            rows.append(row)

    with FEEDBACK_LOG_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as feedback_file:
        writer = csv.DictWriter(
            feedback_file,
            fieldnames=FIELDNAMES,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def save_feedback(
    *,
    transaction_id: str,
    customer_id: str,
    system_risk_score: str,
    system_recommendation: str,
    analyst_decision: str,
    analyst_note: str,
    triggered_rules: list[str],
    triggered_policies: list[str],
    sources: list[str],
    queue_priority: Optional[str] = None,
    alert_severity: Optional[str] = None,
) -> Path:
    FEEDBACK_LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sync_feedback_from_s3()
    _migrate_feedback_log_if_needed()

    file_exists = FEEDBACK_LOG_PATH.exists()
    priority_value = queue_priority or alert_severity

    if not priority_value:
        raise ValueError(
            "queue_priority is required to save analyst feedback."
        )

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "queue_priority": _format_queue_priority(priority_value),
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

    sync_feedback_to_s3()

    return FEEDBACK_LOG_PATH
