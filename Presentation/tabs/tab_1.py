import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from Presentation.data_loader import calculate_ttest_summary, load_lonza_and_stats
from Presentation.config import COLOR_PALETTE

def render_tab_1(df, df_feedback):
    st.markdown("## H1: Coordination Cost (Task Duration) & Dual-Axis Cost Profile")
    st.markdown("**Hypothesis**: Accessing and interacting with the AI increases the duration of a round due to reading and synthesis overhead.")
    
    # Calculate stats
    stats_res = calculate_ttest_summary(df, 'ai_used', 'round_duration_seconds', group1_val=True, group2_val=False)
    
    # Load Lonza data stats to get user_agg
    _, _, stats_data = load_lonza_and_stats()
    user_agg = stats_data.get("user_agg")
    
    # Render statistical summary card
    sig_class = "badge-sig" if stats_res["significant"] else "badge-non-sig"
    sig_text = "SIGNIFICANT" if stats_res["significant"] else "NOT SIGNIFICANT"
    
    st.markdown(
        f"""
        <div class="glass-card">
            <h3>Hypothesis Testing Summary</h3>
            <div style="display: flex; gap: 30px; align-items: center; flex-wrap: wrap;">
                <div>
                    <span class="stats-badge {sig_class}">{sig_text}</span>
                    <span style="font-size: 1.1rem; font-weight: 500;">{stats_res['message']}</span>
                </div>
                <div style="width: 1px; background-color: {COLOR_PALETTE['grid']}; height: 30px;"></div>
                <div>
                    <p style="margin:0; color:{COLOR_PALETTE['text_muted']}; font-size:0.85rem;">AVG ROUND TIME (AI USED)</p>
                    <p style="margin:0; font-size:1.4rem; font-weight:700; color:{COLOR_PALETTE['primary']};">{stats_res['g1_mean']:.2f} seconds</p>
                </div>
                <div style="width: 1px; background-color: {COLOR_PALETTE['grid']}; height: 30px;"></div>
                <div>
                    <p style="margin:0; color:{COLOR_PALETTE['text_muted']}; font-size:0.85rem;">AVG ROUND TIME (NO AI)</p>
                    <p style="margin:0; font-size:1.4rem; font-weight:700; color:{COLOR_PALETTE['no_ai']};">{stats_res['g2_mean']:.2f} seconds</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Plotly subplots for wide rendering
    round_avg = df.groupby(['round', 'ai_used'])['round_duration_seconds'].mean().reset_index()
    round_avg['AI State'] = round_avg['ai_used'].map({True: 'AI Used', False: 'No AI'})
    
    user_agg_sorted = df.groupby('prolific_id').agg({
        'ai_used': 'mean', # AI Score
        'round_duration_seconds': 'sum' # Cumulative Duration
    }).reset_index().sort_values('round_duration_seconds', ascending=False)
    
    # Create multi-variate subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Average Duration per Round", "Total Session Duration by Subject"),
        column_widths=[0.5, 0.5],
        horizontal_spacing=0.1
    )
    
    for ai_state, color in [('No AI', COLOR_PALETTE['no_ai']), ('AI Used', COLOR_PALETTE['ai'])]:
        sub_data = round_avg[round_avg['AI State'] == ai_state]
        fig.add_trace(
            go.Scatter(
                x=sub_data['round'],
                y=sub_data['round_duration_seconds'],
                mode='lines+markers',
                name=ai_state,
                line=dict(color=color, width=3),
                marker=dict(size=8),
                hovertemplate="Round %{x}<br>Avg Time: %{y:.1f}s<br>" + ai_state
            ),
            row=1, col=1
        )
        
    fig.add_trace(
        go.Bar(
            x=user_agg_sorted['prolific_id'],
            y=user_agg_sorted['round_duration_seconds'],
            marker=dict(
                color=user_agg_sorted['ai_used'],
                colorscale='Blues',
                colorbar=dict(
                    title="AI Score",
                    thickness=15,
                    x=1.02
                ),
                line=dict(color=COLOR_PALETTE['grid'], width=0.5)
            ),
            name="Cumulative Duration",
            hovertemplate="Subject: %{x}<br>Total Time: %{y:.1f}s<br>AI Usage: %{marker.color:.1%}"
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Game Round Number", tickmode='linear', row=1, col=1)
    fig.update_yaxes(title_text="Avg Duration (seconds)", row=1, col=1)
    fig.update_xaxes(title_text="Subjects (Sorted by Duration)", showticklabels=False, row=1, col=2)
    fig.update_yaxes(title_text="Cumulative Session Duration (s)", row=1, col=2)
    
    fig.update_layout(
        height=400,
        showlegend=True,
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ---------------------------------------------
    # FIGURE 1: DUAL-AXIS SCATTER PLOT
    # ---------------------------------------------
    st.markdown("### Figure 1: AI Usage versus Task Duration & Perceived Effort (Dual-Axis Profile)")
    st.markdown("This plot maps each participant's AI usage score (x-axis) against both their average task duration (left axis, blue) and perceived effort (right axis, orange).")
    
    if user_agg is not None and not user_agg.empty:
        # Create a dual-axis scatter plot using graph objects
        fig_dual = go.Figure()
        
        # Trace for task duration (y-axis 1)
        fig_dual.add_trace(
            go.Scatter(
                x=user_agg['ai_used'],
                y=user_agg['round_duration_seconds'],
                mode='markers+text',
                text=[f"P{int(pid)}" for pid in user_agg['prolific_id']],
                textposition="top center",
                name="Avg Duration (s)",
                marker=dict(color=COLOR_PALETTE['primary'], size=10, symbol='circle'),
                yaxis="y1",
                hovertemplate="AI Usage: %{x:.1%}<br>Avg Time: %{y:.1f}s"
            )
        )
        
        # Trace for perceived effort (y-axis 2)
        fig_dual.add_trace(
            go.Scatter(
                x=user_agg['ai_used'],
                y=user_agg['seq_score'],
                mode='markers+text',
                text=[f"P{int(pid)}" for pid in user_agg['prolific_id']],
                textposition="bottom center",
                name="Perceived Effort",
                marker=dict(color=COLOR_PALETTE['warning'], size=10, symbol='diamond'),
                yaxis="y2",
                hovertemplate="AI Usage: %{x:.1%}<br>Perceived Effort: %{y:.2f}"
            )
        )
        
        # Fit trend lines if possible
        if len(user_agg) > 1:
            # Duration trend
            slope_dur, intercept_dur = np.polyfit(user_agg['ai_used'], user_agg['round_duration_seconds'], 1)
            x_line = np.linspace(user_agg['ai_used'].min(), user_agg['ai_used'].max(), 50)
            fig_dual.add_trace(
                go.Scatter(
                    x=x_line,
                    y=slope_dur * x_line + intercept_dur,
                    mode='lines',
                    line=dict(color=COLOR_PALETTE['primary'], width=1.5, dash='dash'),
                    name="Duration Trend",
                    yaxis="y1",
                    hoverinfo='skip'
                )
            )
            
            # Effort trend
            slope_eff, intercept_eff = np.polyfit(user_agg['ai_used'], user_agg['seq_score'], 1)
            fig_dual.add_trace(
                go.Scatter(
                    x=x_line,
                    y=slope_eff * x_line + intercept_eff,
                    mode='lines',
                    line=dict(color=COLOR_PALETTE['warning'], width=1.5, dash='dot'),
                    name="Effort Trend",
                    yaxis="y2",
                    hoverinfo='skip'
                )
            )
            
        fig_dual.update_layout(
            height=450,
            xaxis=dict(
                title="AI Usage Score (% of rounds AI used)",
                tickformat=".0%",
                gridcolor=COLOR_PALETTE['grid']
            ),
            yaxis1=dict(
                title=dict(text="Avg Task Duration (seconds)", font=dict(color=COLOR_PALETTE['primary'])),
                tickfont=dict(color=COLOR_PALETTE['primary']),
                gridcolor=COLOR_PALETTE['grid']
            ),
            yaxis2=dict(
                title=dict(text="Perceived Effort (Rating scale 1-10)", font=dict(color=COLOR_PALETTE['warning'])),
                tickfont=dict(color=COLOR_PALETTE['warning']),
                overlaying="y",
                side="right"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=50, b=40, l=40, r=40)
        )
        
        st.plotly_chart(fig_dual, use_container_width=True)
    else:
        st.warning("Insufficient data to build dual-axis correlation profile.")
        
    st.markdown(
        f"""
        <div class="glass-card">
            <h4>H1 Cost-Effort Insight</h4>
            <ul>
                <li>The dual-axis plot visualizes the core discrepancy of the <b>Efficiency Illusion</b>: as AI usage increases, task duration trends upward (due to cognitive coordination overhead), whereas perceived effort scales downward (due to the subjective ease of delegating tasks).</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
