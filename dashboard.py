import streamlit as st
import pandas as pd
import altair as alt
import scipy.stats as stats
import gspread
from google.oauth2.service_account import Credentials
import os
import difflib

st.set_page_config(page_title="Fermentation Game Analytics", layout="wide")

st.title("Fermentation Game Analytics")
st.markdown("### Hypothesis Testing & Data Overview")
st.info("""
**Definitions:**
*   **AI Used**: Classified **per round**. A participant can use AI in round 1 (True) and not in round 2 (False).
*   **AI Score**: The percentage of rounds where a specific participant used AI.
""")

# Load Data
DATA_FILE = "game_logs_fallback.csv"
FEEDBACK_FILE = "feedback_logs_fallback.csv"

# Log Columns (Current Schema)
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

# Constants
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "Beacon_v02"

def connect_to_gsheet():
    """Connect to Google Sheets using st.secrets (Cloud) or credentials.json (Local)."""
    try:
        if "gcp_service_account" in st.secrets:
            # Create credentials from the secrets dict
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
            client = gspread.authorize(creds)
            return client.open(SHEET_NAME)
    except Exception as e:
        pass

    # Local fallback
    if os.path.exists("credentials.json"):
        try:
            creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
            client = gspread.authorize(creds)
            return client.open(SHEET_NAME)
        except Exception:
            pass
    return None

@st.cache_data(ttl=60) # Cache for 60 seconds to allow near-real-time updates
def load_data():
    data = None
    feedback = None
    
    # --- TRY GOOGLE SHEETS FIRST ---
    try:
        sh = connect_to_gsheet()
        if sh:
            # Load Game Logs (Sheet1)
            try:
                ws = sh.sheet1
                records = ws.get_all_records()
                if records:
                    data = pd.DataFrame(records)
            except Exception as e:
                st.warning(f"Could not load Game Logs from GSheet: {e}")

            # Load Feedback Logs (Worksheet 'Feedback')
            try:
                ws_feedback = sh.worksheet("Feedback")
                records_fb = ws_feedback.get_all_records()
                if records_fb:
                    feedback = pd.DataFrame(records_fb)
            except Exception as e:
                # Limit warning if feedback sheet just doesn't exist yet
                pass
    except Exception as e:
         st.error(f"GSheet Connection failed: {e}")

    # --- FALLBACK TO LOCAL CSV IF GSHEET FAILED OR EMPTY ---
    if data is None or data.empty:
        if os.path.exists(DATA_FILE):
            try:
                data = pd.read_csv(DATA_FILE, on_bad_lines='warn')
            except Exception:
                pass

    if feedback is None or feedback.empty:
        if os.path.exists(FEEDBACK_FILE):
             try:
                 feedback = pd.read_csv(FEEDBACK_FILE, on_bad_lines='warn')
             except Exception:
                 pass
    
    # --- PROCESSING & REPAIR (APPLY TO WHATEVER SOURCE WE GOT) ---
    if data is not None and not data.empty:
        try:
            # STANDARD COLUMN REPAIR
            # Ensure all expected columns exist, filling missing ones with defaults
            for col in GAME_LOG_COLS:
                if col not in data.columns:
                    if col in ['round_duration_seconds', 'tutorial_duration_seconds']:
                        data[col] = 0.0
                    elif col == 'ai_used':
                        data[col] = False
                    else:
                        data[col] = ""

            # Ensure boolean columns are proper booleans (handle string 'True'/'False')
            if 'ai_used' in data.columns:
                # Convert to string first to handle mixed types, then map
                data['ai_used'] = data['ai_used'].astype(str).map({'True': True, 'False': False, 'true': True, 'false': False}).fillna(False)
            
            # Numeric conversion
            if 'round_duration_seconds' in data.columns:
                 data['round_duration_seconds'] = pd.to_numeric(data['round_duration_seconds'], errors='coerce').fillna(0)

            # --- BACKFILL DURATION FOR HISTORICAL DATA ---
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
                data = data.sort_values(['prolific_id', 'timestamp'])
                
                # Calculate time difference between consecutive rows for same user
                data['time_diff'] = data.groupby('prolific_id')['timestamp'].diff().dt.total_seconds().fillna(0)
                
                # Create effective plotting column
                def get_valid_duration(row):
                    if row['round_duration_seconds'] > 0.1:
                        return row['round_duration_seconds']
                    if 0 < row['time_diff'] < 3600: # heuristic: < 1 hour
                        return row['time_diff']
                    return 0.0
                
                data['round_duration_seconds'] = data.apply(get_valid_duration, axis=1)

        except Exception as e:
            st.error(f"Error processing game data: {e}")

    if feedback is not None and not feedback.empty:
        try:
             # Repair Feedback Columns
             for col in FEEDBACK_LOG_COLS:
                 if col not in feedback.columns:
                     feedback[col] = 0 if 'seconds' in col else ""
        except Exception as e:
            st.error(f"Error processing feedback data: {e}")
            
    return data, feedback

