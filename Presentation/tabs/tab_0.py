import streamlit as st
from Presentation.config import COLOR_PALETTE

def render_tab_0(df, df_feedback):
    st.markdown(
        f"""
        <div class="glass-card" style="text-align: center; padding: 48px 24px; margin-bottom: 30px;">
            <p style="font-size: 1.1rem; color: {COLOR_PALETTE['primary']}; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 600;">
                Scientific Presentation Dashboard
            </p>
            <h1 style="font-size: 3rem; margin-top: 10px; margin-bottom: 20px; font-weight: 700; line-height: 1.2;">
                Cognitive Friction & Copier Dynamics
            </h1>
            <p style="font-size: 1.5rem; color: {COLOR_PALETTE['text']}; font-weight: 300; margin-bottom: 40px; max-width: 800px; margin-left: auto; margin-right: auto;">
                Analyzing human-AI collaboration strategies and coordination costs in fermentation troubleshooting games.
            </p>
            <div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; margin-top: 20px;">
                <div>
                    <p style="margin: 0; color: {COLOR_PALETTE['text_muted']}; font-size: 0.9rem;">CONFERENCE</p>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">Bio-Process Engineering 2026</p>
                </div>
                <div style="width: 1px; background-color: {COLOR_PALETTE['grid']};"></div>
                <div>
                    <p style="margin: 0; color: {COLOR_PALETTE['text_muted']}; font-size: 0.9rem;">RESEARCH FIELD</p>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">Human-AI Interaction / Decision Support</p>
                </div>
                <div style="width: 1px; background-color: {COLOR_PALETTE['grid']};"></div>
                <div>
                    <p style="margin: 0; color: {COLOR_PALETTE['text_muted']}; font-size: 0.9rem;">DATASET SIZE</p>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">{df['prolific_id'].nunique()} Unique Subjects</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%;">
                <h3>Abstract & Context</h3>
                <p style="color: {COLOR_PALETTE['text']}; line-height: 1.6;">
                    This research investigates how decision-support artificial intelligence impacts human troubleshooting efficiency and cognitive burden inside a simulated <b>Fermentation Bioreactor Troubleshooting Game</b>.
                </p>
                <p style="color: {COLOR_PALETTE['text']}; line-height: 1.6;">
                    Subjects are tasked with correcting faulty fermentation variables (e.g. dissolved oxygen, temperature, pressure). Half of the subjects have access to an AI assistant that suggests remedies and provides auto-generated diagnostic summaries. We test three primary hypotheses concerning time costs (H1), delegation effects (H2), and the difficulty illusion (H3).
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%;">
                <h3>Study Methodology</h3>
                <div class="metric-container">
                    <span style="font-weight: bold; color: {COLOR_PALETTE['primary']};">Experimental Design:</span>
                    <p style="margin: 4px 0 0 0; color: {COLOR_PALETTE['text']};">Between-subject comparison tracking AI logs, text-input modifications, timing, and player assessment scores.</p>
                </div>
                <div class="metric-container" style="border-left-color: {COLOR_PALETTE['secondary']};">
                    <span style="font-weight: bold; color: {COLOR_PALETTE['secondary']};">Key Indicators:</span>
                    <ul style="margin: 4px 0 0 0; padding-left: 20px; color: {COLOR_PALETTE['text']};">
                        <li>AI Similarity: Lexical distance between participant and AI input</li>
                        <li>Round Duration: Duration (seconds) recorded for each scenario</li>
                        <li>Text Complexity: Information density metrics of players' diagnoses</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
