"""Food preparation recommendation logic for SmartMess."""

from __future__ import annotations

import math


FOOD_BUFFER_RATE = 0.05


def calculate_food_requirement(predicted_attendance: int) -> tuple[int, int, str]:
    """Return portions, potential surplus, and risk using a fixed 5% buffer.

    ``expected_wastage`` is a potential surplus estimate for the demo. It is not
    actual measured waste, which can only be known after a meal is served.
    """
    predicted = int(predicted_attendance)
    if predicted < 0:
        raise ValueError("predicted_attendance cannot be negative")

    recommended_food = math.ceil(predicted * (1 + FOOD_BUFFER_RATE))
    expected_wastage = recommended_food - predicted
    surplus_ratio = expected_wastage / predicted if predicted else 0.0

    if surplus_ratio <= 0.05:
        wastage_risk = "Low"
    elif surplus_ratio <= 0.10:
        wastage_risk = "Medium"
    else:
        wastage_risk = "High"

    return recommended_food, expected_wastage, wastage_risk