df, df_feedback = load_data()

if df is None or df.empty:
    st.warning(f"No game data found in {DATA_FILE}.")
    st.stop()

# --- PREPROCESSING ---
# Filter out rows that might be test/tutorial if needed, or focused on actual rounds
# round_prob = df[df['scenario_id'] != 1] # Exclude final success state for some analysis

# --- OVERVIEW ---
st.header("1. Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Log Entries", len(df))
col1.metric("Unique Players", df['prolific_id'].nunique())

if df_feedback is not None and not df_feedback.empty:
    avg_time = df_feedback['total_time_seconds'].mean()
    col2.metric("Avg Total Duration (s)", f"{avg_time:.2f}")
    
    st.subheader("Total Time Distribution")
    st.bar_chart(df_feedback['total_time_seconds'])


# ... (Imports and Config remain same)

# --- HELPER: STATS ---
def calculate_ttest(data, group_col, value_col, group1_val=True, group2_val=False):
    """
    Calculates T-Test for two independent groups.
    Returns formatted string with T-stat, p-value, and significance.
    """
    g1 = data[data[group_col] == group1_val][value_col].dropna()
    g2 = data[data[group_col] == group2_val][value_col].dropna()
    
    if len(g1) < 2 or len(g2) < 2:
        return "Insufficient data for T-Test"
    
    t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False)
    sig = "Significant (**p < 0.05**)" if p_val < 0.05 else "Not Significant"
    
    g1_mean = g1.mean()
    g2_mean = g2.mean()
    
    return f"**T-Test**: {group1_val} (Mean={g1_mean:.2f}) vs {group2_val} (Mean={g2_mean:.2f}) -> t={t_stat:.2f}, p={p_val:.4f} ({sig})"

# ... (Load Data remains same)

# --- HYPOTHESIS 1: COORDINATION COST (TIME) ---
st.header("H1: Coordination Cost (Time)")
st.markdown("**Hypothesis:** Higher AI usage increases task duration.")

# 1. Round Duration Analysis (Granular)
if 'round_duration_seconds' in df.columns and df['round_duration_seconds'].sum() > 0:
    st.subheader("Round Duration vs AI Usage")
    
    # 1. Average Time per Round (Metric)
    avg_round_time = df['round_duration_seconds'].mean()
    st.metric("Global Avg Time per Round", f"{avg_round_time:.2f} s")
    
    st.caption("Note: '0' duration bars indicate missing timestamp data in older logs.")

    # 2. Stacked Bar Chart (Red/Blue Split)
    st.subheader("Participant Time Breakdown (Red=No AI, Blue=AI)")
    
    # Classify users: Did they EVER use AI?
    ai_users = df[df['ai_used'] == True]['prolific_id'].unique()
    df['user_group'] = df['prolific_id'].apply(lambda x: 'AI User' if x in ai_users else 'Control (No AI)')
    
    # Define color scale for bars based on specific round usage
    # We want Red for No AI, Blue for AI
    color_scale = alt.Scale(domain=[False, True], range=['#d62728', '#1f77b4'])
    
    chart_stack_split = alt.Chart(df).mark_bar().encode(
        x=alt.X('prolific_id:N', title='Participant'),
        y=alt.Y('round_duration_seconds:Q', title='Duration (s)'),
        color=alt.Color('ai_used:N', scale=color_scale, title="AI Used (Round)"),
        column=alt.Column('user_group:N', title="Group"),
        tooltip=['prolific_id', 'round', 'round_duration_seconds', 'ai_used', 'scenario_name'],
        order=alt.Order('round') # Stack by round order
    ).properties(title="Time Breakdown by Group & AI Usage")
    
    st.altair_chart(chart_stack_split, use_container_width=True)

