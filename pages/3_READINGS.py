import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data_from_gsheets
from utils2 import load_score_data
import plotly.graph_objects as go

df = load_data_from_gsheets()
st.title("📈 MONITORING DASHBOARD")

col1, col2 = st.columns([2, 2])
with col1:
    unique_dates = sorted(df['Date'].dt.date.unique())
    selected_dates = st.multiselect("Select Date(s):", unique_dates, default=unique_dates)
with col2:
    time_range = st.slider("Select Time Range (Hours):", 0, 24, (0, 24), step=1)

df_filtered = df[df['Date'].dt.date.isin(selected_dates)].copy()
df_filtered['Timestamp'] = pd.to_datetime(df_filtered['Date'].astype(str) + ' ' + df_filtered['Time'].astype(str))
start_hour, end_hour = time_range
df_filtered = df_filtered[(df_filtered['Timestamp'].dt.hour >= start_hour) & (df_filtered['Timestamp'].dt.hour <= end_hour)]

# Normalize dates to the same day to align times across dates
df_filtered['Timestamp'] = df_filtered['Timestamp'].apply(lambda t: t.replace(year=2000, month=1, day=1))

if df_filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()


#check_and_send_email(df_filtered, email_config)

#css script for better navigation
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] {
        font-size: 30px;
        font-weight: bold;
        padding: 12px 24px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🌡 Temperature", "❤️ Heart Rate", "🫁 SpO2", "🕹 Game Scores"])



def display_tab(tab, y_col, unit, y_range):
    with tab:
        st.subheader(f"{y_col} Trend")
        fig = px.line(
            df_filtered,
            x='Timestamp',
            y=y_col,
            color=df_filtered['Date'].dt.strftime('%d-%m-%Y'),
            line_shape='linear',
            markers=False,
            
        )
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title=f"{y_col} ({unit})",
            yaxis_range=y_range,
            legend_title="Date",
            legend=dict(orientation="h", y=-0.3),
            xaxis=dict(
                tickformat="%H:%M:%S",
                dtick=13000,  # setting the time interval
                tickangle=90
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander(f"📌 Highlights for {y_col}"):
            abnormal = None
            if y_col == "Temperature":
                abnormal = df_filtered[df_filtered[y_col] > 99.5]
            elif y_col == "Heart Rate":
                abnormal = df_filtered[(df_filtered[y_col] < 60) | (df_filtered[y_col] > 100)]
            elif y_col == "SpO2":
                abnormal = df_filtered[df_filtered[y_col] < 95]

            if abnormal is not None and not abnormal.empty:
                st.warning(f"⚠️ {len(abnormal)} abnormal {y_col} reading(s) detected.")
                abnormal_display = abnormal.copy()
                abnormal_display['Time'] = abnormal_display['Timestamp'].dt.strftime('%H:%M:%S')
                abnormal_display['Date'] = abnormal_display['Date'].dt.strftime('%d-%m-%Y')
                st.dataframe(abnormal_display[['Time', 'Date', y_col]], use_container_width=True)
            else:
                st.success(f"✅ All {y_col} readings are normal.")

display_tab(tab1, "Temperature", "°F", [70, 105])
display_tab(tab2, "Heart Rate", "bpm", [30, 110])
display_tab(tab3, "SpO2", "%", [75, 105])

with tab4:
    st.title("Cumulative Score")

    # Load data
    score_df = load_score_data()

    if score_df.empty:
        st.warning("No score data to display.")
    else:
        # Aggregate metrics by date
        agg_df = score_df.groupby(score_df['Date'].dt.date).agg(
            Total_Score=("Score", "sum"),
            Average_Score=("Score", "mean"),
            Min_Score=("Score", "min"),
            Max_Score=("Score", "max")
        ).reset_index()
        agg_df.columns = ["Date", "Total Score", "Average Score", "Min Score", "Max Score"]

        # Chart type selection
        chart_type = st.radio(
            "Select Chart Type", 
            options=["Grouped Bar Chart", "Line Chart"],
            horizontal=True
        )

        # Date filter
        unique_dates = agg_df["Date"].unique()
        selected_dates = st.multiselect(
            "Choose Dates",
            options=unique_dates,
            default=unique_dates,
            key="chart_date_selector"
        )

        filtered_df = agg_df[agg_df["Date"].isin(selected_dates)]

        # Plotting
        if chart_type == "Grouped Bar Chart":
            fig = go.Figure(data=[
                go.Bar(name="Total Score", x=filtered_df["Date"], y=filtered_df["Total Score"], marker_color="dodgerblue"),
                go.Bar(name="Average Score", x=filtered_df["Date"], y=filtered_df["Average Score"], marker_color="orange"),
                go.Bar(name="Min Score", x=filtered_df["Date"], y=filtered_df["Min Score"], marker_color="green"),
                go.Bar(name="Max Score", x=filtered_df["Date"], y=filtered_df["Max Score"], marker_color="red")
            ])

            fig.update_layout(
                barmode="group",
                title="Total, Average, Min & Max Scores per Date",
                xaxis_title="Date",
                yaxis_title="Score",
                legend_title="Metrics",
                legend=dict(orientation="h", y=1.1)
            )
        else:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=filtered_df["Date"], y=filtered_df["Total Score"],
                mode='lines+markers', name='Total Score', line=dict(color='dodgerblue', width=3)
            ))

            fig.add_trace(go.Scatter(
                x=filtered_df["Date"], y=filtered_df["Average Score"],
                mode='lines+markers', name='Average Score', line=dict(color='orange', width=3)
            ))

            fig.add_trace(go.Scatter(
                x=filtered_df["Date"], y=filtered_df["Min Score"],
                mode='lines+markers', name='Min Score', line=dict(color='green', dash='dot', width=2)
            ))

            fig.add_trace(go.Scatter(
                x=filtered_df["Date"], y=filtered_df["Max Score"],
                mode='lines+markers', name='Max Score', line=dict(color='red', dash='dash', width=2)
            ))

            fig.update_layout(
                title="Score Trends Over Selected Dates",
                xaxis_title="Date",
                yaxis_title="Score",
                legend_title="Metrics",
                margin=dict(t=60),
                hovermode="x unified"
            )

        st.plotly_chart(fig, use_container_width=True)

