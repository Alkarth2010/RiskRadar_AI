import tempfile
from pathlib import Path

from src.fraud.alert_adapter import convert_to_workflow_alert
from src.fraud.alert_generator import generate_alerts
from src.graph.workflow import build_workflow
from src.utils import feedback_logger


REQUIRED_RESULT_KEYS = [
    "risk_score",
    "recommended_action",
    "triggered_policies",
    "risk_reasoning",
    "investigation_summary",
    "agent_trace",
    "sources",
]


def _select_alerts_by_severity(alerts):
    selected = {}

    for alert in alerts:
        if alert.severity not in selected:
            selected[alert.severity] = alert

    return selected


def _format_queue_priority(severity):
    return f"{severity}_PRIORITY"


def _assert_required_result_fields(result):
    missing_keys = [
        key
        for key in REQUIRED_RESULT_KEYS
        if key not in result
    ]

    assert not missing_keys, (
        f"Missing workflow result keys: {missing_keys}"
    )


def _assert_parallel_trace(result):
    trace = result.get(
        "agent_trace",
        []
    )

    expected_steps = [
        "Parallel fraud analysis started",
        "Risk scoring analyst completed",
        "Behavioral pattern analyst completed",
        "Evidence fusion completed",
        "Human decision pending",
    ]

    for expected_step in expected_steps:
        assert any(
            expected_step in step
            for step in trace
        ), f"Missing trace step: {expected_step}"


def _run_workflow_for_alert(workflow, alert):
    workflow_alert = convert_to_workflow_alert(alert)

    return workflow.invoke(
        {
            "alert": workflow_alert.model_dump()
        }
    )


def _test_feedback_logging(alert, result):
    with tempfile.TemporaryDirectory() as temp_dir:
        feedback_logger.FEEDBACK_LOG_PATH = (
            Path(temp_dir) / "feedback_log.csv"
        )

        feedback_path = feedback_logger.save_feedback(
            transaction_id=alert.transaction_id,
            customer_id=alert.customer_id,
            queue_priority=_format_queue_priority(alert.severity),
            system_risk_score=result["risk_score"],
            system_recommendation=result["recommended_action"],
            analyst_decision="MONITOR",
            analyst_note="Day 4 E2E test",
            triggered_rules=alert.triggered_rules,
            triggered_policies=result["triggered_policies"],
            sources=result["sources"],
        )

        assert feedback_path.exists()

        content = feedback_path.read_text(
            encoding="utf-8"
        )

        assert "transaction_id" in content
        assert "queue_priority" in content
        assert alert.transaction_id in content
        assert _format_queue_priority(alert.severity) in content
        assert "MONITOR" in content
        assert "Day 4 E2E test" in content


def main():
    alerts = generate_alerts()
    selected_alerts = _select_alerts_by_severity(alerts)
    workflow = build_workflow()

    print("\nDAY 4 E2E TEST\n")
    print(f"Generated alerts: {len(alerts)}")

    for severity in [
        "HIGH",
        "MEDIUM",
        "LOW",
    ]:
        alert = selected_alerts.get(severity)

        assert alert is not None, (
            f"No {severity} alert available for E2E test"
        )

        result = _run_workflow_for_alert(
            workflow,
            alert,
        )

        _assert_required_result_fields(result)
        _assert_parallel_trace(result)

        print(
            f"queue_priority={_format_queue_priority(severity)} "
            f"transaction={alert.transaction_id}: "
            f"workflow_risk={result['risk_score']}, "
            f"recommendation={result['recommended_action']}, "
            f"sources={len(result['sources'])}, "
            f"trace_steps={len(result['agent_trace'])}"
        )

    _test_feedback_logging(
        selected_alerts["HIGH"],
        _run_workflow_for_alert(
            workflow,
            selected_alerts["HIGH"],
        ),
    )

    print("\nFeedback logging: passed")
    print("Day 4 E2E test: passed\n")


if __name__ == "__main__":
    main()
