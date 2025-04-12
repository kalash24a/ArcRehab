import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Constants
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "16pZcstLCjce244Os-_tzjazCNc90BgfoIky_3Y0vQAM"
VITALS_SHEET_NAME = "Sheet2"

@st.cache_data(show_spinner=False)
def load_data_from_gsheets():
    try:
        # Read credentials from Streamlit secrets
        service_account_info = dict(st.secrets["google_service_account"])
        
        # Fix multiline private key if necessary
        if isinstance(service_account_info['private_key'], str) and "\\n" in service_account_info['private_key']:
            service_account_info['private_key'] = service_account_info['private_key'].replace("\\n", "\n")

        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        # Fetch data
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=VITALS_SHEET_NAME).execute()
        values = result.get("values", [])

        if not values:
            return pd.DataFrame()

        headers, data = values[0], values[1:]
        df = pd.DataFrame(data, columns=headers)

        # Clean and process DataFrame
        df = df[df['Date'] != '']
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
        df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
        df['Heart Rate'] = pd.to_numeric(df['Heart Rate'], errors='coerce')
        df['SpO2'] = pd.to_numeric(df['SpO2'], errors='coerce')
        df = df.dropna()
        df['Timestamp'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))

        return df

    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame()
