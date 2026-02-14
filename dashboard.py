import streamlit as st
import pandas as pd
import altair as alt
import scipy.stats as stats
import os

st.set_page_config(page_title="Fermentation Game Analytics", layout="wide")

st.title("Fermentation Game Analytics")
st.markdown("### Hypothesis Testing & Data Overview")

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

@st.cache_data
def load_data():
    data = None
    if os.path.exists(DATA_FILE):
        try:
            # Load with existing header, handle bad lines gracefully
            data = pd.read_csv(DATA_FILE, on_bad_lines='warn')
            
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
                # valid if explicit duration > 0, OR if inferred diff is reasonable (< 1 hour)
                # Note: Round 1 for old data will be 0 as it has no predecessor
                def get_valid_duration(row):
                    if row['round_duration_seconds'] > 0.1:
                        return row['round_duration_seconds']
                    if 0 < row['time_diff'] < 3600: # heuristic: < 1 hour
                        return row['time_diff']
                    return 0.0
                
                data['round_duration_seconds'] = data.apply(get_valid_duration, axis=1)

        except Exception as e:
            st.error(f"Error loading game data: {e}")
    
    feedback = None
    if os.path.exists(FEEDBACK_FILE):
        try:
             feedback = pd.read_csv(FEEDBACK_FILE, on_bad_lines='warn')
             
             # Repair Feedback Columns
             for col in FEEDBACK_LOG_COLS:
                 if col not in feedback.columns:
                     feedback[col] = 0 if 'seconds' in col else ""
                     
        except Exception as e:
            st.error(f"Error loading feedback data: {e}")
            
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
    
    return f"**T-Test Results**: t={t_stat:.2f}, p={p_val:.4f} -> {sig}"

# ... (Load Data remains same)

# --- HYPOTHESIS 1: COORDINATION COST (TIME) ---
st.header("H1: Coordination Cost (Time)")
st.markdown("**Hypothesis:** Higher AI usage increases task duration.")

# 1. Round Duration Analysis (Granular)
if 'round_duration_seconds' in df.columns and df['round_duration_seconds'].sum() > 0:
    st.subheader("Round Duration vs AI Usage")
    
    # Stats
    st.markdown(calculate_ttest(df, 'ai_used', 'round_duration_seconds'))

    # Viz: Boxplot + CI
    base = alt.Chart(df).encode(x='ai_used:N', color='ai_used:N')
    boxplot = base.mark_boxplot().encode(y='round_duration_seconds:Q')
    errorbars = base.mark_errorbar(extent='ci').encode(y='round_duration_seconds:Q')
    
    chart_h1 = (boxplot + errorbars).properties(title="Time per Round (Mean + 95% CI)")
    st.altair_chart(chart_h1, use_container_width=True)
    
    # NEW: Stacked Bar Chart for Time Breakdown
    st.subheader("Participant Time Breakdown")
    chart_stack = alt.Chart(df).mark_bar().encode(
        x='prolific_id:N',
        y='round_duration_seconds:Q',
        color='round:N',
        tooltip=['prolific_id', 'round', 'round_duration_seconds', 'ai_used']
    ).properties(title="Total Time Breakdown by Round per Participant")
    st.altair_chart(chart_stack, use_container_width=True)

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

# Viz
base_h2 = alt.Chart(df).encode(x='ai_used:N', color='ai_used:N')
box_h2 = base_h2.mark_boxplot().encode(y='text_len:Q')
err_h2 = base_h2.mark_errorbar(extent='ci').encode(y='text_len:Q')

chart_h2 = (box_h2 + err_h2).properties(title="Assessment Length (Mean + 95% CI)")
st.altair_chart(chart_h2, use_container_width=True)


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
