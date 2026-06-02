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

print(result)