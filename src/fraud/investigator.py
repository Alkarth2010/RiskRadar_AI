from src.fraud.risk_engine import calculate_risk
from src.rag.rag_pipeline import RiskRadarRAG


class FraudInvestigator:

    def __init__(self):

        self.rag = RiskRadarRAG()

    def investigate(self, alert):

        risk_result = calculate_risk(alert)

        retrieval = self.rag.retrieve_policy_context(
            risk_result["triggered_policies"]
        )

        return {
            "risk_score":
                risk_result["risk_level"],

            "triggered_policies":
                risk_result["triggered_policies"],

            "context":
                retrieval["context"],

            "sources":
                retrieval["sources"]
        }