#................
    # score 
    st.subheader("Comprehensive Data Matrix")

    st.dataframe(
        filtered_df.style.format({
            "Total Score": "{:.0f}",
            "Average Score": "{:.2f}",
            "Min Score": "{:.0f}",
            "Max Score": "{:.0f}"
        }),
        use_container_width=True
    )
    
    
    st.subheader("Calories Burned Prediction")

    col1, col2, col3 = st.columns(3)

    with col1:
        user_weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=70.0)

    with col2:
        timer = st.number_input("Timer (seconds)", min_value=10.0, max_value=1000.0, value=15.0)

    with col3:
        MET = st.number_input("MET", min_value=0.0, max_value=10.0, value=3.5)

    # Compute total kicks per day
    filtered_df["Total Kicks"] = filtered_df["Total Score"] / 10
    kick_duration_per_kick = timer / filtered_df["Total Kicks"].sum()

    # Compute duration per day in hours
    filtered_df["Duration (hrs)"] = (filtered_df["Total Kicks"] * kick_duration_per_kick) / 3600

    # Compute calories burned per day
    filtered_df["Calories Burned"] = MET * user_weight * filtered_df["Duration (hrs)"]

    st.markdown("**Estimated Calories Burned per Date**")
    st.dataframe(
        filtered_df[["Date", "Total Score", "Total Kicks", "Duration (hrs)", "Calories Burned"]].style.format({
            "Total Score": "{:.0f}",
            "Total Kicks": "{:.0f}",
            "Duration (hrs)": "{:.3f}",
            "Calories Burned": "{:.2f}"
        }),
        use_container_width=True
    )

if st.button("🔄 Refresh Data Now"):
    st.cache_data.clear()
    df = load_data_from_gsheets()
    st.success("Data refreshed!")
else:
    df = load_data_from_gsheets()

if st.button("🔄 Refresh Data Now"):
    st.cache_data.clear()
    score_df = load_score_data()
    st.success("Data refreshed!")
else:
    filtered_df = load_score_data()
