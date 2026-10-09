"""Dataset loading, validation, and feature preparation for SmartMess."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).with_name("dataset.csv")

FEATURE_COLUMNS = [
    "Day",
    "Meal",
    "Menu",
    "Holiday",
    "Exam_Period",
    "Previous_Attendance",
]
TARGET_COLUMN = "Actual_Attendance"
REQUIRED_COLUMNS = [
    "Date",
    *FEATURE_COLUMNS,
    TARGET_COLUMN,
    "Food_Prepared",
    "Food_Wasted",
]
CATEGORICAL_COLUMNS = ["Day", "Meal", "Menu", "Holiday", "Exam_Period"]


def load_and_validate_data(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Load the CSV and raise a clear error when its contract is invalid."""
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Run: python generate_data.py"
        )

    data = pd.read_csv(dataset_path)
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"dataset.csv is missing required columns: {missing}")
    if data.empty:
        raise ValueError("dataset.csv contains no records")
    if data[FEATURE_COLUMNS + [TARGET_COLUMN]].isnull().any().any():
        raise ValueError("Training features and target must not contain missing values")

    allowed_yes_no = {"Yes", "No"}
    for column in ("Holiday", "Exam_Period"):
        invalid = set(data[column].astype(str)) - allowed_yes_no
        if invalid:
            raise ValueError(f"{column} contains invalid values: {sorted(invalid)}")

    numeric_columns = [
        "Previous_Attendance",
        "Actual_Attendance",
        "Food_Prepared",
        "Food_Wasted",
    ]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="raise")
        if (data[column] < 0).any():
            raise ValueError(f"{column} cannot contain negative values")

    return data


def prepare_features(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return model inputs and target using the agreed column names."""
    return data[FEATURE_COLUMNS].copy(), data[TARGET_COLUMN].copy()
