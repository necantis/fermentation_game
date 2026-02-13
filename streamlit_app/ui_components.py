import streamlit as st
import plotly.graph_objects as go
from game_logic import SENSOR_DEFS, SENSOR_RANGES, LINE_COLORS

def render_sensor_chart(sensor_id, history):
    """
    Render a single sensor chart using Plotly.
    Includes 'Normal' range background.
    """
    def_data = SENSOR_DEFS[sensor_id]
    ranges = SENSOR_RANGES.get(sensor_id, {})
    
    # Create X-axis labels (T1, T2, ...) based on history length
    x_labels = [f"T{i+1}" for i in range(len(history))]
    
    fig = go.Figure()

    # Add Normal Range (Green Background)
    if 'normal' in ranges:
        min_norm, max_norm = ranges['normal']
        fig.add_hrect(
            y0=min_norm, y1=max_norm,
            fillcolor="green", opacity=0.1,
            layer="below", line_width=0,
        )

    # Add Trace
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=history,
        mode='lines+markers',
        line=dict(color=LINE_COLORS.get(sensor_id, 'blue'), width=3),
        marker=dict(size=8),
        name=def_data['label']
    ))
    
    # Layout Update
    fig.update_layout(
        title=dict(text=f"{def_data['label']} ({def_data['unit']})", font=dict(size=14)),
        margin=dict(l=20, r=20, t=40, b=20),
        height=200,
        yaxis=dict(
            range=[def_data['min'], def_data['max']],
            autorange=False
        ),
        xaxis=dict(
            fixedrange=True
        )
    )
    
    return fig

def render_dashboard(game_state):
    """Render the 4 sensor graphs."""
    cols = st.columns(2) # 2x2 grid or 1x4? Code implies 1x4 stack on left. Let's do 1 column for left panel simulation.
    
    # Actually, mimicking the layout: Left Panel (Graphs), Middle (User), Right (AI)
    # in Streamlit, we might want columns: [2, 3, 2]
    
    # For this function, we just return the figures or render them in the current context.
    # Let's assume the caller sets up the column.
    
    sensors = ['sg', 'wortTemp', 'co2Activity', 'ph']
    for s in sensors:
        fig = render_sensor_chart(s, game_state.sensor_history[s])
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{s}_{game_state.round_number}")