else:
    st.info("Insufficient round duration data for granular analysis.")

# ... (H1 Total Time Aggregated remains similar, maybe add stats if possible but N is low)

# --- HYPOTHESIS 2: DELEGATION EFFECT (LENGTH) ---
st.header("H2: Delegation Effect (Answer Length)")
st.markdown("**Hypothesis:** Higher AI usage reduces answer length.")

# Calculate text length
df['text_len'] = df['assessment'].fillna("").astype(str).apply(len)

# Stats
st.markdown(calculate_ttest(df, 'ai_used', 'text_len'))

# Calculate Complexity (ARI Proxy: 4.71*(chars/words) + 0.5*(words/sentences) - 21.43)
# Simplified here: just avg word length + len
def calc_complexity(text):
    if not isinstance(text, str) or not text.strip(): return 0
    words = text.split()
    if not words: return 0
    avg_word_len = sum(len(w) for w in words) / len(words)
    return avg_word_len * len(words) # Rough proxy for "information density"

df['complexity'] = df['assessment'].apply(calc_complexity)

# Calculate Similarity to AI
def calc_similarity(row):
    # Only relevant if AI was used and text exists
    if not row['ai_used'] or pd.isna(row['ai_assessment_text']): return 0.0
    user_text = str(row['assessment'])
    ai_text = str(row['ai_assessment_text'])
    return difflib.SequenceMatcher(None, user_text, ai_text).ratio()

df['ai_similarity'] = df.apply(calc_similarity, axis=1)

# Stats for Length
st.markdown("#### Answer Length (Chars)")
st.markdown(calculate_ttest(df, 'ai_used', 'text_len'))

# Viz Length
chart_h2_len = alt.Chart(df).mark_boxplot().encode(
    x='ai_used:N', y='text_len:Q', color='ai_used:N'
).properties(title="Length")

# Stats for Complexity
st.markdown("#### Complexity (Word Length * Word Count)")
st.markdown(calculate_ttest(df, 'ai_used', 'complexity'))

# Viz Complexity
chart_h2_comp = alt.Chart(df).mark_boxplot().encode(
    x='ai_used:N', y='complexity:Q', color='ai_used:N'
).properties(title="Complexity")

col_h2_1, col_h2_2 = st.columns(2)
col_h2_1.altair_chart(chart_h2_len, use_container_width=True)
col_h2_2.altair_chart(chart_h2_comp, use_container_width=True)

# SIMILARITY ANALYSIS: Copiers vs Improvers
st.subheader("Deep Dive: Copiers vs Improvers (Among AI Users)")
ai_only_df = df[df['ai_used'] == True].copy()

