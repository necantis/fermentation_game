import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import gspread
from google.oauth2.service_account import Credentials
import os
import difflib

# Import workshop pipeline functions
from Presentation.lonza_pipeline import ingest_and_unify_lonza, calculate_correlations_and_ttests, pre_render_bootstrap_importance

# Constants (matching project defaults)
DATA_FILE = "game_logs_fallback.csv"
FEEDBACK_FILE = "feedback_logs_fallback.csv"
SHEET_NAME = "Beacon_v02"
CREDENTIALS_FILE = "credentials.json"

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

GAME_LOG_COLS = [
    'timestamp', 'prolific_id', 'round', 'batch_num', 
    'scenario_id', 'scenario_name', 
    'assessment', 'action', 'seq_score',
    'ai_used', 'text_changed', 
    'ai_assessment_text', 'user_assessment_final',
    'tutorial_duration_seconds',
    'round_duration_seconds'
]

FEEDBACK_LOG_COLS = [
    'timestamp', 'prolific_id', 'total_time_seconds', 
    'tutorial_duration_seconds', 'feedback_text'
]

def connect_to_gsheet():
    """Connect to Google Sheets using st.secrets or local credentials.json."""
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
            client = gspread.authorize(creds)
            return client.open(SHEET_NAME)
    except Exception:
        pass

    if os.path.exists(CREDENTIALS_FILE):
        try:
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
            client = gspread.authorize(creds)
            return client.open(SHEET_NAME)
        except Exception:
            pass
    return None

