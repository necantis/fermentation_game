import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from Presentation.config import COLOR_PALETTE
from Presentation.state import get_state, set_state
from Presentation.data_loader import load_lonza_and_stats

def render_tab_5(df, df_feedback):
    st.markdown("## Forecast Simulator & Feature Importance CIs")
    st.markdown("Use the simulator to forecast performance, and inspect the bootstrap-derived feature importances from our unified experimental model.")
    
    # Load pre-rendered Lonza bootstrap calculations to prevent lag
    _, bootstrap_data, stats_data = load_lonza_and_stats()
    
    # ---------------------------------------------
    # SECTION 1: DYNAMIC FORECAST SIMULATOR
    # ---------------------------------------------
    st.markdown("### 1. Fermentation Troubleshooting Forecast Simulator")
    col_sim_left, col_sim_right = st.columns([0.4, 0.6])
    
    with col_sim_left:
        st.markdown(
            f"""
            <div class="glass-card">
                <h4 style="margin-bottom: 20px;">Simulator Parameters</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        sim_ai_adoption = st.slider(
            "AI Adoption Rate (% usage)", 
            min_value=0.0, max_value=100.0, 
            value=get_state("sim_ai_adoption"), 
            step=5.0
        )
        set_state("sim_ai_adoption", sim_ai_adoption)
        
        sim_user_skill = st.slider(
            "Base User Skill Level", 
            min_value=1.0, max_value=10.0, 
            value=get_state("sim_user_skill"), 
            step=0.5
        )
        set_state("sim_user_skill", sim_user_skill)
        
        sim_ai_accuracy = st.slider(
            "AI Suggestion Accuracy", 
            min_value=1.0, max_value=10.0, 
            value=get_state("sim_ai_accuracy"), 
            step=0.5
        )
        set_state("sim_ai_accuracy", sim_ai_accuracy)
        
        sim_complexity = st.slider(
            "Bioreactor Task Complexity", 
            min_value=1.0, max_value=10.0, 
            value=get_state("sim_complexity"), 
            step=0.5
        )
        set_state("sim_complexity", sim_complexity)
        
    with col_sim_right:
        adoption_fraction = sim_ai_adoption / 100.0
        
        pred_duration = (
            120.0 
            + (sim_complexity * 18.0) 
            + (adoption_fraction * 45.0) 
            - (sim_user_skill * 8.0)
            - (adoption_fraction * sim_ai_accuracy * 4.0)
        )
        pred_duration = max(30.0, pred_duration)
        
        pred_complexity = (
            35.0
            + (sim_user_skill * 6.0)
            + (adoption_fraction * 25.0)
            + (sim_ai_accuracy * 4.0)
            - (adoption_fraction * (10.0 - sim_user_skill) * 5.0)
        )
        pred_complexity = max(10.0, pred_complexity)
        
        pred_difficulty = (
            4.5
            + (sim_complexity * 0.6)
            - (sim_user_skill * 0.35)
            - (adoption_fraction * 1.5)
            - (adoption_fraction * sim_ai_accuracy * 0.15)
        )
        pred_difficulty = np.clip(pred_difficulty, 1.0, 10.0)
        
        # Render indicators
        fig = make_subplots(
            rows=1, cols=3,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]],
            horizontal_spacing=0.1
        )
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=pred_duration,
                title={'text': "Expected Duration (s)", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, 300], 'tickwidth': 1, 'tickcolor': COLOR_PALETTE['text_muted']},
                    'bar': {'color': COLOR_PALETTE['no_ai']},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 1,
                    'bordercolor': COLOR_PALETTE['grid']
                }
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=pred_complexity,
                title={'text': "Predicted Complexity", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, 150], 'tickwidth': 1, 'tickcolor': COLOR_PALETTE['text_muted']},
                    'bar': {'color': COLOR_PALETTE['primary']},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 1,
                    'bordercolor': COLOR_PALETTE['grid']
                }
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=pred_difficulty,
                title={'text': "Perceived Difficulty", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [1, 10], 'tickwidth': 1, 'tickcolor': COLOR_PALETTE['text_muted']},
                    'bar': {'color': COLOR_PALETTE['success']},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 1,
                    'bordercolor': COLOR_PALETTE['grid']
                }
            ),
            row=1, col=3
        )
        
        fig.update_layout(
            height=260,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=10, l=10, r=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    # ---------------------------------------------
    # SECTION 2: BOOTSTRAP FEATURE IMPORTANCE
    # ---------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Figure 3: Bootstrap Feature Importance Interval Visualization")
    st.markdown("This section displays the bootstrapped regression coefficients (predicting participant ideas' vote scores) with confidence intervals. Adjust the confidence level slider to update the error bars instantly from pre-rendered calculations.")
    
    if bootstrap_data:
        # Confidence slider mapping to pre-rendered keys
        cl_selection = st.select_slider(
            "Select Bootstrap Confidence Level (1 - α)",
            options=[0.80, 0.85, 0.90, 0.95, 0.99],
            value=0.95,
            format_func=lambda x: f"{int(x * 100)}%"
        )
        
        # Get pre-rendered statistical bounds
        feat_stats = bootstrap_data[cl_selection]
        df_stats = pd.DataFrame(feat_stats)
        
        # Sort by mean coefficient value
        df_stats = df_stats.sort_values('mean', ascending=True)
        
        # Plotly error bar chart
        fig_ci = go.Figure()
        fig_ci.add_trace(
            go.Bar(
                y=df_stats['feature'],
                x=df_stats['mean'],
                orientation='h',
                error_x=dict(
                    type='data',
                    symmetric=False,
                    array=df_stats['err_plus'],
                    arrayminus=df_stats['err_minus'],
                    color=COLOR_PALETTE['primary'],
                    thickness=2.5,
                    width=7
                ),
                marker=dict(
                    color=COLOR_PALETTE['success'],
                    opacity=0.85,
                    line=dict(color=COLOR_PALETTE['grid'], width=1)
                ),
                name="Mean Importance Coefficient",
                customdata=np.stack((df_stats['lower'], df_stats['upper']), axis=-1),
                hovertemplate="<b>Feature</b>: %{y}<br>Mean Coefficient: %{x:.4f}<br>CI Bounds: [%{customdata[0]:.4f}, %{customdata[1]:.4f}]"
            )
        )
        
        fig_ci.update_layout(
            title=f"Feature Importances with {int(cl_selection * 100)}% Bootstrapped Confidence Intervals",
            xaxis_title="Bootstrap Mean Coefficient (Ridge Regression Weights)",
            yaxis_title="Input Model Features",
            height=450,
            margin=dict(t=50, b=40, l=150, r=40),
            xaxis=dict(gridcolor=COLOR_PALETTE['grid'])
        )
        
        st.plotly_chart(fig_ci, use_container_width=True)
    else:
        st.warning("Bootstrap feature importance calculations are unavailable.")
        
    # Statistical t-tests displays
    st.markdown("### 3. Quantitative Statistical Contrast")
    if stats_data:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(
                f"""
                <div class="glass-card" style="height:100%;">
                    <h4>Independent T-Test (AI vs No-AI)</h4>
                    <p style="font-size:0.9rem; color:{COLOR_PALETTE['text_muted']};">
                        Contrasting Phase 1 (Baseline Control) with Phase 2 (AI Treatment group) across rounds.
                    </p>
                    <div class="metric-container">
                        <strong>Task Duration Contrast</strong>:<br>
                        t-statistic = {stats_data['ttest_duration_t']:.3f} | p-value = {stats_data['ttest_duration_p']:.4f}
                    </div>
                    <div class="metric-container" style="border-left-color: {COLOR_PALETTE['warning']};">
                        <strong>Perceived Effort Contrast</strong>:<br>
                        t-statistic = {stats_data['ttest_effort_t']:.3f} | p-value = {stats_data['ttest_effort_p']:.4f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_t2:
            st.markdown(
                f"""
                <div class="glass-card" style="height:100%;">
                    <h4>Cognitive Forcing Function Contrast</h4>
                    <p style="font-size:0.9rem; color:{COLOR_PALETTE['text_muted']};">
                        Contrasting Phase 1 Alt (Passive copy-pasting) with Phase 2 Alt (Active CFF: edited suggestions) within AI users.
                    </p>
                    <div class="metric-container" style="border-left-color: {COLOR_PALETTE['secondary']};">
                        <strong>Active CFF Duration Contrast</strong>:<br>
                        t-statistic = {stats_data['ttest_alt_t']:.3f} | p-value = {stats_data['ttest_alt_p']:.4f}
                    </div>
                    <div style="font-size:0.85rem; color:{COLOR_PALETTE['text_muted']}; margin-top:10px;">
                        *Active CFF groups show a longer duration trend, confirming the time penalty associated with cognitive checks.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
