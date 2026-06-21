import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.stats as stats
from Presentation.config import COLOR_PALETTE

def render_tab_4(df, df_feedback):
    st.markdown("## Participant Clusters: Copiers vs Improvers vs Control")
    st.markdown("This tab aggregates metrics by participant to classify their strategy: **Copier** (high similarity, lower individual complexity), **Improver** (uses AI but expands/rewrites), or **No AI** (Control).")

    # Aggregate by player
    user_agg = df.groupby('prolific_id').agg({
        'ai_used': 'mean', # AI Score
        'round_duration_seconds': 'mean',
        'complexity': 'mean',
        'seq_score': 'mean',
        'ai_similarity': 'mean'
    }).reset_index()

    user_agg.rename(columns={
        'ai_used': 'ai_score',
        'round_duration_seconds': 'avg_time',
        'seq_score': 'avg_difficulty',
        'ai_similarity': 'avg_similarity'
    }, inplace=True)

    user_agg['avg_similarity'] = user_agg['avg_similarity'].fillna(0.0)

    # Classification
    def classify_user(row):
        if row['ai_score'] > 0 and row['complexity'] < 40:
            return 'Copier'
        elif row['ai_score'] > 0 and row['complexity'] > 80:
            return 'Improver'
        else:
            return 'Users'

    user_agg['cluster'] = user_agg.apply(classify_user, axis=1)

    # Interactive options to control presentation
    col_filters_1, col_filters_2 = st.columns(2)
    with col_filters_1:
        color_theme = st.selectbox("Color Bubble Gradient By", ["Avg Time per Round", "Avg Similarity to AI"])
    with col_filters_2:
        size_metric = st.selectbox("Bubble Size Represents", ["Avg Perceived Difficulty", "Avg Complexity"])

    # Map selected options to columns
    color_col = 'avg_time' if color_theme == "Avg Time per Round" else 'avg_similarity'
    size_col = 'avg_difficulty' if size_metric == "Avg Perceived Difficulty" else 'complexity'

    # Build the multi-variate bubble chart
    fig = go.Figure()

    cluster_shapes = {
        'Copier': 'square',
        'Improver': 'triangle-up',
        'Users': 'circle'
    }
    
    cluster_colors = {
        'Copier': COLOR_PALETTE['no_ai'],
        'Improver': COLOR_PALETTE['success'],
        'Users': COLOR_PALETTE['primary']
    }

    # Plot each cluster as a separate trace
    for cluster_name in ['Copier', 'Improver', 'Users']:
        cluster_data = user_agg[user_agg['cluster'] == cluster_name]
        if cluster_data.empty:
            continue

        # Scale size representation
        sizes = cluster_data[size_col].fillna(0)
        if size_col == 'complexity':
            display_sizes = np.clip(sizes * 0.2, 8, 40)
        else: # difficulty
            display_sizes = np.clip(sizes * 3.5, 8, 40)

        fig.add_trace(
            go.Scatter(
                x=cluster_data['ai_score'],
                y=cluster_data['complexity'],
                mode='markers',
                marker=dict(
                    symbol=cluster_shapes[cluster_name],
                    size=display_sizes,
                    color=cluster_data[color_col],
                    colorscale='Cividis' if color_col == 'avg_time' else 'Blues',
                    showscale=True if cluster_name == 'Users' else False,
                    colorbar=dict(
                        title=color_theme,
                        thickness=15,
                        x=1.02
                    ) if cluster_name == 'Users' else None,
                    line=dict(color='rgba(255, 255, 255, 0.4)', width=1.5)
                ),
                name=f"{cluster_name} (Shape: {cluster_shapes[cluster_name]})",
                customdata=np.stack((cluster_data['prolific_id'], cluster_data['avg_time'], cluster_data['avg_difficulty'], cluster_data['avg_similarity']), axis=-1),
                hovertemplate="<b>ID</b>: %{customdata[0]}<br>" +
                              "<b>Cluster</b>: " + cluster_name + "<br>" +
                              "<b>AI Score</b>: %{x:.1%}<br>" +
                              "<b>Complexity</b>: %{y:.1f}<br>" +
                              "<b>Avg Time</b>: %{customdata[1]:.1f}s<br>" +
                              "<b>Avg Difficulty</b>: %{customdata[2]:.2f}<br>" +
                              "<b>Avg Similarity</b>: %{customdata[3]:.2f}"
            )
        )

        # Overlay Regression line if enough points
        if len(cluster_data) > 1:
            try:
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    cluster_data['ai_score'].astype(float), cluster_data['complexity'].astype(float)
                )
                x_vals = np.linspace(cluster_data['ai_score'].min(), cluster_data['ai_score'].max(), 50)
                y_vals = slope * x_vals + intercept
                fig.add_trace(
                    go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='lines',
                        line=dict(color=cluster_colors[cluster_name], width=1.5, dash='dash'),
                        name=f"{cluster_name} Trend (R²={(r_value**2):.2f})",
                        hoverinfo='skip'
                    )
                )
            except Exception:
                pass

    fig.update_layout(
        title="Figure 2: Interactive Bubble Chart (AI Score vs Complexity)",
        xaxis_title="AI Usage Score (Percentage of Rounds)",
        yaxis_title="Average Text Complexity (Word Length × Word Count)",
        height=500,
        margin=dict(t=60, b=50, l=50, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 10px;">
            <div class="glass-card" style="border-top: 4px solid {COLOR_PALETTE['no_ai']};">
                <h4 style="color: {COLOR_PALETTE['no_ai']};">Copier Group</h4>
                <p style="font-size: 0.9rem; color: {COLOR_PALETTE['text']};">
                    High AI score, low complexity writeups. These subjects rely on direct copy-pasting of AI recommendations without critical modifications, resulting in rapid submissions but lower individual information synthesis.
                </p>
            </div>
            <div class="glass-card" style="border-top: 4px solid {COLOR_PALETTE['success']};">
                <h4 style="color: {COLOR_PALETTE['success']};">Improver Group</h4>
                <p style="font-size: 0.9rem; color: {COLOR_PALETTE['text']};">
                    High AI score, high complexity writeups. These subjects read the AI suggestions, then elaborate or extend them with custom laboratory metrics. They use the AI as a scaffolding assistant to produce richer outcomes.
                </p>
            </div>
            <div class="glass-card" style="border-top: 4px solid {COLOR_PALETTE['primary']};">
                <h4 style="color: {COLOR_PALETTE['primary']};">Control / Users</h4>
                <p style="font-size: 0.9rem; color: {COLOR_PALETTE['text']};">
                    Subjects who do not use the AI, or use it sporadically. They exhibit a wide spread of timings and text complexity, representing the baseline performance of organic troubleshooting.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------
    # OPERATIONAL COST CALCULATOR SECTION
    # ---------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Operational Labor Cost Calculator")
    st.markdown("Verify the financial tradeoff of human-AI interaction paradigms. While **Copiers** save immediate labor time through rapid copy-pasting, **Improvers** invest more verification time but generate higher-complexity analytical outcomes.")

    # Calculate actual cluster mean round durations
    copiers_df = user_agg[user_agg['cluster'] == 'Copier']
    improvers_df = user_agg[user_agg['cluster'] == 'Improver']
    
    t_copier = float(copiers_df['avg_time'].mean()) if not copiers_df.empty else 105.0
    t_improver = float(improvers_df['avg_time'].mean()) if not improvers_df.empty else 165.0
    
    if np.isnan(t_copier): t_copier = 105.0
    if np.isnan(t_improver): t_improver = 165.0

    # Layout sliders
    col_calc_1, col_calc_2 = st.columns(2)
    with col_calc_1:
        labor_rate = st.slider("Engineering Labor Rate ($/hour)", min_value=30.0, max_value=250.0, value=120.0, step=5.0)
    with col_calc_2:
        annual_tickets = st.slider("Annual Bioreactor Troubleshooting Incidents", min_value=100, max_value=10000, value=2000, step=100)

    # Cost = (seconds / 3600) * rate * tickets
    annual_cost_copier = (t_copier / 3600.0) * labor_rate * annual_tickets
    annual_cost_improver = (t_improver / 3600.0) * labor_rate * annual_tickets
    cost_delta = annual_cost_improver - annual_cost_copier

    # Display side-by-side metrics
    col_met_1, col_met_2, col_met_3 = st.columns(3)
    with col_met_1:
        st.metric(
            label="Copier Profile Annual Cost", 
            value=f"${annual_cost_copier:,.2f}", 
            delta=f"Avg {t_copier:.1f} s per round",
            delta_color="normal"
        )
    with col_met_2:
        st.metric(
            label="Improver Profile Annual Cost", 
            value=f"${annual_cost_improver:,.2f}", 
            delta=f"Avg {t_improver:.1f} s per round",
            delta_color="inverse"
        )
    with col_met_3:
        st.metric(
            label="Operational Labor Cost Delta", 
            value=f"${abs(cost_delta):,.2f}", 
            delta="Additional quality verification cost" if cost_delta > 0 else "Time savings cost delta",
            delta_color="off"
        )

