import streamlit as st
import os
import sys

# Add parent directory to sys.path to allow correct package resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import configurations, state management, data loader
from Presentation.config import PAGE_TITLE, LAYOUT, INITIAL_SIDEBAR_STATE, setup_plotly_theme, inject_custom_css
from Presentation.state import init_presentation_state, get_state, set_state
from Presentation.data_loader import load_and_preprocess_data

# Import tab modules
from Presentation.tabs import tab_0, tab_1, tab_2, tab_3, tab_4, tab_5

# Initialize Streamlit Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# Apply Scientific Presentation custom theme styles
inject_custom_css()
setup_plotly_theme()

# Initialize the central state dictionary
init_presentation_state()

# Load gameplay and feedback data using localized cache
df, df_feedback = load_and_preprocess_data()

# Check for empty data
if df is None or df.empty:
    st.warning("⚠️ Localized data files not found or empty. Please run gameplay simulations first to log data.")
    st.stop()

# Presentation Header (Scientific Conference style)
st.markdown(
    """<div style="margin-bottom: 25px;">
<span style="font-size: 0.85rem; letter-spacing: 0.1em; color: #38bdf8; text-transform: uppercase; font-weight: 500;">
ID: 854 / PAR-T9.3-2: 2 | Track 9.3: "AI in the Lab: Transformations in R&D and the Practice of Science"
</span>
<hr style="margin: 8px 0 15px 0; border: 0; border-top: 1px solid rgba(255, 255, 255, 0.1);">
</div>""",
    unsafe_allow_html=True
)

# Generate 6 clean tabs numbered 01 through 06
tabs = st.tabs([
    "01. The Overall Picture",
    "02. The Experiment (Game)",
    "03. The Efficiency Illusion (Data)",
    "04. Feedback & Actions",
    "05. The Second Iteration (Results)",
    "06. Discussion & Conclusions"
])

# Map active tab changes to the central state dictionary
for idx, tab_el in enumerate(tabs):
    with tab_el:
        if idx == 0:
            tab_0.render_tab_0(df, df_feedback)
        elif idx == 1:
            tab_1.render_tab_1(df, df_feedback)
        elif idx == 2:
            tab_2.render_tab_2(df, df_feedback)
        elif idx == 3:
            tab_3.render_tab_3(df, df_feedback)
        elif idx == 4:
            tab_4.render_tab_4(df, df_feedback)
        elif idx == 5:
            tab_5.render_tab_5(df, df_feedback)

# Footer info
st.markdown(
    """
    <div style="margin-top: 40px; text-align: center; font-size: 0.8rem; color: #94a3b8; padding: 20px 0; border-top: 1px solid rgba(255, 255, 255, 0.05);">
        Bio-Process Engineering & Scientific Visualization Suite • Antigravity Orchestrator 2026
    </div>
    """,
    unsafe_allow_html=True
)
