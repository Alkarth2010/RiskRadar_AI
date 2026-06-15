from pathlib import Path
from typing import Union

import pandas as pd

from src.utils.s3_storage import (
    build_s3_key,
    download_file,
    use_s3_storage,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = PROJECT_ROOT / "data" / "synthetic" / "transactions.csv"
S3_CACHE_PATH = (
    PROJECT_ROOT
    / ".cache"
    / "s3"
    / "data"
    / "synthetic"
    / "transactions.csv"
)


def _get_transactions_path(csv_path: Union[str, Path] = None) -> Path:
    if csv_path:
        return Path(csv_path)

    if use_s3_storage():
        return download_file(
            build_s3_key("data/synthetic/transactions.csv"),
            S3_CACHE_PATH,
        )

    return DEFAULT_PATH


def load_transactions(
    csv_path: Union[str, Path] = None
) -> pd.DataFrame:
    """Load synthetic bank transactions."""
    path = _get_transactions_path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"Transactions file not found: {path}")

    return pd.read_csv(path, parse_dates=["timestamp"])


def get_fraud_cases(df: pd.DataFrame = None):
    if df is None:
        df = load_transactions()

    return df[df["is_fraud"] == 1].copy()
