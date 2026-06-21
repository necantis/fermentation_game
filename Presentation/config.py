import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go
import os

# Page Setup Defaults
PAGE_TITLE = "Scientific Presentation: AI in Fermentation troubleshooting"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "collapsed"

# Harmonious HSL-derived palette (Theme: Dark Slate & Celestial Blue/Rose)
COLOR_PALETTE = {
    "primary": "#38bdf8",       # Sky Blue
    "secondary": "#a855f7",     # Purple
    "no_ai": "#f43f5e",         # Rose (Control)
    "ai": "#0284c7",            # Celestial Blue (Treatment)
    "success": "#10b981",       # Emerald
    "warning": "#f59e0b",       # Amber
    "background": "#0f172a",    # Dark Slate
    "card_bg": "#1e293b",       # Slate 800
    "text": "#f1f5f9",          # Light gray
    "text_muted": "#94a3b8",    # Muted gray
    "grid": "rgba(255, 255, 255, 0.08)",
}

# Define and register custom Plotly template
def setup_plotly_theme():
    """Sets up a custom dark, clean template for Plotly matching the scientific presentation design."""
    custom_template = go.layout.Template()
    
    # Layout styles
    custom_template.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            size=12,
            color=COLOR_PALETTE["text"]
        ),
        title=dict(
            font=dict(
                family="Outfit, sans-serif",
                size=18,
                color=COLOR_PALETTE["text"]
            ),
            x=0.05
        ),
        xaxis=dict(
            gridcolor=COLOR_PALETTE["grid"],
            linecolor=COLOR_PALETTE["grid"],
            zerolinecolor=COLOR_PALETTE["grid"],
            title=dict(font=dict(size=13, color=COLOR_PALETTE["text_muted"]))
        ),
        yaxis=dict(
            gridcolor=COLOR_PALETTE["grid"],
            linecolor=COLOR_PALETTE["grid"],
            zerolinecolor=COLOR_PALETTE["grid"],
            title=dict(font=dict(size=13, color=COLOR_PALETTE["text_muted"]))
        ),
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.6)",
            bordercolor=COLOR_PALETTE["grid"],
            borderwidth=1,
            font=dict(size=11, color=COLOR_PALETTE["text_muted"])
        ),
        colorway=[
            COLOR_PALETTE["primary"],
            COLOR_PALETTE["no_ai"],
            COLOR_PALETTE["success"],
            COLOR_PALETTE["secondary"],
            COLOR_PALETTE["warning"],
        ],
        hovermode="closest",
        margin=dict(t=50, b=40, l=50, r=30)
    )
    
    # Register and set as default
    pio.templates["scientific_presentation"] = custom_template
    pio.templates.default = "scientific_presentation"

def inject_custom_css():
    """Injects custom CSS from the styles.css file in the same directory."""
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning("Styles stylesheet not found.")
