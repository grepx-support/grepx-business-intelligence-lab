from dash import Input, Output, State, html
from config.theme import DARK, LIGHT
from components.cards import card_style

def register_theme_callbacks(app):
    """Register all theme-related callbacks."""
        
    @app.callback(
        Output("theme_store", "data"),
        Output("toggle-button", "children"),
        Input("theme_toggle_switch", "n_clicks"),
        State("theme_store", "data"),
        prevent_initial_call=True
    )
    def toggle_theme(n_clicks, current_theme):
        """Toggle between light and dark theme."""
        new_theme = "dark" if current_theme == "light" else "light"
        circle_position = "3px" if new_theme == "dark" else "27px"
        
        circle = html.Div(
            style={
                "width": "20px",
                "height": "20px",
                "borderRadius": "50%",
                "backgroundColor": "white",
                "position": "absolute",
                "left": circle_position,
                "top": "3px",
                "transition": "left 0.3s ease"
            }
        )
        
        return new_theme, [circle]

    @app.callback(
        Output("page", "style"),
        Output("controls_card", "style"),
        Output("price_card", "style"),
        Output("corr_card", "style"),
        Output("monthly_card", "style"),
        Output("yearly_card", "style"),
        Output("kpi_grid", "style"),
        Input("theme_store", "data")
    )
    def apply_theme(mode):
        """Apply theme colors to all major components."""
        theme = LIGHT if mode == "light" else DARK
        base = {"backgroundColor": theme["APP_BG"], "minHeight": "100vh", "padding": "16px", "color": theme["TEXT"]}
        c = {**card_style(theme)}
        grid = {"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "14px"}
        return base, c, c, c, c, c, grid

