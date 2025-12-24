from dash import Input, Output
from data.db import load_price_data

def register_control_callbacks(app):
    """Register dropdown and control callbacks."""
    
    @app.callback(
        Output("symbols", "className"),
        Output("metric", "className"),
        Output("scale_mode", "className"),
        Output("season_year", "className"),
        Input("theme_store", "data")
    )
    def update_dropdown_theme(mode):
        """Dynamically change dropdown class based on theme."""
        dropdown_class = "dark-dropdown" if mode == "dark" else "light-dropdown"
        return dropdown_class, dropdown_class, dropdown_class, dropdown_class


    @app.callback(
        Output("season_year", "options"),
        Input("symbols", "value"),
    )
    def set_year_options(symbols):
        """Update year dropdown options based on selected symbols."""
        df = load_price_data(symbols or [])
        if df.empty:
            return [{"label": "ALL (Seasonality)", "value": "ALL"}]
        years = sorted(df["date"].dt.year.dropna().unique().tolist())
        return [{"label": "ALL", "value": "ALL"}] + [{"label": str(y), "value": str(y)} for y in years]
