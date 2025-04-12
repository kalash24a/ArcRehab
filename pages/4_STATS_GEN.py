import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from utils import load_data_from_gsheets


df = load_data_from_gsheets()
st.title("📊 Daily Vital Statistics Overview")

metrics = ['Temperature', 'Heart Rate', 'SpO2']
combined_stats = pd.DataFrame()

for metric in metrics:
    temp_stats = df.groupby(df['Date'].dt.strftime('%d-%m-%Y'))[metric].agg(['count', 'mean', 'median', 'max', 'min']).reset_index()
    temp_stats = temp_stats.rename(columns={'Date': 'Formatted Date'})
    temp_stats['Metric'] = metric
    combined_stats = pd.concat([combined_stats, temp_stats], ignore_index=True)

combined_stats = combined_stats.rename(columns={'Formatted Date': 'Date'})
combined_stats = combined_stats.melt(id_vars=['Date', 'Metric'], var_name='Stat', value_name='Value')

st.subheader("📊 Statistics Bar Chart")
fig_bar = px.bar(combined_stats, x='Date', y='Value', color='Stat', barmode='group')
fig_bar.update_layout(legend_title="Stat", legend=dict(orientation="h", y=-0.3))
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📈 Statistics Line Chart")
fig_line = px.line(combined_stats, x='Date', y='Value', color='Stat', line_dash='Metric', markers=True)
fig_line.update_layout(legend_title="Stat", legend=dict(orientation="h", y=-0.3))
st.plotly_chart(fig_line, use_container_width=True)





