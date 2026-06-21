import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from Presentation.data_loader import calculate_ttest_summary
from Presentation.config import COLOR_PALETTE

def render_tab_2(df, df_feedback):
    st.markdown("## H2: Delegation Effect (Answer Complexity & Length)")
    st.markdown("**Hypothesis**: Accessing the AI leads to cognitive offloading, where subjects write shorter or less complex assessments, relying instead on AI outputs.")
    
    # Calculate stats
    stats_len = calculate_ttest_summary(df, 'ai_used', 'text_len', group1_val=True, group2_val=False)
    stats_comp = calculate_ttest_summary(df, 'ai_used', 'complexity', group1_val=True, group2_val=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        sig_class = "badge-sig" if stats_len["significant"] else "badge-non-sig"
        sig_text = "SIGNIFICANT" if stats_len["significant"] else "NOT SIGNIFICANT"
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%;">
                <h4>Text Length Analysis (Characters)</h4>
                <p>Testing if AI usage changes the length of troubleshooting write-ups.</p>
                <div class="metric-container">
                    <span class="stats-badge {sig_class}">{sig_text}</span><br>
                    <strong>t-stat</strong>: {stats_len['t_stat']:.3f} | <strong>p-val</strong>: {stats_len['p_val']:.4f}<br>
                    <strong>AI Used Mean</strong>: {stats_len['g1_mean']:.1f} chars<br>
                    <strong>No AI Mean</strong>: {stats_len['g2_mean']:.1f} chars
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        sig_class = "badge-sig" if stats_comp["significant"] else "badge-non-sig"
        sig_text = "SIGNIFICANT" if stats_comp["significant"] else "NOT SIGNIFICANT"
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%;">
                <h4>Complexity Analysis (Word length × Word count)</h4>
                <p>Testing if AI usage changes the information density of write-ups.</p>
                <div class="metric-container" style="border-left-color: {COLOR_PALETTE['secondary']};">
                    <span class="stats-badge {sig_class}">{sig_text}</span><br>
                    <strong>t-stat</strong>: {stats_comp['t_stat']:.3f} | <strong>p-val</strong>: {stats_comp['p_val']:.4f}<br>
                    <strong>AI Used Mean</strong>: {stats_comp['g1_mean']:.1f}<br>
                    <strong>No AI Mean</strong>: {stats_comp['g2_mean']:.1f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Write-up Length", "Write-up Complexity", "AI Similarity vs Complexity"),
        column_widths=[0.3, 0.3, 0.4],
        horizontal_spacing=0.08
    )
    
    # 1. Text Length Boxplot
    df_box = df.copy()
    df_box['AI State'] = df_box['ai_used'].map({True: 'AI Used', False: 'No AI'})
    
    for state, color in [('No AI', COLOR_PALETTE['no_ai']), ('AI Used', COLOR_PALETTE['ai'])]:
        sub = df_box[df_box['AI State'] == state]
        fig.add_trace(
            go.Box(
                y=sub['text_len'],
                name=state,
                marker_color=color,
                boxpoints='outliers',
                showlegend=False
            ),
            row=1, col=1
        )
        
    # 2. Complexity Boxplot
    for state, color in [('No AI', COLOR_PALETTE['no_ai']), ('AI Used', COLOR_PALETTE['ai'])]:
        sub = df_box[df_box['AI State'] == state]
        fig.add_trace(
            go.Box(
                y=sub['complexity'],
                name=state,
                marker_color=color,
                boxpoints='outliers',
                showlegend=False
            ),
            row=1, col=2
        )
        
    # 3. Scatter Plot: AI Similarity vs Complexity (AI Users only)
    ai_only = df[df['ai_used'] == True]
    if not ai_only.empty:
        fig.add_trace(
            go.Scatter(
                x=ai_only['ai_similarity'],
                y=ai_only['complexity'],
                mode='markers',
                marker=dict(
                    color=COLOR_PALETTE['primary'],
                    size=8,
                    line=dict(width=1, color='rgba(255, 255, 255, 0.2)')
                ),
                name="AI Users",
                hovertemplate="Similarity: %{x:.2f}<br>Complexity: %{y:.1f}"
            ),
            row=1, col=3
        )
        
        # Add regression line
        if len(ai_only) > 1:
            try:
                x_vals = ai_only['ai_similarity'].dropna()
                y_vals = ai_only['complexity'].dropna()
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
                    row=1, col=3
                )
            except Exception:
                pass
                
    fig.update_yaxes(title_text="Character Count", row=1, col=1)
    fig.update_yaxes(title_text="Complexity Score", row=1, col=2)
    fig.update_xaxes(title_text="Similarity to AI Suggestion", row=1, col=3)
    fig.update_yaxes(title_text="Complexity Score", row=1, col=3)
    
    fig.update_layout(
        height=450,
        margin=dict(t=50, b=40, l=40, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(
        f"""
        <div class="glass-card">
            <h4>Scientific Interpretation</h4>
            <p>
                Contrary to expectations, subjects utilizing the AI assistant often produce <b>longer</b> and <b>more complex</b> responses than control group subjects. 
                However, when looking closely at the similarity chart (right), there is a strong correlation between high AI similarity (indicating direct copy-pasting of AI recommendations) and reduced individual complexity. 
                This indicates a split strategy: some players use the AI to bootstrap highly complex analytical descriptions, while others delegate entirely and copy-paste.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------
    # IFRAME EMBEDDING SECTION
    # ---------------------------------------------
    st.markdown("---")
    st.markdown("### Interactive Lab Session: Fermentation troubleshooting Simulator")
    st.markdown("You can run troubleshooting sequences in real-time below to observe the delegation effects and cognitive offloading patterns.")
    
    iframe_html = """
    <div class="iframe-container">
        <iframe src="http://localhost:8501/" title="Fermentation Troubleshooting Game"></iframe>
    </div>
    """
    st.markdown(iframe_html, unsafe_allow_html=True)

