from dash import Input, Output, State
from data.db import load_price_data
from utils.metrics import add_returns
from components.cards import card_style
from config.theme import DARK, LIGHT
from dash import html
import plotly.express as px
from dash import dcc

def register_drilldown_callback(app):
    """Register month drilldown callback."""
    
    @app.callback(
        Output("month_drilldown_card", "children"),
        Input("monthly_heat", "clickData"),
        State("symbols", "value"),
        State("season_year", "value"),
        State("theme_store", "data"),
        prevent_initial_call=False
    )
    def update_month_card(clickData, symbols, season_year, mode):
        """Display drilldown details when user clicks a month on the heatmap."""
        if not clickData:
            return None

        theme = DARK if mode == "dark" else LIGHT
        df = load_price_data(symbols or [])
        
        if df.empty:
            return html.Div("No Data", style={"color": theme["TEXT"]})

        df = add_returns(df)

        # Extract clicked symbol and month
        pt = clickData["points"][0]
        month = int(pt["x"])
        sym = str(pt["y"])

        df_sym = df[df["symbol"] == sym]
        year = int(df_sym["date"].dt.year.max()) if season_year == "ALL" else int(season_year)

        sdf = df_sym[(df_sym["date"].dt.year == year) & (df_sym["date"].dt.month == month)]
        
        if sdf.empty:
            return html.Div(f"{sym} • {year}-{month:02d} (No data)", style={"color": theme["TEXT"]})

        # Calculate stats
        first_close = float(sdf["close"].iloc[0])
        last_close = float(sdf["close"].iloc[-1])
        mret = (last_close - first_close) / first_close
        peak = sdf["close"].cummax()
        dd = (sdf["close"] / peak - 1).min()
        vol = float(sdf["returns"].std() * (252 ** 0.5))

        # Create chart
        fig = px.line(sdf, x="date", y="close", title=f"{sym} Daily Close • {year}-{month:02d}")
        fig.update_layout(
            paper_bgcolor=theme["CARD_BG"],
            plot_bgcolor=theme["CARD_BG"],
            font_color=theme["TEXT"],
            xaxis=dict(gridcolor=theme["GRID"]),
            yaxis=dict(gridcolor=theme["GRID"]),
        )

        return html.Div(
            style={
                "marginTop": "40px",
                "display": "grid",
                "gridTemplateColumns": "1fr 300px",
                "gap": "20px",
                "maxWidth": "100%",
                "width": "100%",
                "boxSizing": "border-box",
                "overflow": "hidden",
            },
            children=[
                html.Div(
                    style={"minWidth": "0", "overflow": "hidden"},
                    children=[
                        html.H3(f"{sym} • {year}-{month:02d}", style={"marginTop": "0", "marginBottom": "12px"}),
                        dcc.Graph(figure=fig, style={"height": "400px", "margin": "0"})
                    ]
                ),
                html.Div(
                    style={**card_style(theme), "minWidth": "0", "maxWidth": "300px", "height": "fit-content"},
                    children=[
                        html.H4("Month Snapshot", style={"marginTop": "0"}),
                        html.Div(f"Return: {mret*100:.2f}%", style={"marginTop": "8px"}),
                        html.Div(f"Annualized Vol (in-month): {vol*100:.2f}%", style={"marginTop": "6px"}),
                        html.Div(f"Max Drawdown (in-month): {dd*100:.2f}%", style={"marginTop": "6px"}),
                        html.Br(),
                        html.Div("Tip: Click other months to compare behavior.", style={"opacity": 0.75})
                    ]
                )
            ]
        )