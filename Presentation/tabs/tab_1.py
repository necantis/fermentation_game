import streamlit as st
import pandas as pd
from Presentation.config import COLOR_PALETTE

GAME_APP_URL = "https://fermentation-game.streamlit.app/"
DASHBOARD_URL = "https://fermentation-game-dashboard.streamlit.app/"

def render_tab_1(df, df_feedback):
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 24px; margin-bottom: 25px; border-left: 4px solid {COLOR_PALETTE['secondary']};">
            <span style="font-size: 0.85rem; letter-spacing: 0.15em; color: {COLOR_PALETTE['secondary']}; font-weight: 600; text-transform: uppercase;">
                Interactive Session & Telemetry Pipeline
            </span>
            <h2 style="margin-top: 5px; font-weight: 700; font-size: 2.2rem;">
                The Experiment (The Fermentation Game)
            </h2>
            <p style="color: {COLOR_PALETTE['text_muted']}; font-size: 1.05rem; margin-top: 5px; max-width: 950px; line-height: 1.6;">
                Interact with the simulation environment below to perform troubleshooting steps (adjusting dissolved oxygen, temperature, pressure). 
                As you perform actions, real-time telemetry metrics are captured and appended to the data pipeline.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Iframe container
    st.markdown("### 1. Embedded Bioreactor Simulator")
    st.caption(f"Game URL: {GAME_APP_URL}")
    iframe_html = """
    <div class="iframe-container" style="position: relative; width: 100%; height: 600px; border-radius: 12px; overflow: hidden; background: #1e293b; margin-bottom: 25px;">
        <iframe src="https://fermentation-game.streamlit.app/" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;" title="Fermentation Troubleshooting Game"></iframe>
    </div>
    """
    st.markdown(iframe_html, unsafe_allow_html=True)
    st.link_button("Open Game In New Tab", GAME_APP_URL)
    st.caption(f"Presentation dashboard URL: {DASHBOARD_URL}")

    # Data logs collected underneath
    st.markdown("### 2. Telemetry Log Capture (Real-time schema)")
    st.markdown("Underneath the interface, the simulation captures these specific telemetry variables:")
    
    if df is not None and not df.empty:
        st.dataframe(df[['timestamp', 'prolific_id', 'round', 'scenario_name', 'ai_used', 'text_changed', 'round_duration_seconds']].tail(5), use_container_width=True)
    else:
        st.warning("No telemetry traces found in pipeline.")

    # Persona C post-doc template
    st.markdown("---")
    st.markdown("### 3. Replicable Pandas Parsing Template (For Persona C)")
    st.markdown(
        "To satisfy researchers, we document our parsing methodology below. This clean python snippet parses the raw event logs "
        "using standard pandas features. Feel free to copy and adapt this in your own research."
    )

    code_template = """import pandas as pd
import numpy as np
import difflib

def parse_fermentation_logs(file_path):
    # 1. Load telemetry logs, skipping corrupted lines automatically
    df = pd.read_csv(file_path, on_bad_lines='skip')
    
    # 2. Repair schema gaps and fill missing boolean/numeric fields
    df['ai_used'] = df['ai_used'].astype(str).map(
        {'True': True, 'False': False, 'true': True, 'false': False}
    ).fillna(False)
    
    df['text_changed'] = df['text_changed'].astype(str).map(
        {'True': True, 'False': False, 'true': True, 'false': False}
    ).fillna(False)
    
    # Convert duration and score to numeric fallbacks
    df['round_duration_seconds'] = pd.to_numeric(df['round_duration_seconds'], errors='coerce').fillna(0.0)
    df['seq_score'] = pd.to_numeric(df['seq_score'], errors='coerce').fillna(0.0)
    
    # 3. Sort by participant and timestamp to calculate exact task durations dynamically
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.sort_values(['prolific_id', 'timestamp'])
    df['time_diff'] = df.groupby('prolific_id')['timestamp'].diff().dt.total_seconds().fillna(0.0)
    
    # Backfill missing duration using timestamp diff (if duration is 0)
    df['round_duration_seconds'] = df.apply(
        lambda r: r['time_diff'] if r['round_duration_seconds'] <= 0.1 and 0.0 < r['time_diff'] < 3600.0 else r['round_duration_seconds'],
        axis=1
    )
    
    # 4. Compute answer metrics (character length and text complexity)
    df['text_len'] = df['assessment'].fillna("").astype(str).apply(len)
    
    def calc_complexity(text):
        if not isinstance(text, str) or not text.strip():
            return 0.0
        words = text.split()
        return float(len(words) * (sum(len(w) for w in words) / len(words)))
        
    df['complexity'] = df['assessment'].apply(calc_complexity)
    
    # 5. Compute lexical similarity ratio between user input and AI advice
    def calc_similarity(row):
        if not row['ai_used'] or pd.isna(row['ai_assessment_text']):
            return 0.0
        user_text = str(row['assessment'])
        ai_text = str(row['ai_assessment_text'])
        return float(difflib.SequenceMatcher(None, user_text, ai_text).ratio())
        
    df['ai_similarity'] = df.apply(calc_similarity, axis=1)
    
    return df

# Usage
# df_clean = parse_fermentation_logs("game_logs_fallback.csv")
# print(df_clean.head())
"""
    st.code(code_template, language="python")
