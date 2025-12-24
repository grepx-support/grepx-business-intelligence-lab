from dash import dcc, html

SYMBOLS = ["AMZN", "MSFT", "NVDA", "TSLA", "META", "GOOGL", "NFLX", "INTC", "BABA"]

def create_layout():
    """Create main page layout."""
    return html.Div(
    id="page",
    className="light-theme",
    children=[
        dcc.Store(id="theme_store", data="light"),
        dcc.Store(id="heat_click_store"),
        dcc.Store(id="global_state", storage_type="memory"),
        
        # Header
        html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "gap": "12px"},
            children=[
                html.Div([
                    html.H1(
                        "Stock Analytics Pro",
                        style={
                            "margin": "0",
                            "fontSize": "36px",
                            "fontWeight": "800",
                            "letterSpacing": "-0.8px",
                            "background": "linear-gradient(135deg, #4da3ff 0%, #2c5aa0 50%, #1a1a1a 100%)",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                            "backgroundClip": "text"
                        }
                    ),
                    html.Div(
                        "Advanced portfolio analytics with real-time risk metrics",
                        style={"fontSize": "13px", "color": "#888888", "marginTop": "6px", "fontWeight": "400", "letterSpacing": "0.3px"}
                    )
                ]),
                html.Div(
                    style={"display": "flex", "gap": "18px", "alignItems": "center", "paddingRight": "8px"},
                    children=[
                        html.Div("THEME", style={"fontSize": "11px", "fontWeight": "700", "color": "#4da3ff", "textTransform": "uppercase", "letterSpacing": "1px"}),
                        html.Div(
                            id="theme_toggle_switch",
                            style={"display": "flex", "alignItems": "center", "gap": "10px", "cursor": "pointer", "userSelect": "none"},
                            children=[
                                html.Div(
                                    id="toggle-button",
                                    style={
                                        "width": "50px",
                                        "height": "26px",
                                        "borderRadius": "13px",
                                        "backgroundColor": "#4da3ff",
                                        "position": "relative",
                                        "transition": "background-color 0.3s ease",
                                        "border": "none",
                                        "padding": "2px"
                                    },
                                    children=[
                                        html.Div(
                                            style={
                                                "width": "20px",
                                                "height": "20px",
                                                "borderRadius": "50%",
                                                "backgroundColor": "white",
                                                "position": "absolute",
                                                "right": "3px",
                                                "top": "3px",
                                                "transition": "right 0.3s ease"
                                            }
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ],
        ),
        html.Br(),

        # Controls
        html.Div(
            id="controls_card",
            children=[
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "minmax(0,2fr) minmax(0,1fr)", "gap": "14px"},
                    children=[
                        html.Div([
                            html.Div("Tickers", style={"opacity": 0.8}),
                            dcc.Dropdown(id="symbols", options=[{"label": s, "value": s} for s in SYMBOLS], value=SYMBOLS, multi=True, className="dark-dropdown"),
                        ]),
                        html.Div([
                            html.Div("Price Metric", style={"opacity": 0.8}),
                            dcc.Dropdown(id="metric", options=[
                                {"label": "Close", "value": "close"},
                                {"label": "Volume", "value": "volume"},
                                {"label": "VWAP", "value": "vwap"},
                            ], value="close", className="dark-dropdown"),
                        ]),
                        html.Div([
                            html.Div("Scale", style={"opacity": 0.8}),
                            dcc.Dropdown(id="scale_mode", options=[
                                {"label": "Raw", "value": "raw"},
                                {"label": "Normalized (100)", "value": "norm"},
                            ], value="raw", className="dark-dropdown"),
                        ]),
                        html.Div([
                            html.Div("Year", style={"opacity": 0.8}),
                            dcc.Dropdown(id="season_year", options=[{"label": "ALL", "value": "ALL"}], value="ALL", className="dark-dropdown"),
                        ]),
                    ]
                )
            ],
        ),
        html.Br(),

        # KPI Grid
        html.Div(id="kpi_grid"),
        html.Br(),

        # Charts Row 1
        html.Div(
            id="row1",
            style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "14px"},
            children=[
                html.Div(id="price_card", children=[dcc.Graph(id="price_chart")]),
                html.Div(id="corr_card", children=[dcc.Graph(id="corr_heat")]),
            ]
        ),
        html.Br(),

        # Charts Row 2
        html.Div(
            id="row2",
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"},
            children=[
                html.Div(id="monthly_card", children=[dcc.Graph(id="monthly_heat")]),
                html.Div(id="yearly_card", children=[dcc.Graph(id="yearly_line")]),
            ]
        ),
        html.Br(),

        # Risk Cards
        html.Div(id="risk_cards", style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),

        # Month Drilldown Modal
        html.Div(id="month_drilldown_card")
    ]
)
