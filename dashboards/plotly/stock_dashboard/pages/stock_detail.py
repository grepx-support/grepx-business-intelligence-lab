# pages/stock_detail.py
from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from fundamentals.fundamentals import get_fundamentals

register_page(__name__, path_template="/stock/<ticker>")

def layout(ticker=None):
    if not ticker:
        return html.Div("Please select a ticker from the overview.")

    ticker = ticker.upper()
    fundamentals = get_fundamentals(ticker)  # Live yfinance data

    fund_cards = dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6(key, className="card-title"),
                    html.H4(value if value else "N/A", className="card-text")
                ])
            ]),
            width=3, className="mb-4"
        ) for key, value in fundamentals.items()
    ])

    # Fixed: Use className for green text instead of invalid 'color' prop
    recommendation = dbc.Alert([
        html.H3("Investment Recommendation (as of December 14, 2025)", className="alert-heading"),
        html.H4("Strong Buy – Leading AI Growth Stock for Risk-Tolerant Investors", className="text-success fw-bold"),
        html.P([
            "NVIDIA dominates AI accelerators. Current price ~$175, with analyst consensus Strong Buy ",
            "(from 39–64 analysts) and average 12-month price targets of $248–259 (41–48% upside)."
        ]),
        html.Hr(),
        html.H5("Key Strengths & Opportunities"),
        html.Ul([
            html.Li("Unmatched AI GPU leadership; explosive data center demand driving record revenue."),
            html.Li("High profitability: Gross margins ~70–75%, net margins >50%."),
            html.Li("Forward P/E ~23–30 reasonable given strong earnings growth (TTM EPS ~$4.06)."),
            html.Li("Blackwell chips ramping strongly in volume; Rubin platform planned for 2026."),
            html.Li("Strong balance sheet: Low debt, massive cash flow for R&D and buybacks."),
        ]),
        html.H5("Major Risks & Challenges"),
        html.Ul([
            html.Li("Elevated trailing P/E ~43–45 with limited safety margin if AI capex slows."),
            html.Li("Geopolitical restrictions: Limited H200 approval for China; Blackwell/Rubin fully banned."),
            html.Li("Rising competition from AMD, Intel, and custom ASICs (Google, Amazon, Meta)."),
            html.Li("High volatility (Beta >2.0); history of sharp corrections."),
            html.Li("Potential AI spending normalization in 2026+."),
        ]),
        html.P("Overall: Top-tier long-term growth stock. Use dollar-cost averaging and limit allocation (5–10%). Not suitable for conservative investors.", className="mt-3 fst-italic")
    ], color="info", className="mt-4")

    return dbc.Container([
        html.H1(f"{ticker} - Insights & Recommendation"),
        dcc.Link("← Back to Overview", href="/", className="btn btn-primary mb-3"),
        html.Hr(),
        html.H2("Key Fundamentals"),
        fund_cards,
        recommendation,
        html.H2("Technical Analysis", className="mt-5"),
        html.P("Candlestick chart and technical metrics coming soon...", className="text-muted")
    ], fluid=True)