import streamlit as st

DEFAULT_STATE = {
    # Navigation state
    "active_tab": 0,
    
    # Filter states
    "selected_participant": "All",
    "exclude_outliers": False,
    "outlier_threshold_seconds": 600.0,
    
    # Visual states
    "theme_mode": "dark",
    "chart_type": "Plotly",
    
    # Hypothesis specific states
    "h1_sort_order": "Duration (Descending)",
    "h2_metric": "complexity",
    
    # Tab 5 Simulator states
    "sim_ai_adoption": 60.0,     # Percentage of rounds where AI is used
    "sim_user_skill": 5.0,        # Base user skill level (1-10)
    "sim_ai_accuracy": 8.0,      # AI suggestion accuracy (1-10)
    "sim_complexity": 6.0,       # Task complexity (1-10)
}

def init_presentation_state():
    """Initializes the central state dictionary under st.session_state if not present."""
    if "presentation" not in st.session_state:
        st.session_state.presentation = DEFAULT_STATE.copy()

def get_state(key, default=None):
    """Retrieves a state value by key, returning the default if not present."""
    init_presentation_state()
    return st.session_state.presentation.get(key, default)

def set_state(key, value):
    """Sets a state value by key."""
    init_presentation_state()
    st.session_state.presentation[key] = value

def reset_state():
    """Resets the state to defaults."""
    st.session_state.presentation = DEFAULT_STATE.copy()
