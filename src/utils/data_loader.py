"""
RiskRadar AI - Data Loading Utilities (Week 1 stub)

Provides helpers to load the synthetic transactions dataset.
"""

import pandas as pd
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "synthetic" / "transactions.csv"


def load_transactions(csv_path: str | Path = None) -> pd.DataFrame:
    """Load synthetic bank transactions."""
    path = Path(csv_path) if csv_path else DEFAULT_PATH
    if not path.exists():
        raise FileNotFoundError(f"Transactions file not found: {path}")
    return pd.read_csv(path, parse_dates=["timestamp"])


def get_fraud_cases(df: pd.DataFrame = None):
    if df is None:
        df = load_transactions()
    return df[df["is_fraud"] == 1].copy()
