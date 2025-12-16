# app.py
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from components.layout import create_layout
from callbacks.theme import register_theme_callbacks
from callbacks.charts import register_chart_callbacks
from callbacks.controls import register_control_callbacks
from callbacks.drilldown import register_drilldown_callback
from callbacks.tabs import *  # Imports the two callbacks above

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
app.title = "Stock Analytics Pro"

# Main layout with horizontal worksheet-style tabs
app.layout = html.Div([
    dbc.Tabs(
        id="main-tabs",
        active_tab="home",          # This is correct for dbc.Tabs
        className="mb-4",
        children=[
            dbc.Tab(label="Home", tab_id="home"),
            dbc.Tab(label="Fundamental Analysis", tab_id="fundamentals"),
        ]
    ),
    html.Div(id="tab-content")
])
# Register all your existing callbacks (they work perfectly on the Home tab)
register_theme_callbacks(app)
register_chart_callbacks(app)
register_control_callbacks(app)
register_drilldown_callback(app)

# The tab callbacks are already registered via the import above

if __name__ == "__main__":
    app.run(debug=True, port=8050)