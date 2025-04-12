import streamlit as st
from utils2 import load_score_data
from utils import load_data_from_gsheets

st.title("DASHBOARD ")

# -------------------------
# User Inputs for Calories
# -------------------------
st.subheader("METRICS")
c1, c2, c3 = st.columns(3)

with c1:
    user_weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=70.0, key="metric_weight")
with c2:
    timer = st.number_input("Timer (seconds)", min_value=10.0, max_value=1000.0, value=15.0, key="metric_timer")
with c3:
    MET = st.number_input("MET", min_value=0.0, max_value=10.0, value=3.5, key="metric_met")

# -------------------------
# Comparison Mode Selection
# -------------------------
compare_mode = st.selectbox("Compare with:", ["Previous Reading", "Mean Value"], index=0)

# -------------------------
# Function to Get Latest Readings
# -------------------------
def get_latest_readings(user_weight, timer, MET, mode):
    # Load vital data
    temp_df = load_data_from_gsheets()  # Expecting columns: Date, Time, SpO2, Heart Rate, Temperature

    # For Temperature, Heart Rate and SpO2, extract the latest and comparison values
    latest_temperature = temp_df.iloc[-1]["Temperature"]
    latest_heart_rate  = temp_df.iloc[-1]["Heart Rate"]
    latest_spo2        = temp_df.iloc[-1]["SpO2"]

    if mode == "Previous Reading":
        prev_temperature = temp_df.iloc[-2]["Temperature"]
        prev_heart_rate  = temp_df.iloc[-2]["Heart Rate"]
        prev_spo2        = temp_df.iloc[-2]["SpO2"]
    else:  # Mean Value comparison
        prev_temperature = temp_df["Temperature"].mean()
        prev_heart_rate  = temp_df["Heart Rate"].mean()
        prev_spo2        = temp_df["SpO2"].mean()

    # Load score data
    score_df = load_score_data()  # Assuming this dataset has a column "Score"
    latest_score = score_df.iloc[-1]["Score"]
    latest_kicks = latest_score / 10   # Given that score divided by 10 equals kicks

    if mode == "Previous Reading":
        prev_score  = score_df.iloc[-2]["Score"]
        prev_kicks  = prev_score / 10
    else:  # Mean Value comparison
        prev_score  = score_df["Score"].mean()
        prev_kicks  = prev_score / 10

    # Calculate kick duration in seconds.
    # Here we assume timer represents a time window for all kicks (latest or average);
    # we use total kicks for latest reading to derive per-kick duration.
    total_kicks = latest_kicks
    kick_duration_sec = timer / total_kicks if total_kicks > 0 else 1

    # Calculate duration in hours for the latest and comparison kicks
    latest_hours = (latest_kicks * kick_duration_sec) / 3600
    prev_hours   = (prev_kicks * kick_duration_sec) / 3600

    # Calculate calories burned for latest and comparison
    latest_calories = MET * user_weight * latest_hours
    prev_calories   = MET * user_weight * prev_hours

    return {
        "Temperature": (latest_temperature, latest_temperature - prev_temperature),
        "Heart Rate (BPM)": (latest_heart_rate, latest_heart_rate - prev_heart_rate),
        "SpO₂ (%)": (latest_spo2, latest_spo2 - prev_spo2),
        "Score": (latest_score, latest_score - prev_score),
        "Calories Burned": (latest_calories, latest_calories - prev_calories),
    }

# -------------------------
# Get and Display Metrics
# -------------------------
readings = get_latest_readings(user_weight, timer, MET, compare_mode)

# Create columns for metrics display
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, _ = st.columns(2)

col1.metric("Temperature", f"{readings['Temperature'][0]}°F", f"{readings['Temperature'][1]:+.1f}°F", border=True)
col2.metric("Heart Rate (BPM)", f"{readings['Heart Rate (BPM)'][0]}", f"{readings['Heart Rate (BPM)'][1]:+}", border=True)
col3.metric("SpO₂ (%)", f"{readings['SpO₂ (%)'][0]}%", f"{readings['SpO₂ (%)'][1]:+}%", border=True)
col4.metric("Score", f"{readings['Score'][0]}", f"{readings['Score'][1]:+}", border=True)
col5.metric("Calories Burned", f"{readings['Calories Burned'][0]:.2f} kcal", f"{readings['Calories Burned'][1]:+.2f} kcal", border=True)

import plotly.graph_objects as go
import pandas as pd

# -------------------------
# Plotting Calories Burned Over Time
# -------------------------

st.subheader("Calories Burned Over Time")

# Dropdown to choose chart type
chart_type = st.selectbox("Select chart type", ["Line", "Bar"])

# Prepare the data
score_df = load_score_data()
score_df["Kicks"] = score_df["Score"] / 10
score_df["Calories Burned"] = MET * user_weight * (score_df["Kicks"] * (timer / score_df["Kicks"]) / 3600)

# Convert Date or Datetime
if "Date" in score_df.columns:
    score_df["Date"] = pd.to_datetime(score_df["Date"], dayfirst=True)
    x_axis = score_df["Date"]
elif "Timestamp" in score_df.columns:
    score_df["Timestamp"] = pd.to_datetime(score_df["Timestamp"])
    x_axis = score_df["Timestamp"]
else:
    x_axis = score_df.index

# Create the chart
fig = go.Figure()

if chart_type == "Line":
    fig.add_trace(go.Scatter(x=x_axis, y=score_df["Score"], mode="lines+markers", name="Score", line=dict(color="royalblue")))
    fig.add_trace(go.Scatter(x=x_axis, y=score_df["Calories Burned"], mode="lines+markers", name="Calories Burned (kcal)", line=dict(color="tomato")))
else:
    fig.add_trace(go.Bar(x=x_axis, y=score_df["Score"], name="Score", marker_color="royalblue"))
    fig.add_trace(go.Bar(x=x_axis, y=score_df["Calories Burned"], name="Calories Burned (kcal)", marker_color="tomato"))

fig.update_layout(
    title="Score and Calories Burned Over Time",
    xaxis_title="Date",
    yaxis_title="Value",
    legend_title="Metric",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)


