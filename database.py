import sqlite3
import pandas as pd

DB_NAME = "smartmess.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_date TEXT NOT NULL,
            day TEXT NOT NULL,
            meal TEXT NOT NULL,
            menu TEXT NOT NULL,
            holiday TEXT NOT NULL,
            exam_period TEXT NOT NULL,
            previous_attendance INTEGER NOT NULL,
            predicted_attendance INTEGER NOT NULL,
            recommended_food INTEGER NOT NULL,
            expected_wastage INTEGER NOT NULL,
            wastage_risk TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_prediction(
    prediction_date,
    day,
    meal,
    menu,
    holiday,
    exam_period,
    previous_attendance,
    predicted_attendance,
    recommended_food,
    expected_wastage,
    wastage_risk,
    created_at
):
    conn = get_connection()

    conn.execute("""
        INSERT INTO predictions (
            prediction_date,
            day,
            meal,
            menu,
            holiday,
            exam_period,
            previous_attendance,
            predicted_attendance,
            recommended_food,
            expected_wastage,
            wastage_risk,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prediction_date,
        day,
        meal,
        menu,
        holiday,
        exam_period,
        previous_attendance,
        predicted_attendance,
        recommended_food,
        expected_wastage,
        wastage_risk,
        created_at
    ))

    conn.commit()
    conn.close()


def get_prediction_history():
    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM predictions
        ORDER BY id DESC
    """).fetchall()

    columns = [
        "id",
        "prediction_date",
        "day",
        "meal",
        "menu",
        "holiday",
        "exam_period",
        "previous_attendance",
        "predicted_attendance",
        "recommended_food",
        "expected_wastage",
        "wastage_risk",
        "created_at"
    ]

    conn.close()

    return pd.DataFrame(rows, columns=columns)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    