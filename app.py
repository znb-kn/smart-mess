import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

# =========================================================
# IMPORTS
# =========================================================

from database import (
    init_db,
    save_prediction,
    get_prediction_history
)

# Person 1 - ML model
from model import predict_demand

# Person 1 - Food recommendation logic
from food_logic import calculate_food_requirement


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SmartMess",
    page_icon="🍽️",
    layout="wide"
)


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🍽️ SmartMess")

st.sidebar.caption(
    "Smart Food Demand Prediction "
    "& Food Waste Reduction System"
)

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Demand Prediction",
        "Analytics",
        "History"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("🍽️ SmartMess Dashboard")

    st.write(
        "Predict meal demand and plan food preparation "
        "to reduce unnecessary food wastage."
    )

    history = get_prediction_history()

    # -----------------------------------------------------
    # No prediction available
    # -----------------------------------------------------

    if history.empty:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Expected Attendance",
            "—"
        )

        col2.metric(
            "Recommended Food",
            "—"
        )

        col3.metric(
            "Expected Wastage",
            "—"
        )

        col4.metric(
            "Wastage Risk",
            "—"
        )

        st.info(
            "Create a prediction from the "
            "Demand Prediction page to view results here."
        )

    # -----------------------------------------------------
    # Prediction available
    # -----------------------------------------------------

    else:

        latest = history.iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Expected Attendance",
            int(latest["predicted_attendance"])
        )

        col2.metric(
            "Recommended Food",
            int(latest["recommended_food"])
        )

        col3.metric(
            "Expected Wastage",
            int(latest["expected_wastage"])
        )

        col4.metric(
            "Wastage Risk",
            latest["wastage_risk"]
        )

        st.divider()

        st.subheader("Latest Prediction")

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Date:** {latest['prediction_date']}"
            )

            st.write(
                f"**Day:** {latest['day']}"
            )

            st.write(
                f"**Meal:** {latest['meal']}"
            )

            st.write(
                f"**Menu:** {latest['menu']}"
            )

        with col2:

            st.write(
                f"**Previous Attendance:** "
                f"{latest['previous_attendance']}"
            )

            st.write(
                f"**Predicted Attendance:** "
                f"{latest['predicted_attendance']}"
            )

            st.write(
                f"**Recommended Food:** "
                f"{latest['recommended_food']}"
            )

            st.write(
                f"**Expected Wastage:** "
                f"{latest['expected_wastage']}"
            )

        st.divider()

        st.subheader("Recent Predictions")

        recent = history.head(5)[
            [
                "prediction_date",
                "meal",
                "menu",
                "predicted_attendance",
                "recommended_food",
                "expected_wastage",
                "wastage_risk"
            ]
        ].copy()

        recent.columns = [
            "Date",
            "Meal",
            "Menu",
            "Predicted Attendance",
            "Recommended Food",
            "Expected Wastage",
            "Risk"
        ]

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# DEMAND PREDICTION
# =========================================================

