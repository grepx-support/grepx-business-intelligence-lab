from dash import html
from config.theme import ACCENT, SAFE, WARN, DANGER

def card_style(theme):
    """Returns base card styling dictionary."""
    return {
        "backgroundColor": theme["CARD_BG"],
        "borderRadius": "18px",
        "padding": "14px",
        "boxShadow": "0 14px 40px rgba(0,0,0,0.30)",
        "border": f"1px solid {theme['GRID']}",
    }

def kpi_card(theme, title, big, sub, color=ACCENT):
    """Creates a KPI card with title, big value, and subtitle."""
    return html.Div(
        style={
            **card_style(theme),
            "background": f"linear-gradient(135deg, {color}26, {theme['CARD_BG']})",
            "minHeight": "92px",
        },
        children=[
            html.Div(title, style={"fontSize": "12px", "opacity": 0.85, "color": theme["MUTED"]}),
            html.Div(big, style={"fontSize": "28px", "fontWeight": "800", "marginTop": "6px", "color": theme["TEXT"]}),
            html.Div(sub, style={"fontSize": "12px", "opacity": 0.8, "marginTop": "4px", "color": theme["MUTED"]}),
        ]
    )


def risk_chip_color(score):
    """Returns (color, label) tuple based on risk score."""
    if score < 30:
        return SAFE, "Low"
    elif score < 60:
        return WARN, "Medium"
    elif score < 80:
        return "#ff9f1a", "High"
    else:
        return DANGER, "Extreme"


def risk_card(theme, sym, score, ann_vol, max_dd):
    """Creates a risk metric card for a single symbol."""
    color, label = risk_chip_color(score)
    return html.Div(
        style={
            **card_style(theme),
            "minWidth": "260px",
            "background": f"linear-gradient(180deg, {color}18, {theme['CARD_BG']})",
        },
        children=[
            html.Div(sym, style={"fontSize": "13px", "letterSpacing": "1px", "color": theme["MUTED"]}),
            html.Div(f"{score:.2f}/100", style={"fontSize": "34px", "fontWeight": "900", "marginTop": "6px", "color": theme["TEXT"]}),
            html.Div(label + " Risk", style={"fontSize": "12px", "fontWeight": "700", "color": color}),
            html.Div(f"Ann Vol: {ann_vol:.2%}  |  Max DD: {max_dd:.2%}", style={"fontSize": "12px", "marginTop": "8px", "color": theme["MUTED"]})
        ]
    )

from dash import dcc

def nvda_stock_link():
    """Return a navigation link component to the NVDA stock page."""
    return dcc.Link(
        html.H4(
            "NVDA",
            style={"color": "#4da3ff", "fontWeight": "bold"},
        ),
        href="/stock/NVDA",
    )
