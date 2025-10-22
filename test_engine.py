import json
import os
import logging

class CreditSimilarityEngine:
    def __init__(self, institution_id):
        self.institution_id = institution_id
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config()
        self.risk_thresholds = self.config.get("risk_thresholds", self.default_thresholds())
        self.logger.info(f"[{self.institution_id}] Thresholds loaded: {self.risk_thresholds}")

    def load_config(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "..", "config", "tenants", f"{self.institution_id}.json")
        path = os.path.abspath(path)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        self.logger.warning(f"[{self.institution_id}] Config not found. Using defaults.")
        return {}

    def default_thresholds(self):
        return {
            "reject_auto": 0.90,
            "high_risk": 0.80,
            "risky": 0.70,
            "medium_risk": 0.50,
            "low_risk": 0.00
        }

if __name__ == "__main__":
    engine = CreditSimilarityEngine("banreservas")
    print("Thresholds:", engine.risk_thresholds)
