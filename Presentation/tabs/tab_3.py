import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from Presentation.data_loader import calculate_ttest_summary
from Presentation.config import COLOR_PALETTE

def render_tab_3(df, df_feedback):
    st.markdown("## H3: Efficiency Illusion (Perceived Difficulty)")
    st.markdown("**Hypothesis**: Accessing the AI creates an illusion of task efficiency, lowering perceived difficulty even when actual performance (time, steps) is unchanged or degraded.")
    
    # Calculate stats
    stats_diff = calculate_ttest_summary(df, 'ai_used', 'seq_score', group1_val=True, group2_val=False)
    
    sig_class = "badge-sig" if stats_diff["significant"] else "badge-non-sig"
    sig_text = "SIGNIFICANT" if stats_diff["significant"] else "NOT SIGNIFICANT"
    
    st.markdown(
        f"""
        <div class="glass-card">
            <h3>Difficulty Hypothesis Test Result</h3>
            <div style="display: flex; gap: 30px; align-items: center; flex-wrap: wrap;">
                <div>
                    <span class="stats-badge {sig_class}">{sig_text}</span>
                    <span style="font-size: 1.1rem; font-weight: 500;">{stats_diff['message']}</span>
                </div>
                <div style="width: 1px; background-color: {COLOR_PALETTE['grid']}; height: 30px;"></div>
                <div>
                    <p style="margin:0; color:{COLOR_PALETTE['text_muted']}; font-size:0.85rem;">AVG PERCEIVED DIFFICULTY (AI USED)</p>
                    <p style="margin:0; font-size:1.4rem; font-weight:700; color:{COLOR_PALETTE['primary']};">{stats_diff['g1_mean']:.2f}</p>
                </div>
                <div style="width: 1px; background-color: {COLOR_PALETTE['grid']}; height: 30px;"></div>
                <div>
                    <p style="margin:0; color:{COLOR_PALETTE['text_muted']}; font-size:0.85rem;">AVG PERCEIVED DIFFICULTY (NO AI)</p>
                    <p style="margin:0; font-size:1.4rem; font-weight:700; color:{COLOR_PALETTE['no_ai']};">{stats_diff['g2_mean']:.2f}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Prepare User Aggregations for scatter plot
    user_agg = df.groupby('prolific_id').agg({
        'ai_used': 'mean', # AI Score
        'seq_score': 'mean', # Average Difficulty
        'round_duration_seconds': 'mean' # Average time
    }).reset_index()
    user_agg.rename(columns={'ai_used': 'ai_score', 'seq_score': 'avg_difficulty'}, inplace=True)
    
    # Multi-variate subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Perceived Difficulty Distribution", "Subject AI Usage vs Average Difficulty"),
        column_widths=[0.4, 0.6],
        horizontal_spacing=0.1
    )
    
    # 1. Boxplot + Mean marker
    df_box = df.copy()
    df_box['AI State'] = df_box['ai_used'].map({True: 'AI Used', False: 'No AI'})
    
    for state, color in [('No AI', COLOR_PALETTE['no_ai']), ('AI Used', COLOR_PALETTE['ai'])]:
        sub = df_box[df_box['AI State'] == state]
        fig.add_trace(
            go.Box(
                y=sub['seq_score'],
                name=state,
                marker_color=color,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8,
                showlegend=False
            ),
            row=1, col=1
        )
        
    # 2. Scatter Plot: AI Score vs Perceived Difficulty
    fig.add_trace(
        go.Scatter(
            x=user_agg['ai_score'],
            y=user_agg['avg_difficulty'],
            mode='markers',
            marker=dict(
                size=user_agg['round_duration_seconds'] / 2.0, # Sized by average duration
                sizemode='area',
                sizeref=0.5,
                sizemin=4,
                color=COLOR_PALETTE['primary'],
                line=dict(color='rgba(255, 255, 255, 0.2)', width=1)
            ),
            name="Subjects",
            hovertemplate="Subject: %{customdata}<br>AI Score: %{x:.1%}<br>Avg Difficulty: %{y:.2f}",
            customdata=user_agg['prolific_id']
        ),
        row=1, col=2
    )
    
    # Add Trendline to Scatter Plot
    if len(user_agg) > 1:
        try:
            x_vals = user_agg['ai_score'].dropna()
            y_vals = user_agg['avg_difficulty'].dropna()
            slope, intercept = np.polyfit(x_vals, y_vals, 1)
            x_range = np.linspace(x_vals.min(), x_vals.max(), 100)
            y_range = slope * x_range + intercept
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=y_range,
                    mode='lines',
                    line=dict(color=COLOR_PALETTE['secondary'], dash='dash', width=2),
                    name="Trendline",
                    showlegend=False
                ),
                row=1, col=2
            )
        except Exception:
            pass

    fig.update_yaxes(title_text="Perceived Difficulty Rating", row=1, col=1)
    fig.update_xaxes(title_text="AI Score (% of rounds AI used)", row=1, col=2)
    fig.update_yaxes(title_text="Avg Perceived Difficulty", row=1, col=2)
    
    fig.update_layout(
        height=500,
        margin=dict(t=50, b=40, l=40, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(
        f"""
        <div class="glass-card">
            <h4>Efficiency Illusion Explanation</h4>
            <p>
                The boxplot highlights a reduction in average difficulty ratings when AI is used. This fits the **Efficiency Illusion** framework: despite spending more time on task completion (H1), players feel the tasks are easier because the cognitive burden of drafting explanations is externalized to the AI.
                The scatter plot (right, bubble size indicates task time) shows a downward trend in average perceived difficulty as the subject's overall AI adoption score increases.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
