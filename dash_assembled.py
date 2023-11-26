from dash import Dash, html, dcc, Input, Output, Patch, clientside_callback, callback
import plotly.express as px
import plotly.io as pio
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from backtest import *


# Ajoutez vos données et initialisez l'application Dash comme auparavant...
load_figure_template(["minty", "minty_dark"])

df = px.data.gapminder()

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME])

color_mode_switch = html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="color-mode-switch"),
        dbc.Switch(id="color-mode-switch", value=False, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="color-mode-switch"),
    ]
)

test_mode_switch = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Label("Live"), width="auto"),  # Positionne "Basique" à gauche
                dbc.Col(dbc.Switch(id="test-mode-switch", value=False, className="d-inline-block ms-1", persistence=True), width="auto"),
                dbc.Col(html.Label("Analyse"), width="auto"),  # Positionne "Avancé" à droite
            ],
            className="align-items-center",  # Centre les éléments verticalement dans la ligne
        ),
    ],
    style={"position": "absolute", "top": "50px", "left": "200px", "fontSize": "22px"}  # Ajoutez cette ligne pour définir la taille du texte du bouton
)


fig = run_strategy(8)
fig2 = run_strategy(2)

### LES BOUTONS ###
trade_button = dbc.Button("Lancer les trades", id="trade-button", n_clicks=0, className="btn btn-primary")
stop_trade_button = dbc.Button("Stopper les trades", id="stop-trade-button", n_clicks=0, className="btn btn-secondary")


pair = dcc.Dropdown(
                    options=[
                        {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                        {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                        {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                            ],value='BTC/USDT',id='pair-dropdown'
                    )

strat = dcc.Dropdown(
                    options=[
                        {'label': 'Stratégie 1', 'value': 'Stratégie 1'},
                        {'label': 'Stratégie 2', 'value': 'Stratégie 2'},
                        {'label': 'Stratégie 3', 'value': 'Stratégie 3'},
                            ],value='Stratégie 1',id='strat-dropdown'
                    )

# Utilisez dbc.Row et dbc.Col pour organiser les éléments
app.layout = dbc.Container(
    [
        html.Div(["DASHBOARD TRADING"], className="bg-primary text-white h3 p-2"),
        dbc.Row(
            [
                dbc.Col(color_mode_switch, width=2),  # Replace with actual content
                dbc.Col(test_mode_switch, width=2),  # Replace with actual content
            ]
        ),
        dbc.Container( # PARTIE ANALYSE
            [
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id="graph", figure=fig, className="border"), width=8),
                    ]
                ),dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id="graph2", figure=fig2, className="border"), width=8),
                    ]
                )
            ],
            className="mt-4",id="Analyse",  # Adjust margin-top as necessary
        ),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(pair, style={"position": "absolute", "top": "200px", "left": "500px"}, width=2),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(strat, style={"position": "absolute", "top": "300px", "left": "500px"}, width=2),
                    ],
                )
            ],
        ),
        dbc.Container(
            [
                html.Div([trade_button], style={"position": "absolute", "top": "250px", "left": "300px"}),
                html.Div([stop_trade_button], style={"position": "absolute", "top": "350px", "left": "300px"}),
            ]
        ),
    ]
)
        

@callback(
    Output("graph", "figure"),
    Input("color-mode-switch", "value"),
    allow_duplicate=True,
)
def update_figure_template(switch_on):
    # Mettez à jour le modèle de thème pour Plotly Express
    template = "minty" if switch_on else "minty_dark"
    fig.update_layout(template=template)

    return fig

@callback(
    Output("Analyse", "style"),
    Output("trade-button", "style"),
    Output("stop-trade-button", "style"),
    Output("pair-dropdown", "style"),
    Output("strat-dropdown", "style"),
    Input("test-mode-switch", "value"),
    allow_duplicate=True,
)
def hide_graph(switch_value):
    if switch_value:
        # If the switch is on, show the graph and the button
        return {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}
    else:
        # If the switch is off, hide the graph and the button
        return {"display": "none"}, {"display": "block"}, {"display": "block"}, {"display": "block"}, {"display": "block"}


clientside_callback(
    """
    (switchOn) => {
       switchOn
         ? document.documentElement.setAttribute('data-bs-theme', 'light')
         : document.documentElement.setAttribute('data-bs-theme', 'dark')
       return window.dash_clientside.no_update
    }
    """,
    Output("color-mode-switch", "id"),
    Input("color-mode-switch", "value"),
)
print("test")

if __name__ == "__main__":
    app.run_server(debug=True)