if not ai_only_df.empty and 'ai_similarity' in ai_only_df.columns:
    # 1. Define Split (Median)
    median_sim = ai_only_df['ai_similarity'].median()
    ai_only_df['strategy'] = ai_only_df['ai_similarity'].apply(lambda x: 'Copier (High Sim)' if x > median_sim else 'Improver (Low Sim)')
    
    st.markdown(f"**Median Similarity**: {median_sim:.2f}")
    
    # 2. Comparison Metrics
    st.markdown("#### Strategy Comparison (Copiers vs Improvers)")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.caption("Complexity")
        st.markdown(calculate_ttest(ai_only_df, 'strategy', 'complexity', 'Copier (High Sim)', 'Improver (Low Sim)'))
        chart_s1 = alt.Chart(ai_only_df).mark_boxplot().encode(x='strategy:N', y='complexity:Q', color='strategy:N')
        st.altair_chart(chart_s1, use_container_width=True)
        
    with col_s2:
        st.caption("Time (Seconds)")
        st.markdown(calculate_ttest(ai_only_df, 'strategy', 'round_duration_seconds', 'Copier (High Sim)', 'Improver (Low Sim)'))
        chart_s2 = alt.Chart(ai_only_df).mark_boxplot().encode(x='strategy:N', y='round_duration_seconds:Q', color='strategy:N')
        st.altair_chart(chart_s2, use_container_width=True)

    with col_s3:
        st.caption("Perceived Difficulty")
        st.markdown(calculate_ttest(ai_only_df, 'strategy', 'seq_score', 'Copier (High Sim)', 'Improver (Low Sim)'))
        chart_s3 = alt.Chart(ai_only_df).mark_boxplot().encode(x='strategy:N', y='seq_score:Q', color='strategy:N')
        st.altair_chart(chart_s3, use_container_width=True)

else:
    st.info("No AI usage data to analyze similarity.")

# --- PARTICIPANT LEVEL ANALYSIS ---
st.header("Participant Level Analysis")
st.markdown("Aggregating metrics by Participant to handle 'AI Score' (% of rounds AI was used).")

# Aggregate
user_agg = df.groupby('prolific_id').agg({
    'ai_used': 'mean', # % of rounds used
    'round_duration_seconds': 'mean',
    'complexity': 'mean',
    'seq_score': 'mean',
    'text_len': 'mean'
}).reset_index()

user_agg.rename(columns={'ai_used': 'ai_score', 'round_duration_seconds': 'avg_time', 'seq_score': 'avg_difficulty'}, inplace=True)

col_p1, col_p2 = st.columns(2)

with col_p1:
    st.subheader("AI Score vs Avg Complexity")
    chart_p1 = alt.Chart(user_agg).mark_circle(size=60).encode(
        x='ai_score:Q', y='complexity:Q', tooltip=['prolific_id', 'ai_score', 'complexity']
    ).properties(title="AI Score vs Complexity")
    st.altair_chart(chart_p1 + chart_p1.transform_regression('ai_score', 'complexity').mark_line(), use_container_width=True)

with col_p2:
    st.subheader("AI Score vs Avg Time")
    chart_p2 = alt.Chart(user_agg).mark_circle(size=60).encode(
        x='ai_score:Q', y='avg_time:Q', tooltip=['prolific_id', 'ai_score', 'avg_time']
    ).properties(title="AI Score vs Avg Time")
    st.altair_chart(chart_p2 + chart_p2.transform_regression('ai_score', 'avg_time').mark_line(), use_container_width=True)


# --- HYPOTHESIS 3: EFFICIENCY ILLUSION (DIFFICULTY) ---
st.header("H3: Efficiency Illusion (Difficulty)")
st.markdown("**Hypothesis:** Higher AI usage lowers perceived difficulty.")

# Stats
st.markdown(calculate_ttest(df, 'ai_used', 'seq_score'))

# Viz
base_h3 = alt.Chart(df).encode(x='ai_used:N', color='ai_used:N')
box_h3 = base_h3.mark_boxplot().encode(y='seq_score:Q')
err_h3 = base_h3.mark_errorbar(extent='ci').encode(y='seq_score:Q')

chart_h3 = (box_h3 + err_h3).properties(title="Perceived Difficulty (Mean + 95% CI)")
st.altair_chart(chart_h3, use_container_width=True)

# Raw Data
with st.expander("View Raw Data"):
    st.dataframe(df)
