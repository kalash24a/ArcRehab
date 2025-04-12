import streamlit as st
from utils import load_data_from_gsheets
import numpy as np
import pandas as pd
import plotly.express as px
from utils import load_data_from_gsheets
from utils2 import load_score_data
st.title(" DATASET")
st.markdown("---")

st.subheader("📋 MEDICAL DATASET")
df = load_data_from_gsheets()
preview_df = df.copy()
preview_df['Date'] = preview_df['Date'].dt.strftime('%d-%m-%Y')
preview_df['Time'] = preview_df['Time'].astype(str)

st.dataframe(preview_df, use_container_width=True)
st.download_button("⬇ Download Full Dataset", df.to_csv(index=False), "Medical_Readings.csv", "text/csv")


# Summary Table
st.markdown("---")
st.subheader("📋 AGGREGATED METRIC TABLE")

available_dates = sorted(df['Date'].dt.strftime('%d-%m-%Y').unique(), reverse=True)
selected_dates = st.multiselect("Select date(s) to view stats table:", available_dates, default=available_dates[:1])

if selected_dates:
    summary_dict = {metric: {'count': 0, 'mean': [], 'median': [], 'max': [], 'min': []} for metric in ['SpO2', 'Temperature', 'Heart Rate']}

    for date_str in selected_dates:
        df_selected = df[df['Date'].dt.strftime('%d-%m-%Y') == date_str]
        for metric in summary_dict.keys():
            values = df_selected[metric].dropna()
            summary_dict[metric]['count'] += values.count()
            summary_dict[metric]['mean'].append(values.mean())
            summary_dict[metric]['median'].append(values.median())
            summary_dict[metric]['max'].append(values.max())
            summary_dict[metric]['min'].append(values.min())

    summary_rows = []
    for metric in ['SpO2', 'Temperature', 'Heart Rate']:
        data = summary_dict[metric]
        summary_rows.append({
            'Metric': metric,
            'Count': data['count'],
            'Mean': np.mean(data['mean']),
            'Median': np.median(data['median']),
            'Max': np.max(data['max']),
            'Min': np.min(data['min'])
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df[['Metric', 'Count', 'Mean', 'Median', 'Max', 'Min']]

    st.dataframe(summary_df.style.format({'Mean': '{:.2f}', 'Median': '{:.2f}', 'Max': '{:.2f}', 'Min': '{:.2f}'}), use_container_width=True)
    csv = summary_df.to_csv(index=False)
    st.download_button("⬇ Download Summary Table", csv, "Daily_Summary.csv", "text/csv")
else:
    st.info("Please select at least one date to display the summary table.")
 
st.markdown("---")   
 
#scorecard
st.subheader("📋 SCORE DATA")
# Load the score data
score_df = load_score_data()

unique_dates = score_df['Date'].dt.date.unique()
selected_dates = st.multiselect("Select Dates", options=unique_dates, default=unique_dates)

filtered_df = score_df[score_df['Date'].dt.date.isin(selected_dates)]

st.dataframe(filtered_df.sort_values("Timestamp"), use_container_width=True)

