import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from src.fraud.models import FraudAlert
from src.graph.workflow import build_workflow


workflow = build_workflow()

alert = FraudAlert(
    transaction_id="TXN001",
    amount=250000,
    country="Russia",
    new_device=True,
    transactions_last_10min=15
)

result = workflow.invoke(
    {
        "alert": alert.model_dump()
    }
)


print("\n" + "=" * 60)
print("FRAUD INVESTIGATION REPORT")
print("=" * 60)

print(f"\nTransaction ID : {result['alert']['transaction_id']}")
print(f"Risk Score     : {result['risk_score']}")
print(f"Recommendation : {result['recommended_action']}")

print("\nCase Summary")
print("-" * 60)

print(
    f"Transaction {result['alert']['transaction_id']} "
    f"has been classified as "
    f"{result['risk_score']} risk."
)

print(
    f"Recommended Action: "
    f"{result['recommended_action']}"
)

print("\nTriggered Policies")
print("-" * 60)

for policy in result["triggered_policies"]:
    print(f"• {policy}")

print("\nAgent Trace")
print("-" * 60)

for i, step in enumerate(result["agent_trace"], start=1):
    print(f"{i}. {step}")

print("\nRisk Reasoning")
print("-" * 60)
print(result["risk_reasoning"])

print("\nInvestigation Summary")
print("-" * 60)
print(result["investigation_summary"])

print("\nSources")
print("-" * 60)

for source in result["sources"]:
    print(f"• {source}")

print("\n" + "=" * 60)