def calc_complexity(text):
    """Calculates text complexity proxy: word length * word count."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    words = text.split()
    if not words:
        return 0.0
    avg_word_len = sum(len(w) for w in words) / len(words)
    return float(avg_word_len * len(words))

def calc_similarity(row):
    """Calculates diff ratio similarity between user assessment and AI suggestion."""
    if not row.get('ai_used') or pd.isna(row.get('ai_assessment_text')):
        return 0.0
    user_text = str(row.get('assessment', ''))
    ai_text = str(row.get('ai_assessment_text', ''))
    if not user_text.strip() or not ai_text.strip():
        return 0.0
    return float(difflib.SequenceMatcher(None, user_text, ai_text).ratio())

@st.cache_data(ttl=120)
def load_and_preprocess_data():
    """
    Cached function to load data from GSheet or local files, repair schema gaps,
    backfill time, compute text complexity/similarities, and return clean DataFrames.
    """
    data = None
    feedback = None
    
    # 1. Try Google Sheets first
    try:
        sh = connect_to_gsheet()
        if sh:
            try:
                records = sh.sheet1.get_all_records()
                if records:
                    data = pd.DataFrame(records)
            except Exception:
                pass
            
            try:
                ws_fb = sh.worksheet("Feedback")
                records_fb = ws_fb.get_all_records()
                if records_fb:
                    feedback = pd.DataFrame(records_fb)
            except Exception:
                pass
    except Exception:
        pass

    # 2. Fallback to Local CSVs
    rel_data_file = DATA_FILE
    rel_feedback_file = FEEDBACK_FILE
    
    if not os.path.exists(rel_data_file):
        rel_data_file = os.path.join("..", DATA_FILE)
    if not os.path.exists(rel_feedback_file):
        rel_feedback_file = os.path.join("..", FEEDBACK_FILE)

    if data is None or data.empty:
        if os.path.exists(rel_data_file):
            try:
                data = pd.read_csv(rel_data_file, on_bad_lines='skip')
            except Exception:
                pass

    if feedback is None or feedback.empty:
        if os.path.exists(rel_feedback_file):
            try:
                feedback = pd.read_csv(rel_feedback_file, on_bad_lines='skip')
            except Exception:
                pass

    # 3. Processing and schema correction
    if data is not None and not data.empty:
        # Fill missing columns
        for col in GAME_LOG_COLS:
            if col not in data.columns:
                if col in ['round_duration_seconds', 'tutorial_duration_seconds']:
                    data[col] = 0.0
                elif col == 'ai_used':
                    data[col] = False
                else:
                    data[col] = ""

        # Repair Boolean fields
        data['ai_used'] = data['ai_used'].astype(str).map(
            {'True': True, 'False': False, 'true': True, 'false': False}
        ).fillna(False)
        data['text_changed'] = data['text_changed'].astype(str).map(
            {'True': True, 'False': False, 'true': True, 'false': False}
        ).fillna(False)

        # Numeric conversions
        data['round_duration_seconds'] = pd.to_numeric(data['round_duration_seconds'], errors='coerce').fillna(0.0)
        data['seq_score'] = pd.to_numeric(data['seq_score'], errors='coerce').fillna(0.0)

        # Process timestamp and diff
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
            data = data.sort_values(['prolific_id', 'timestamp'])
            data['time_diff'] = data.groupby('prolific_id')['timestamp'].diff().dt.total_seconds().fillna(0.0)
            
            # Backfill round durations
            def get_valid_duration(row):
                if row['round_duration_seconds'] > 0.1:
                    return row['round_duration_seconds']
                if 0.0 < row['time_diff'] < 3600.0:
                    return row['time_diff']
                return 0.0
            
            data['round_duration_seconds'] = data.apply(get_valid_duration, axis=1)

        # Add metric calculations
        data['text_len'] = data['assessment'].fillna("").astype(str).apply(len)
        data['complexity'] = data['assessment'].apply(calc_complexity)
        data['ai_similarity'] = data.apply(calc_similarity, axis=1)
        
        # User groupings
        ai_users = data[data['ai_used'] == True]['prolific_id'].unique()
        data['user_group'] = data['prolific_id'].apply(lambda x: 'AI User' if x in ai_users else 'Control (No AI)')

    if feedback is not None and not feedback.empty:
        for col in FEEDBACK_LOG_COLS:
            if col not in feedback.columns:
                feedback[col] = 0.0 if 'seconds' in col else ""
        feedback['total_time_seconds'] = pd.to_numeric(feedback['total_time_seconds'], errors='coerce').fillna(0.0)

    return data, feedback

def calculate_ttest_summary(data, group_col, value_col, group1_val=True, group2_val=False):
    """Utility to perform a t-test and return styled results."""
    g1 = data[data[group_col] == group1_val][value_col].dropna()
    g2 = data[data[group_col] == group2_val][value_col].dropna()
    
    if len(g1) < 2 or len(g2) < 2:
        return {"t_stat": 0.0, "p_val": 1.0, "significant": False, "g1_mean": 0.0, "g2_mean": 0.0, "message": "Insufficient data for t-test"}
        
    t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False)
    significant = p_val < 0.05
    sig_text = "Significant (p < 0.05)" if significant else "Not Significant"
    
    msg = f"t = {t_stat:.3f}, p = {p_val:.4f} ({sig_text})"
    return {
        "t_stat": float(t_stat),
        "p_val": float(p_val),
        "significant": significant,
        "g1_mean": float(g1.mean()),
        "g2_mean": float(g2.mean()),
        "message": msg
    }

@st.cache_data(show_spinner="Loading workshop data…")
def load_lonza_and_stats():
    """
    Ingests and cleans workshop files, computes pre-rendered bootstrap stats, 
    and returns (df_unified, bootstrap_data, stats_data).
    """
    # Locate paths — anchored to this file's location so they always resolve
    # correctly regardless of what directory Streamlit is launched from.
    _here = os.path.dirname(os.path.abspath(__file__))          # .../Presentation
    _repo = os.path.dirname(_here)                               # .../fermentation_game
    w_path = os.path.join(_repo, "Tests", "Workshop_Wooclap.csv")
    s_path = os.path.join(_repo, "Tests", "Workshop_Scores.csv")
        
    df_unified = ingest_and_unify_lonza(w_path, s_path)
    bootstrap_data = pre_render_bootstrap_importance(df_unified)
    
    # Load game data for correlations and t-tests
    df_game, _ = load_and_preprocess_data()
    stats_data = calculate_correlations_and_ttests(df_game)
    
    return df_unified, bootstrap_data, stats_data
