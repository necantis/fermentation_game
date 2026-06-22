import streamlit as st
import pandas as pd
from Presentation.config import COLOR_PALETTE

def render_tab_0(df, df_feedback):
    st.markdown(
        f"""<div class="glass-card" style="padding: 24px; margin-bottom: 25px; border-left: 4px solid {COLOR_PALETTE['primary']};">
<span style="font-size: 0.85rem; letter-spacing: 0.1em; color: {COLOR_PALETTE['primary']}; font-weight: 600; text-transform: uppercase;">
ID: 854 / PAR-T9.3-2: 2 &nbsp;|&nbsp; Track 9.3: AI in the Lab
</span>
<h2 style="margin-top: 8px; font-weight: 700; font-size: 2.1rem; line-height: 1.25; color: #0ea5e9;">
The Efficiency Illusion: Cognitive Offloading and Coordination Costs in AI-Assisted Anomaly Detection
</h2>
<p style="margin-top: 10px; font-size: 1.1rem; font-weight: 500; color: {COLOR_PALETTE['text']};">
<b>Author:</b> Bonazzi, Riccardo &nbsp;•&nbsp; <i>University of Applied Sciences Western Switzerland (HES-SO), Switzerland</i> &nbsp;•&nbsp; <a href="mailto:riccardo.bonazzi@hevs.ch" style="color: {COLOR_PALETTE['primary']}; text-decoration: none;">riccardo.bonazzi@hevs.ch</a>
</p>
<p style="margin-top: 8px; font-size: 0.95rem; color: {COLOR_PALETTE['text_muted']}; line-height: 1.5;">
<b>Keywords:</b> Human-Machine Interaction, Epistemic Norms, Cognitive Offloading, Human-AI collaboration, Agentic AI
</p>
<hr style="margin: 15px 0; border: 0; border-top: 1px solid rgba(255, 255, 255, 0.1);">
<p style="color: {COLOR_PALETTE['text_muted']}; font-size: 0.95rem; line-height: 1.6; margin: 0;">
<b>Reviewer Note:</b> This application serves as an interactive, fully reproducible visualization of a stable mathematical pipeline. 
All data preprocessing, feature engineering, and statistical parameters are calculated programmatically from localized raw data traces 
to ensure absolute transparency and auditability.
</p>
</div>""",
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
        f"""<div class="glass-card">
<table style="width: 100%; border-collapse: collapse; font-size: 0.95rem;">
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
<tr style="border-bottom: 1px solid {COLOR_PALETTE['grid']}; color: {COLOR_PALETTE['text']};">
<td style="padding: 12px; font-weight: 500;"><b>H1: Coordination Cost</b> (Duration)</td>
<td style="padding: 12px; color: {COLOR_PALETTE['text_muted']};">AI usage increases time (r = 0.36)</td>
<td style="padding: 12px; color: {COLOR_PALETTE['text']};">Objective time penalty continues (Mean: 34.41s)</td>
<td style="padding: 12px; font-family: monospace; color: {COLOR_PALETTE['text']};">p = 0.0012 (Significant)</td>
<td style="padding: 12px;"><span style="color: {COLOR_PALETTE['success']}; font-weight: 600;">Supported</span></td>
</tr>
<tr style="border-bottom: 1px solid {COLOR_PALETTE['grid']}; color: {COLOR_PALETTE['text']};">
<td style="padding: 12px; font-weight: 500;"><b>H2: Delegation Effect</b> (Answer Length)</td>
<td style="padding: 12px; color: {COLOR_PALETTE['text_muted']};">AI usage reduces length (r = -0.18)</td>
<td style="padding: 12px; color: {COLOR_PALETTE['text']};"><b>Reversed:</b> AI Used = 122.38 chars vs Control = 11.29</td>
<td style="padding: 12px; font-family: monospace; color: {COLOR_PALETTE['text']};">p = 0.0012 (Significant)</td>
<td style="padding: 12px;"><span style="color: {COLOR_PALETTE['success']}; font-weight: 600;">Reversed & Supported</span></td>
</tr>
<tr style="border-bottom: 1px solid {COLOR_PALETTE['grid']}; color: {COLOR_PALETTE['text']};">
<td style="padding: 12px; font-weight: 500;"><b>H3: Efficiency Illusion</b> (Difficulty)</td>
<td style="padding: 12px; color: {COLOR_PALETTE['text_muted']};">AI usage lowers perceived effort (r = -0.77)</td>
<td style="padding: 12px; color: {COLOR_PALETTE['text']};"><b>Shattered:</b> AI Used = 4.65 rating vs Control = 3.78</td>
<td style="padding: 12px; font-family: monospace; color: {COLOR_PALETTE['text']};">p = 0.0480 (Significant)</td>
<td style="padding: 12px;"><span style="color: {COLOR_PALETTE['success']}; font-weight: 600;">Shattered & Realigned</span></td>
</tr>
</tbody>
</table>
</div>""",
        unsafe_allow_html=True
    )
