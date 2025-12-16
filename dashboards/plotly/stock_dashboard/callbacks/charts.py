from dash import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from data.db import load_price_data
from utils.metrics import *
from config.theme import DARK, LIGHT, ACCENT, SAFE, DANGER, WARN
from components.cards import kpi_card, risk_card


def register_chart_callbacks(app):
    """Register chart update callbacks."""

    @app.callback(
        Output("price_chart", "figure"),
        Output("monthly_heat", "figure"),
        Output("yearly_line", "figure"),
        Output("corr_heat", "figure"),
        Output("kpi_grid", "children"),
        Output("risk_cards", "children"),
        Input("symbols", "value"),
        Input("metric", "value"),
        Input("scale_mode", "value"),
        Input("season_year", "value"),
        Input("theme_store", "data"),
    )
    def update(symbols, metric, scale_mode, season_year, mode):
        """Main callback to update all charts and metrics."""
        theme = DARK if mode == "dark" else LIGHT
        symbols = symbols or []
        df = load_price_data(symbols)

        if df.empty:
            empty = px.line(title="No data")
            empty.update_layout(
                paper_bgcolor=theme["CARD_BG"],
                plot_bgcolor=theme["CARD_BG"],
                font_color=theme["TEXT"]
            )
            return empty, empty, empty, empty, [], []

        df = add_returns(df)
        df = add_vwap(df)

        # Filter by year if selected
        if season_year != "ALL":
            selected_year = int(season_year)
            df = df[df["date"].dt.year == selected_year]
            if df.empty:
                empty = px.line(title=f"No data for {selected_year}")
                empty.update_layout(
                    paper_bgcolor=theme["CARD_BG"],
                    plot_bgcolor=theme["CARD_BG"],
                    font_color=theme["TEXT"]
                )
                return empty, empty, empty, empty, [], []

        df = add_normalized_price(df)

        # Price Chart
        chart_title = "Price Comparison"
        if metric == "volume":
            ycol = "volume"
            chart_title = "Volume Comparison"
        elif metric == "vwap":
            ycol = "vwap"
            chart_title = "VWAP Comparison"
        elif metric == "close":
            ycol = "norm_close" if scale_mode == "norm" else "close"
            chart_title = "Normalized Price (Base = 100)" if scale_mode == "norm" else "Price Comparison (Actual)"

        if season_year != "ALL":
            chart_title += f" ({season_year})"

        price_fig = px.line(df, x="date", y=ycol, color="symbol", title=chart_title)
        price_fig.update_layout(
            paper_bgcolor=theme["CARD_BG"],
            plot_bgcolor=theme["CARD_BG"],
            font_color=theme["TEXT"],
            legend_title_text="Ticker",
            xaxis=dict(gridcolor=theme["GRID"]),
            yaxis=dict(gridcolor=theme["GRID"]),
            height=500,
            margin=dict(l=40, r=20, t=40, b=40),
        )

        # Monthly Heatmap
        mdf = monthly_returns(df)
        if season_year != "ALL":
            yr = int(season_year)
            mdf2 = mdf[mdf["year"] == yr].copy()
            title = f"Monthly Returns ({yr})"
            heat_data = mdf2.pivot(index="symbol", columns="month", values="monthly_return")
            heat_label = "Monthly Return"
        else:
            monthly_avg = mdf.groupby(["symbol", "month"])["monthly_return"].mean().reset_index()
            title = "Average Monthly Returns"
            heat_data = monthly_avg.pivot(index="symbol", columns="month", values="monthly_return")
            heat_label = "Avg Monthly Return"

        heat_data.columns = heat_data.columns.astype(str)
        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        heat = px.imshow(
            heat_data,
            color_continuous_scale="RdYlGn",
            labels={"x": "Month", "y": "Ticker", "color": heat_label},
            title=title
        )
        heat.update_xaxes(tickmode="array", tickvals=[str(i) for i in range(1, 13)], ticktext=month_labels)
        heat.update_layout(
            paper_bgcolor=theme["CARD_BG"],
            plot_bgcolor=theme["CARD_BG"],
            font_color=theme["TEXT"],
            xaxis=dict(gridcolor=theme["GRID"]),
            yaxis=dict(gridcolor=theme["GRID"]),
            height=500,
            margin=dict(l=80, r=20, t=40, b=40),
        )

        # Yearly Returns
        ydf = yearly_returns(df)
        yearly_title = "Yearly Returns" if season_year == "ALL" else f"Yearly Returns ({season_year})"
        
        yearly_fig = px.line(ydf, x="year", y="yearly_return", color="symbol", markers=True, title=yearly_title)
        yearly_fig.update_layout(
            paper_bgcolor=theme["CARD_BG"],
            plot_bgcolor=theme["CARD_BG"],
            font_color=theme["TEXT"],
            xaxis=dict(gridcolor=theme["GRID"]),
            yaxis=dict(gridcolor=theme["GRID"]),
            height=500,
            margin=dict(l=40, r=20, t=40, b=40),
        )

        # Correlation Heatmap
        pivot = df.pivot(index="date", columns="symbol", values="returns")
        corr = pivot.corr()
        symbols_list = corr.columns.tolist()
        corr_title = "Return Correlation" if season_year == "ALL" else f"Return Correlation ({season_year})"

        corr_fig = go.Figure()
        corr_fig.add_trace(
            go.Heatmap(
                z=corr.values,
                x=symbols_list,
                y=symbols_list,
                colorscale="RdBu",
                zmid=0,
                colorbar=dict(title="Correlation")
            )
        )
        corr_fig.update_layout(
            title=corr_title,
            paper_bgcolor=theme["CARD_BG"],
            plot_bgcolor=theme["CARD_BG"],
            font_color=theme["TEXT"],
            xaxis=dict(side="bottom"),
            yaxis=dict(autorange="reversed"),
            height=500,
            margin=dict(l=100, r=50, t=40, b=100)
        )

        # KPIs
        if season_year != "ALL":
            kpi_year = int(season_year)
            latest = ydf[ydf["year"] == kpi_year].set_index("symbol")["yearly_return"].dropna()
            kpi_label = f"({kpi_year})"
        else:
            latest = ydf.groupby("symbol")["yearly_return"].mean()
            kpi_label = "(All Years Avg)"

        best_sym = latest.idxmax() if len(latest) > 0 else "N/A"
        best_val = float(latest.max()) if len(latest) > 0 else 0
        worst_sym = latest.idxmin() if len(latest) > 0 else "N/A"
        worst_val = float(latest.min()) if len(latest) > 0 else 0

        mdf_for_kpi = mdf if season_year == "ALL" else mdf[mdf["year"] == int(season_year)]
        avg_monthly_sym = mdf_for_kpi.groupby("symbol")["monthly_return"].mean().sort_values(ascending=False)
        top_m_sym = avg_monthly_sym.idxmax()
        top_m_val = float(avg_monthly_sym.max())

        avg_yearly_sym = ydf.groupby("symbol")["yearly_return"].mean().sort_values(ascending=False)
        top_y_sym = avg_yearly_sym.idxmax()
        top_y_val = float(avg_yearly_sym.max())

        cagr = cagr_by_symbol(df)
        vol = annual_vol_by_symbol(df)
        sharpe = sharpe_by_symbol(df, rf=0.04)

        best_cagr_sym = cagr.idxmax()
        best_cagr_val = float(cagr.max())
        best_sharpe_sym = sharpe.idxmax()
        best_sharpe_val = float(sharpe.max())
        avg_ann_vol = float(vol.mean())

        kpis = [
            kpi_card(theme, f"Best {kpi_label}", f"{best_sym}", f"{best_val*100:.2f}%", SAFE),
            kpi_card(theme, f"Worst {kpi_label}", f"{worst_sym}", f"{worst_val*100:.2f}%", DANGER),
            kpi_card(theme, "Avg Annual Vol", f"{avg_ann_vol*100:.2f}%", "Annualized (252)", WARN),
            kpi_card(theme, "Tickers", f"{len(symbols)}", "Selected", ACCENT),
            kpi_card(theme, "Top Avg Monthly Return", f"{top_m_sym}", f"{top_m_val*100:.2f}% ({season_year})", SAFE),
            kpi_card(theme, "Top Avg Yearly Return", f"{top_y_sym}", f"{top_y_val*100:.2f}% (Avg)", ACCENT),
            kpi_card(theme, "Best CAGR", f"{best_cagr_sym}", f"{best_cagr_val*100:.2f}%", "#9b59b6"),
            kpi_card(theme, "Best Sharpe", f"{best_sharpe_sym}", f"{best_sharpe_val:.2f} (rf=4%)", "#1abc9c"),
        ]

        # Risk Cards
        rtab = risk_table(df, window=30)
        cards = [
            risk_card(theme, r["symbol"], float(r["risk_score"]), float(r["ann_vol"]), float(r["max_drawdown"]))
            for _, r in rtab.iterrows()
        ]

        return price_fig, heat, yearly_fig, corr_fig, kpis, cards