elif page == "Demand Prediction":

    st.title("📊 Demand Prediction")

    st.write(
        "Enter meal details to predict student attendance "
        "and recommended food preparation."
    )

    # -----------------------------------------------------
    # INPUTS
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        prediction_date = st.date_input(
            "Date",
            value=date.today()
        )

        day = st.selectbox(
            "Day",
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ]
        )

        meal = st.selectbox(
            "Meal",
            [
                "Breakfast",
                "Lunch",
                "Dinner"
            ]
        )

        menu = st.selectbox(
            "Menu",
            [
                "Simple Meals",
                "South Indian",
                "North Indian",
                "Biryani",
                "Paneer",
                "Special Meal"
            ]
        )

    with col2:

        holiday = st.selectbox(
            "Holiday",
            [
                "No",
                "Yes"
            ]
        )

        exam_period = st.selectbox(
            "Exam Period",
            [
                "No",
                "Yes"
            ]
        )

        previous_attendance = st.number_input(
            "Previous Attendance",
            min_value=0,
            max_value=5000,
            value=500,
            step=10
        )

    st.divider()

    # -----------------------------------------------------
    # PREDICT BUTTON
    # -----------------------------------------------------

    predict_button = st.button(
        "🔮 Predict Demand",
        type="primary",
        use_container_width=True
    )

    if predict_button:

        try:

            # -------------------------------------------------
            # PERSON 1 - ML MODEL
            # -------------------------------------------------

            predicted_attendance = predict_demand(
                day=day,
                meal=meal,
                menu=menu,
                holiday=holiday,
                exam_period=exam_period,
                previous_attendance=previous_attendance
            )

            # -------------------------------------------------
            # PERSON 1 - FOOD LOGIC
            # -------------------------------------------------

            (
                recommended_food,
                expected_wastage,
                wastage_risk
            ) = calculate_food_requirement(
                predicted_attendance
            )

            # -------------------------------------------------
            # STORE CURRENT RESULT
            # -------------------------------------------------

            st.session_state["prediction"] = {

                "prediction_date":
                    prediction_date,

                "day":
                    day,

                "meal":
                    meal,

                "menu":
                    menu,

                "holiday":
                    holiday,

                "exam_period":
                    exam_period,

                "previous_attendance":
                    previous_attendance,

                "predicted_attendance":
                    predicted_attendance,

                "recommended_food":
                    recommended_food,

                "expected_wastage":
                    expected_wastage,

                "wastage_risk":
                    wastage_risk
            }

        except Exception as e:

            st.error(
                f"Prediction failed: {e}"
            )

    # =====================================================
    # DISPLAY RESULT
    # =====================================================

    if "prediction" in st.session_state:

        result = st.session_state["prediction"]

        st.divider()

        st.subheader("Prediction Result")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Predicted Attendance",
            result["predicted_attendance"]
        )

        col2.metric(
            "Recommended Food",
            result["recommended_food"]
        )

        col3.metric(
            "Expected Wastage",
            result["expected_wastage"]
        )

        col4.metric(
            "Wastage Risk",
            result["wastage_risk"]
        )

        st.success(
            f"The ML model predicts approximately "
            f"**{result['predicted_attendance']} students**."
        )

        st.info(
            f"Recommended preparation: "
            f"**{result['recommended_food']} portions** "
            f"with a potential surplus of "
            f"**{result['expected_wastage']} portions**."
        )

        # -------------------------------------------------
        # SAVE BUTTON
        # -------------------------------------------------

        save_button = st.button(
            "💾 Save Prediction",
            use_container_width=True
        )

        if save_button:

            try:

                save_prediction(

                    result["prediction_date"].strftime(
                        "%Y-%m-%d"
                    ),

                    result["day"],

                    result["meal"],

                    result["menu"],

                    result["holiday"],

                    result["exam_period"],

                    result["previous_attendance"],

                    result["predicted_attendance"],

                    result["recommended_food"],

                    result["expected_wastage"],

                    result["wastage_risk"],

                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                st.success(
                    "Prediction saved successfully!"
                )

                # Remove current prediction after saving
                del st.session_state["prediction"]

            except Exception as e:

                st.error(
                    f"Could not save prediction: {e}"
                )


# =========================================================
# ANALYTICS
# =========================================================

elif page == "Analytics":

    st.title("📈 Analytics")

    history = get_prediction_history()

    if history.empty:

        st.info(
            "Save predictions to generate analytics."
        )

    else:

        chart_data = history.copy()

        chart_data["prediction_date"] = pd.to_datetime(
            chart_data["prediction_date"]
        )

        chart_data = chart_data.sort_values(
            "prediction_date"
        )

        # -------------------------------------------------
        # ATTENDANCE TREND
        # -------------------------------------------------

        st.subheader("Attendance Trend")

        fig1 = px.line(
            chart_data,
            x="prediction_date",
            y="predicted_attendance",
            markers=True,
            title="Predicted Attendance Over Time"
        )

        fig1.update_layout(
            xaxis_title="Date",
            yaxis_title="Students"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        # -------------------------------------------------
        # MEAL-WISE ATTENDANCE
        # -------------------------------------------------

        st.subheader("Meal-wise Attendance")

        meal_data = (
            history
            .groupby("meal")["predicted_attendance"]
            .mean()
            .reset_index()
        )

        fig2 = px.bar(
            meal_data,
            x="meal",
            y="predicted_attendance",
            title="Average Predicted Attendance by Meal"
        )

        fig2.update_layout(
            xaxis_title="Meal",
            yaxis_title="Average Students"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # -------------------------------------------------
        # DEMAND VS FOOD PREPARATION
        # -------------------------------------------------

        st.subheader(
            "Predicted Demand vs Recommended Food"
        )

        fig3 = px.bar(
            chart_data,
            x="prediction_date",
            y=[
                "predicted_attendance",
                "recommended_food"
            ],
            barmode="group",
            title="Demand vs Food Preparation"
        )

        fig3.update_layout(
            xaxis_title="Date",
            yaxis_title="Portions"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        # -------------------------------------------------
        # WASTAGE TREND
        # -------------------------------------------------

        st.subheader("Expected Wastage Trend")

        fig4 = px.line(
            chart_data,
            x="prediction_date",
            y="expected_wastage",
            markers=True,
            title="Expected Food Wastage"
        )

        fig4.update_layout(
            xaxis_title="Date",
            yaxis_title="Potential Surplus Portions"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )


# =========================================================
# HISTORY
# =========================================================

elif page == "History":

    st.title("🗂️ Prediction History")

    history = get_prediction_history()

    if history.empty:

        st.info(
            "No predictions have been saved yet."
        )

    else:

        display_data = history[
            [
                "prediction_date",
                "day",
                "meal",
                "menu",
                "previous_attendance",
                "predicted_attendance",
                "recommended_food",
                "expected_wastage",
                "wastage_risk"
            ]
        ].copy()

        display_data.columns = [
            "Date",
            "Day",
            "Meal",
            "Menu",
            "Previous Attendance",
            "Predicted Attendance",
            "Recommended Food",
            "Expected Wastage",
            "Wastage Risk"
        ]

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

        st.write(
            f"**Total saved predictions:** "
            f"{len(history)}"
        )