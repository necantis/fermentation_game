import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import datetime
import os
import json

# Constants
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "Beacon_v02"
CREDENTIALS_FILE = "credentials.json"
LOCAL_LOG_FILE = "game_logs_fallback.csv"

def connect_to_gsheet():
    """
    Connect to Google Sheets using st.secrets (Cloud) or credentials.json (Local).
    """
    # 1. Try Streamlit Secrets (Cloud / production)
    try:
        if "gcp_service_account" in st.secrets:
            try:
                # Create credentials from the secrets dict
                creds_dict = dict(st.secrets["gcp_service_account"])
                creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
                client = gspread.authorize(creds)
                spreadsheet = client.open(SHEET_NAME)
                return spreadsheet.sheet1
            except Exception as e:
                print(f"GSheet Connection Error (Secrets): {e}")
                return None
    except Exception:
        # st.secrets access failed (e.g. no secrets.toml found locally)
        pass

    # 2. Try Local File (credentials.json)
    if os.path.exists(CREDENTIALS_FILE):
        try:
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
            client = gspread.authorize(creds)
            spreadsheet = client.open(SHEET_NAME)
            return spreadsheet.sheet1
        except Exception as e:
            print(f"GSheet Connection Error (File): {e}")
            return None
            
    print("No valid credentials found.")
    return None

def log_data(data_dict):
    """
    Log data to Google Sheet, fallback to local CSV.
    data_dict: dict of Record
    """
    # 1. Add Timestamp
    data_dict['timestamp'] = datetime.datetime.now().isoformat()
    
    # 2. Try Google Sheet
    sheet = connect_to_gsheet()
    success = False
    if sheet:
        try:
            # Check if sheet is empty (no headers)
            if not sheet.get_all_values():
                headers = [
                    'timestamp', 'prolific_id', 'round', 'batch_num', 
                    'scenario_id', 'scenario_name', 
                    'assessment', 'action', 'seq_score',
                    'ai_used', 'text_changed', 
                    'ai_assessment_text', 'user_assessment_final',
                    'tutorial_duration_seconds'
                ]
                sheet.append_row(headers)

            # Order values based on headers
            headers = [
                'timestamp', 'prolific_id', 'round', 'batch_num', 
                'scenario_id', 'scenario_name', 
                'assessment', 'action', 'seq_score',
                'ai_used', 'text_changed', 
                'ai_assessment_text', 'user_assessment_final',
                'tutorial_duration_seconds'
            ]
            
            row = [str(data_dict.get(h, '')) for h in headers]
            sheet.append_row(row)
            success = True
        except Exception as e:
            print(f"GSheet Log Error: {e}")
    
    # 3. Local Fallback (Always log locally as backup)
    df = pd.DataFrame([data_dict])
    if not os.path.exists(LOCAL_LOG_FILE):
        df.to_csv(LOCAL_LOG_FILE, index=False)
    else:
        df.to_csv(LOCAL_LOG_FILE, mode='a', header=False, index=False)
        
    return success

def log_feedback(feedback_dict):
    """
    Log feedback and total time to Google Sheet (Sheet 2) or fallback CSV.
    feedback_dict: {timestamp, prolific_id, total_time_seconds, tutorial_duration_seconds, feedback_text}
    """
    # 1. Add Timestamp if not present
    if 'timestamp' not in feedback_dict:
        feedback_dict['timestamp'] = datetime.datetime.now().isoformat()
        
    # 2. Try Google Sheet
    sheet = connect_to_gsheet()
    success = False
    
    if sheet:
        try:
            # Try to get or create a second worksheet "Feedback"
            spreadsheet = sheet.spreadsheet
            try:
                worksheet = spreadsheet.worksheet("Feedback")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title="Feedback", rows=100, cols=10)
                # Add headers
                worksheet.append_row(['timestamp', 'prolific_id', 'total_time_seconds', 'tutorial_duration_seconds', 'feedback_text'])
                
            row = [
                str(feedback_dict.get('timestamp', '')),
                str(feedback_dict.get('prolific_id', '')),
                str(feedback_dict.get('total_time_seconds', '')),
                str(feedback_dict.get('tutorial_duration_seconds', '')),
                str(feedback_dict.get('feedback_text', ''))
            ]
            worksheet.append_row(row)
            success = True
        except Exception as e:
            print(f"GSheet Feedback Log Error: {e}")

    # 3. Local Fallback
    fallback_file = "feedback_logs_fallback.csv"
    df = pd.DataFrame([feedback_dict])
    if not os.path.exists(fallback_file):
        df.to_csv(fallback_file, index=False)
    else:
        df.to_csv(fallback_file, mode='a', header=False, index=False)
        
    return success
