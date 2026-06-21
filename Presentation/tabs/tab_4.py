import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from Presentation.config import COLOR_PALETTE

def render_tab_4(df, df_feedback):
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 24px; margin-bottom: 25px; border-left: 4px solid {COLOR_PALETTE['success']};">
            <span style="font-size: 0.85rem; letter-spacing: 0.15em; color: {COLOR_PALETTE['success']}; font-weight: 600; text-transform: uppercase;">
                Phase 2: Cognitive Forcing Function Test
            </span>
            <h2 style="margin-top: 5px; font-weight: 700; font-size: 2.2rem;">
                The Second Iteration: Forcing Active Verification
            </h2>
            <p style="color: {COLOR_PALETTE['text_muted']}; font-size: 1.05rem; margin-top: 5px; max-width: 950px; line-height: 1.6;">
                The Phase 2 protocol introduces a <b>Cognitive Forcing Function (CFF)</b>: forcing participants to write out their own analysis 
                before they are allowed to see the AI's diagnostic advice. This shatters the baseline "Efficiency Illusion" and alters user behavior.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Framing for Persona A (Scholar)
    st.markdown("### 1. Methodology & Proof of Concept")
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid {COLOR_PALETTE['primary']}; margin-bottom: 25px;">
            <p style="margin: 0; line-height: 1.6; color: {COLOR_PALETTE['text']}; font-size: 0.95rem;">
                <b>Experimental Proof-of-Concept:</b> Rather than a definitive population-level claim, the Phase 2 test is framed as 
                an empirical proof-of-concept validating our <b>trace-mapping methodology</b>. 
                This Streamlit application demonstrates a reproducible data collection and analytical pipeline designed for 
                future, large-scale deployment across safety-critical enterprise environments.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Hypothesis Results Metrics Cards
    st.markdown("### 2. Hypotheses Outcomes & Statistical Significance")
    
    col_h1, col_h2, col_h3 = st.columns(3)
    
    with col_h1:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 4px solid {COLOR_PALETTE['no_ai']};">
                <span style="font-size: 0.75rem; letter-spacing: 0.1em; color: {COLOR_PALETTE['text_muted']}; font-weight: 600; text-transform: uppercase;">
                    H1: Coordination Time Penalty
                </span>
                <h3 style="font-size: 1.8rem; margin: 10px 0; color: {COLOR_PALETTE['no_ai']};">34.41s</h3>
                <p style="font-size: 0.9rem; line-height: 1.5; color: {COLOR_PALETTE['text']};">
                    Higher AI usage continues to carry an objective time penalty. The global average time per round settles at <b>34.41 seconds</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_h2:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 4px solid {COLOR_PALETTE['success']};">
                <span style="font-size: 0.75rem; letter-spacing: 0.1em; color: {COLOR_PALETTE['text_muted']}; font-weight: 600; text-transform: uppercase;">
                    H2: Delegation Effect Reversed
                </span>
                <h3 style="font-size: 1.8rem; margin: 10px 0; color: {COLOR_PALETTE['success']};">122.38 vs 11.29 Chars</h3>
                <p style="font-size: 0.9rem; line-height: 1.5; color: {COLOR_PALETTE['text']};">
                    AI Used = True yields significantly longer answers (<b>122.38 Chars</b> vs Control <b>11.29 Chars</b>; <i>p = 0.0012</i>). 
                    Complexity increases (<b>102.72</b> vs Control <b>26.75</b>; <i>p = 0.0011</i>).
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_h3:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 4px solid {COLOR_PALETTE['secondary']};">
                <span style="font-size: 0.75rem; letter-spacing: 0.1em; color: {COLOR_PALETTE['text_muted']}; font-weight: 600; text-transform: uppercase;">
                    H3: Efficiency Illusion Shattered
                </span>
                <h3 style="font-size: 1.8rem; margin: 10px 0; color: {COLOR_PALETTE['secondary']};">4.65 vs 3.78</h3>
                <p style="font-size: 0.9rem; line-height: 1.5; color: {COLOR_PALETTE['text']};">
                    Forcing human formulation prior to AI exposure shatters automation bias. AI users rate task difficulty significantly higher 
                    (<b>4.65</b> vs Control <b>3.78</b>; <i>p = 0.0480</i>).
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. Strategy Deep Dive: Copiers vs Improvers
    st.markdown("### 3. Strategy Deep Dive: Copiers vs. Improvers")
    st.markdown(
        f"By calculating the semantic similarity ratio of participant answers against the AI's output (Global Median Similarity: **0.2924**), "
        "we identify a clear divergence in collaboration strategies:"
    )
    
    col_str_1, col_str_2 = st.columns(2)
    
    with col_str_1:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 3px solid {COLOR_PALETTE['no_ai']};">
                <h4 style="color: {COLOR_PALETTE['no_ai']}; font-weight: 600;">Passive Copiers (High Similarity)</h4>
                <ul>
                    <li><b>Average Task Duration:</b> 135.00 seconds</li>
                    <li><b>Baseline Answer Length:</b> 46.88 characters</li>
                    <li><b>Behavioral Profile:</b> These users suffer from "Cognitive Surrender". They get caught in a prolonged, unproductive text-reconciliation loop trying to audit the AI's outputs, resulting in severe operational drag.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_str_2:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 3px solid {COLOR_PALETTE['success']};">
                <h4 style="color: {COLOR_PALETTE['success']}; font-weight: 600;">Active Improvers (Low Similarity)</h4>
                <ul>
                    <li><b>Average Task Duration:</b> 72.60 seconds</li>
                    <li><b>Baseline Answer Length:</b> 92.23 characters</li>
                    <li><b>Behavioral Profile:</b> By formulating their own ideas first, they write longer baseline answers and use the AI for cognitive augmentation. They skip the text-reconciliation loop and operate with high efficiency.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Financial Calculator Slider (Persona B)
    st.markdown("---")
    st.markdown("### 4. Financial Impact Module (Organizational Drag Calculator)")
    st.markdown(
        "To make these findings tangible for executives, the slider below translates the verification latency difference "
        "between <b>Copiers (135s)</b> and <b>Improvers (72.6s)</b> into direct operational labor drag."
    )

    # Sliders for labor rate and incident volume
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        labor_rate = st.slider("Engineering Labor Rate ($/hour)", min_value=30.0, max_value=250.0, value=120.0, step=5.0)
    with col_sl2:
        annual_tickets = st.slider("Annual Bioreactor Troubleshooting Incidents", min_value=100, max_value=10000, value=2500, step=100)

    # Calculate labor costs
    t_copier = 135.00
    t_improver = 72.60
    
    annual_cost_copier = (t_copier / 3600.0) * labor_rate * annual_tickets
    annual_cost_improver = (t_improver / 3600.0) * labor_rate * annual_tickets
    cost_drag_delta = annual_cost_copier - annual_cost_improver

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(
            label="Copier Profile Labor Cost",
            value=f"${annual_cost_copier:,.2f}",
            delta=f"Avg {t_copier:.1f}s / incident",
            delta_color="inverse"
        )
    with col_m2:
        st.metric(
            label="Improver Profile Labor Cost",
            value=f"${annual_cost_improver:,.2f}",
            delta=f"Avg {t_improver:.1f}s / incident",
            delta_color="normal"
        )
    with col_m3:
        st.metric(
            label="Financial Drag (Operational Cost Delta)",
            value=f"${cost_drag_delta:,.2f}",
            delta="Loss incurred by passive Copier profiles",
            delta_color="off"
        )

    st.markdown(
        f"""
        <div class="glass-card">
            <h4>Executive Takeaway</h4>
            <p style="margin: 0; line-height: 1.6; color: {COLOR_PALETTE['text_muted']};">
                Implementing the "write-first" protocol shatters the "Efficiency Illusion" and creates a clear subset of "Improvers" who skip the text-reconciliation loop. 
                This design choice reduces task duration from 135s to 72.6s, saving <b>${cost_drag_delta:,.2f}</b> annually in direct labor costs, while generating higher-quality analytical audits.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
