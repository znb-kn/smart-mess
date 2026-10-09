"""SmartMess demand prediction model.

Lightweight version used for integration.
It avoids scikit-learn/SciPy so the Streamlit app can run
even when Windows blocks compiled ML DLLs.
"""

from pathlib import Path
import pandas as pd


DATA_PATH = Path(__file__).with_name("dataset.csv")


def _load_data():
    """Load the SmartMess dataset."""
    if not DATA_PATH.exists():
        return None

    try:
        return pd.read_csv(DATA_PATH)
    except Exception:
        return None


def predict_demand(
    day: str,
    meal: str,
    menu: str,
    holiday: str,
    exam_period: str,
    previous_attendance: int,
) -> int:
    """Predict expected attendance for the selected meal."""

    previous_attendance = int(previous_attendance)

    if previous_attendance < 0:
        raise ValueError("previous_attendance cannot be negative")

    if holiday not in {"Yes", "No"}:
        raise ValueError("holiday must be 'Yes' or 'No'")

    if exam_period not in {"Yes", "No"}:
        raise ValueError("exam_period must be 'Yes' or 'No'")

    data = _load_data()

    # If the dataset cannot be read, use previous attendance
    # as a safe fallback.
    if data is None or data.empty:
        return max(0, previous_attendance)

    # Find the attendance/target column used by the dataset.
    possible_targets = [
        "Attendance",
        "attendance",
        "Expected_Attendance",
        "expected_attendance",
        "Student_Attendance",
        "student_attendance",
        "Target",
        "target",
    ]

    target_column = None

    for column in possible_targets:
        if column in data.columns:
            target_column = column
            break

    # If no target column is available, fall back safely.
    if target_column is None:
        return max(0, previous_attendance)

    # Convert target values to numbers.
    data[target_column] = pd.to_numeric(
        data[target_column],
        errors="coerce"
    )

    data = data.dropna(subset=[target_column])

    if data.empty:
        return max(0, previous_attendance)

    # Start with the previous attendance.
    prediction = float(previous_attendance)

    # Look for records matching the selected conditions.
    filtered = data.copy()

    filters = {
        "Day": day,
        "Meal": meal,
        "Menu": menu,
        "Holiday": holiday,
        "Exam_Period": exam_period,
    }

    matched_any = False

    for column, value in filters.items():
        if column in filtered.columns:
            subset = filtered[
                filtered[column].astype(str).str.strip().str.lower()
                == str(value).strip().lower()
            ]

            if not subset.empty:
                filtered = subset
                matched_any = True

    # If matching historical records exist, use their average.
    if matched_any and not filtered.empty:
        historical_average = float(
            filtered[target_column].mean()
        )

        # Blend previous attendance with historical demand.
        prediction = (
            previous_attendance * 0.60
            + historical_average * 0.40
        )

    # Small adjustments based on known conditions.
    if holiday == "Yes":
        prediction *= 0.80

    if exam_period == "Yes":
        prediction *= 0.90

    # Keep the prediction sensible.
    prediction = max(0, round(prediction))

    return int(prediction)


if __name__ == "__main__":
    result = predict_demand(
        "Monday",
        "Lunch",
        "Biryani",
        "No",
        "No",
        500,
    )

    print(f"Sample predicted attendance: {result}")