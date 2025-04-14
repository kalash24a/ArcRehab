import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Constants
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1z3XFcHbPjdvAmebNm1MlJUbgxWiy8X3XINA6PYTvs6U"
SCORE_SHEET_NAME = "Sheet2"

@st.cache_data(show_spinner=False)
def load_score_data():
    try:
        # Load service account info from Streamlit secrets
        service_account_info = dict(st.secrets["google_service_account"])
        
        # Fix multiline private key if stored with literal "\n"
        if isinstance(service_account_info['private_key'], str) and "\\n" in service_account_info['private_key']:
            service_account_info['private_key'] = service_account_info['private_key'].replace("\\n", "\n")

        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        # Fetch scores from the sheet
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SCORE_SHEET_NAME}!A1:C").execute()
        values = result.get("values", [])

        if not values:
            return pd.DataFrame()

        headers, data = values[0], values[1:]
        df = pd.DataFrame(data, columns=headers)

        # Clean and process the DataFrame
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
        df = df.dropna()
        df['Timestamp'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))

        return df

    except Exception as e:
        st.error(f"Error loading score data from Google Sheets: {e}")
        return pd.DataFrame()
