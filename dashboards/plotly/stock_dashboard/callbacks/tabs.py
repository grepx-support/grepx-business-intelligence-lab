# callbacks/tabs.py
from dash import Input, Output, callback, html, dcc
import dash_bootstrap_components as dbc

from fundamentals.fundamentals import get_fundamentals

# List of your stocks (keep consistent with your main list)
SYMBOLS = ["AMZN", "MSFT", "NVDA", "TSLA", "META", "GOOGL", "NFLX", "INTC", "BABA"]

@callback(
    Output("tab-content", "children"),
    Input("main-tabs", "active_tab")
)
def render_tab_content(active_tab):

    if active_tab == "home":
        # Import here to avoid circular imports
        from components.layout import create_layout
        return create_layout()

    elif active_tab == "fundamentals":
        return dbc.Container([
            html.H2("Fundamental Analysis Worksheet", className="mt-4 mb-4 text-primary"),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Stock", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="fund-stock-dropdown",
                        options=[{"label": s, "value": s} for s in SYMBOLS],
                        value="NVDA",
                        clearable=False,
                        searchable=True,
                        className="mb-4"
                    ),
                ], width=4)
            ]),
            html.Div(id="fund-details")
        ], fluid=True)


@callback(
    Output("fund-details", "children"),
    Input("fund-stock-dropdown", "value")
)
def update_fund_details(ticker):
    if not ticker:
        return html.Div("Select a stock above.", className="text-muted")

    ticker = ticker.upper()
    fundamentals = get_fundamentals(ticker)  # Live yfinance data

    # Create responsive cards for each fundamental metric
    fund_cards = dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6(key, className="card-title text-muted small"),
                    html.H4(
                        str(value) if value is not None else "N/A",
                        className="card-text fw-bold text-primary"
                    )
                ])
            ], className="shadow-sm"),
            width=3,
            className="mb-4"
        ) for key, value in fundamentals.items()
    ])

    # Balanced recommendation – accurate as of December 15, 2025
    recommendation = dbc.Alert([
        html.H3("Investment Recommendation (as of December 15, 2025)", className="alert-heading"),
        html.H4("Strong Buy – Premier AI Growth Stock for Risk-Tolerant Investors", className="text-success fw-bold mb-3"),
        html.P([
            f"{ticker} remains the undisputed leader in AI accelerators. Current price ~$175 ",
            "(after October high of $212). Analyst consensus: Strong Buy (39–64 analysts), ",
            "average 12-month price target $248–259 (~41–48% upside)."
        ]),
        html.Hr(),
        html.H5("Key Strengths & Opportunities"),
        html.Ul([
            html.Li("Unmatched AI GPU dominance; explosive data center demand."),
            html.Li("Exceptional profitability: Gross margins ~70–75%, net margins >50%."),
            html.Li("Forward P/E ~23–30 reasonable given strong earnings growth (TTM EPS ~$4.06)."),
            html.Li("Blackwell ramping strongly in permitted markets; Rubin on track for 2026."),
            html.Li("Limited H200 exports to China approved (with controls); potential revenue recapture."),
        ]),
        html.H5("Major Risks & Challenges"),
        html.Ul([
            html.Li("Trailing P/E ~43–46 elevated; limited margin of safety if AI spending slows."),
            html.Li("Geopolitical restrictions: Blackwell/Rubin banned in China; H200 sales controlled."),
            html.Li("Rising competition from AMD, Intel, and custom ASICs (Google, Amazon, Meta)."),
            html.Li("High volatility (Beta >2.0); history of sharp 30–50% corrections."),
            html.Li("Potential AI capex normalization in 2026."),
        ]),
        html.P("Overall: Outstanding long-term compounder for growth portfolios. Best with dollar-cost averaging and position sizing (5–10% allocation). Not suitable for conservative investors.", className="mt-3 fst-italic fw-medium")
    ], color="info", className="mt-4 shadow-sm")

    return html.Div([
        html.H2(f"{ticker} – Detailed Fundamentals & Insights", className="mb-4 text-center"),
        html.Hr(),
        fund_cards,
        recommendation
    ])
    
