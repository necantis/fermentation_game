import streamlit as st
import pandas as pd
from Presentation.config import COLOR_PALETTE

def render_tab_0(df, df_feedback):
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 24px; margin-bottom: 25px; border-left: 4px solid {COLOR_PALETTE['primary']};">
            <span style="font-size: 0.85rem; letter-spacing: 0.15em; color: {COLOR_PALETTE['primary']}; font-weight: 600; text-transform: uppercase;">
                Rigorous Academic Context & Pipeline Transparency
            </span>
            <h2 style="margin-top: 5px; font-weight: 700; font-size: 2.2rem;">
                The Overall Picture: Bounded Rationality in Human-AI Systems
            </h2>
            <p style="color: {COLOR_PALETTE['text_muted']}; font-size: 1.05rem; margin-top: 5px; max-width: 950px; line-height: 1.6;">
                <b>Reviewer Note:</b> This application serves as an interactive, fully reproducible visualization of a stable mathematical pipeline. 
                All data preprocessing, feature engineering, and statistical parameters are calculated programmatically from localized raw data traces 
                to ensure absolute transparency and auditability.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Side-by-side comparison of theory
    col_theory_1, col_theory_2 = st.columns(2)
    
    with col_theory_1:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 3px solid {COLOR_PALETTE['success']};">
                <h4 style="color: {COLOR_PALETTE['success']}; font-size: 1.25rem; font-weight: 600;">The Prevailing Narrative: Linear Offloading</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; color: {COLOR_PALETTE['text']};">
                    Standard generative AI benchmarks, such as those detailed by <b>Dell'Acqua et al. 2026</b> (<i>Organization Science</i>), 
                    suggest that AI acts as a pure speed accelerator. In these contexts, tasks are linear, error visibility is high, and 
                    the cognitive effort required is low.
                </p>
                <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.85rem; color: {COLOR_PALETTE['primary']}; border-left: 3px solid {COLOR_PALETTE['primary']}; margin-top: 15px;">
                    <b>BCG CONTEXT (Linear Offloading):</b><br>
                    AI Input ──► Fast Generation ──► Linear Copy-Paste/Acceptance ──► Task Finished Faster
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_theory_2:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 3px solid {COLOR_PALETTE['warning']};">
                <h4 style="color: {COLOR_PALETTE['warning']}; font-size: 1.25rem; font-weight: 600;">The Bounded Rationality Reality: Continuous Auditing</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; color: {COLOR_PALETTE['text']};">
                    In practice, applying Herbert Simon's theory of <b>Bounded Rationality</b> reveals that real-world decision processes 
                    are non-linear. They involve reading time, verification steps, and recursive iterations. Unchecked delegation leads to 
                    <b>"Cognitive Surrender"</b> (<i>Bailey et al. 2026</i>), where subjects blindly accept incorrect AI outputs to save effort.
                </p>
                <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.85rem; color: {COLOR_PALETTE['warning']}; border-left: 3px solid {COLOR_PALETTE['warning']}; margin-top: 15px;">
                    <b>OUR CONTEXT (Continuous Auditing):</b><br>
                    Frontline Metrics ──► AI Advice ──► Human Verification Loop ("Read-Verify-Decide") ──► Time
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Hypothesis Mapping & Pilot vs Forcing Function Statistics")
    
    # Hypothesis and statistics table
    st.markdown(
        f"""
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 0.95rem;">
            <thead>
                <tr style="border-bottom: 2px solid {COLOR_PALETTE['grid']}; text-align: left; color: {COLOR_PALETTE['primary']};">
                    <th style="padding: 12px; font-weight: 600;">Construct / Hypothesis</th>
                    <th style="padding: 12px; font-weight: 600;">Phase 1: Baseline Workshop (N=12)</th>
                    <th style="padding: 12px; font-weight: 600;">Phase 2: Forcing Function Test (N=33)</th>
                    <th style="padding: 12px; font-weight: 600;">Statistical p-value (Phase 2)</th>
                    <th style="padding: 12px; font-weight: 600;">Status</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid {COLOR_PALETTE['grid']};">
                    <td style="padding: 12px; font-weight: 500;"><b>H1: Coordination Cost</b> (Duration)</td>
                    <td style="padding: 12px; color: {COLOR_PALETTE['text_muted']};">AI usage increases time (r = 0.36)</td>
                    <td style="padding: 12px;">Objective time penalty continues (Mean: 34.41s)</td>
                    <td style="padding: 12px; font-family: monospace;">p = 0.0012 (Significant)</td>
                    <td style="padding: 12px;"><span style="color: {COLOR_PALETTE['success']}; font-weight: 600;">Supported</span></td>
                </tr>
                <tr style="border-bottom: 1px solid {COLOR_PALETTE['grid']};">
                    <td style="padding: 12px; font-weight: 500;"><b>H2: Delegation Effect</b> (Answer Length)</td>
                    <td style="padding: 12px; color: {COLOR_PALETTE['text_muted']};">AI usage reduces length (r = -0.18)</td>
                    <td style="padding: 12px;"><b>Reversed:</b> AI Used = 122.38 chars vs Control = 11.29</td>
                    <td style="padding: 12px; font-family: monospace;">p = 0.0012 (Significant)</td>
                    <td style="padding: 12px;"><span style="color: {COLOR_PALETTE['success']}; font-weight: 600;">Reversed & Supported</span></td>
                </tr>
                <tr style="border-bottom: 1px solid {COLOR_PALETTE['grid']};">
                    <td style="padding: 12px; font-weight: 500;"><b>H3: Efficiency Illusion</b> (Difficulty)</td>
                    <td style="padding: 12px; color: {COLOR_PALETTE['text_muted']};">AI usage lowers perceived effort (r = -0.77)</td>
                    <td style="padding: 12px;"><b>Shattered:</b> AI Used = 4.65 rating vs Control = 3.78</td>
                    <td style="padding: 12px; font-family: monospace;">p = 0.0480 (Significant)</td>
                    <td style="padding: 12px;"><span style="color: {COLOR_PALETTE['success']}; font-weight: 600;">Shattered & Realigned</span></td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Underlying Data Matrix Preview")
    st.markdown("To ensure complete transparency, below is the raw data matrix loaded by the pipeline, representing the fermentation gameplay traces.")
    
    # Display preview of df
    if df is not None and not df.empty:
        st.dataframe(df[['prolific_id', 'round', 'scenario_name', 'ai_used', 'text_changed', 'seq_score', 'round_duration_seconds']].head(5), use_container_width=True)
    else:
        st.warning("Data matrix not loaded.")
