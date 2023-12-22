"""
This script contains the code for a trading dashboard using Dash.
"""

from datetime import datetime
import os

import logging
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, clientside_callback, callback, State
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate

import api
from strat_live import start_trade, create_trading_logic, backtest, stop_trade, get_investment

log_file = os.path.join(os.getcwd(), 'app.log')
max_lines = 10

# Configure logging
logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
# Load templates for Plotly figures
load_figure_template(["minty", "minty_dark"])

# Sample data for the dashboard
df = px.data.gapminder()

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME])

# UI elements definition
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

logs_switch = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Label("Logs"), width="auto"),  # Positionne "Basique" à gauche
                dbc.Col(dbc.Switch(id="logs-switch", value=False, className="d-inline-block ms-1", persistence=True), width="auto"),
            ],
            className="align-items-center",  # Centre les éléments verticalement dans la ligne
        ),
    ],
    style={"position": "absolute", "top": "50px", "right": "200px", "fontSize": "22px"}  # Ajoutez cette ligne pour définir la taille du texte du bouton
)
### LES FIGURES ###
fig = go.Figure()
fig_graph = go.Figure()


### LES BOUTONS ###
trade_button = dbc.Button("Lancer le bot", id="trade-button", n_clicks=0, color="primary", size="lg")
stop_trade_button = dbc.Button("Stopper le bot", id="stop-trade-button", n_clicks=0, color="secondary", size="lg")
wallet_button = dbc.Button("Afficher portefeuille", id="wallet-button", n_clicks=0, color="primary", size="lg")
previous_state = {'trade': 0, 'stop': 0}
backtest_button = dbc.Button("Voir le backtest", id="backtest-button", n_clicks=0, color="primary", size="lg")
previous_backtest_button = {'backtest_buton': 0}
previous_wallet_button = {'wallet_buton': 0}

### LES LISTES DEROULANTES ###

pair = dcc.Dropdown(
                    options=[
                        {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                        {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                        {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                            ],value='BTC/USDT',id='pair-dropdown',style={'color': 'black'}
                    )

strat = dcc.Dropdown(
                    options=[
                        {'label': 'SimpleSMA', 'value': 'SimpleSMA'},
                        {'label': 'RSI', 'value': 'RSI'},
                        {'label': 'Stratégie 3', 'value': 'Stratégie 3'},
                            ],value='SimpleSMA',id='strat-dropdown',style={'color': 'black'}
                    )
pair_backtest = dcc.Dropdown(
                    options=[
                        {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                        {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                        {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                            ],value='BTC/USDT',id='pair-backtest-dropdown',style={'color': 'black'}
                    )

strat_backtest = dcc.Dropdown(
                    options=[
                        {'label': 'SimpleSMA', 'value': 'SimpleSMA'},
                        {'label': 'RSI', 'value': 'RSI'},
                        {'label': 'Stratégie 3', 'value': 'Stratégie 3'},
                            ],value='SimpleSMA',id='strat-backtest-dropdown',style={'color': 'black'}
                    )

selected_message = html.Div(id='selected-message')
message_bis = html.Div(id='message-bis', children='En attente')#TODO crtl F explicit name
percentage_message = html.Div(id= 'percentage-message')
date = '2022-06-11 00:00:00'
trading_logic = create_trading_logic()

# Utilisez dbc.Row et dbc.Col pour organiser les éléments
app.layout = dbc.Container(
    [
        html.Div(["DASHBOARD TRADING"], className="bg-primary text-white h3 p-2",),
        dbc.Row(
            [
                dbc.Col(color_mode_switch, width=2),  # Replace with actual content
                dbc.Col(test_mode_switch, width=2),  # Replace with actual content
                dbc.Col(logs_switch, width=2),
            ],
        ),
        dbc.Container([
            dbc.Col([html.Div([
                                    dcc.Interval(
                                        id='interval-component',
                                        interval=0.5 * 1000,  # in milliseconds
                                        n_intervals=0
                                    ),
                                    dcc.Textarea(id='log-output', style={"width": "100%", "height": "200px"}),
                                ])
                ])
        ],id = "logs", fluid = True
        ),
        dbc.Container( # ANALYSIS PART
            [
                dbc.Col(
                    [
                        dbc.Row([
                            html.Div([backtest_button], style={"position": "relative", "top": "100px"}, className="d-grid gap-2 d-md-block",)

                            ]),

                        dbc.Row(dbc.Col(pair_backtest, style={"position": "relative", "top": "200px"}, width=2)),
                        dbc.Row(dbc.Col(strat_backtest, style={"position": "relative", "top": "250px"}, width=2)),
                        dbc.Col(
                            [
                                html.Label('Entrez une date (format : YYYY-MM-DD HH:MM:SS) :'),
                                dbc.Row(
                                    [
                                        dbc.Col(dcc.Input(id='input-date', type='text')),
                                        dbc.Col(html.Div(id='output-date')),
                                    ]
                                )
                            ],
                            style={"position": "relative", "top": "300px"},
                            width=2,
                        )

                    ], style={"position": "relative", "left": "0px"}
                ),
                dbc.Col(
                    [
                                dcc.Graph(id="graph", figure=fig, className="border"),
                                dcc.Slider(id='slider', min=2, max=50, step=1, value=25, tooltip={'placement': 'bottom', 'always_visible': True})
                            ],
                            width=10,
                            style={"position": "relative", "left": "200px", "top": "-100px"},
                        ),
                        # dbc.Col(dcc.Graph(id="graph2", figure=fig2, className="border"), width=7, style={"position": "relative", "left": "500px"}),
            ],
            className="mt-4", id="Analyse",style={"position": "relative", "left": "00px", "top": "-100px"}  # Adjust margin-top as necessary
        ),
        dbc.Container( #PARTIE LIVE
            [   

                dbc.Row(
                    [
                        dbc.Col(pair, style={"position": "relative", "top": "100px", "left": "500px"}, width=2),
                        dbc.Col(strat, style={"position": "relative", "top": "100px", "left": "600px"}, width=2),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Row(selected_message),
                        dbc.Row(message_bis),
                    ],style={"position": "relative", "top": "0px", "left": "500px"}, width=10
                ),
                dbc.Col(
                    [
                        dbc.Row(percentage_message,style={"position": "relative", "top": "0px", "left": "20px"}),
                        dcc.Slider(id='slider-wallet',min=5,max=100,step=5,value=5,tooltip={'placement': 'bottom', 'always_visible': True})
                    ],
                    width=10,
                    style={"position": "relative", "top": "0px", "left": "00px", 'width': '400px'},
                ),
                dbc.Row(
                        [
                            html.Div([trade_button], style={"position": "relative", "top": "25px"},
                className="d-grid gap-2 d-md-block",),
                            html.Div([stop_trade_button], style={"position": "relative", "top": "75px"},
                className="d-grid gap-2 d-md-block",),
                            html.Div([wallet_button], style={"position": "relative", "top": "125px"},
                className="d-grid gap-2 d-md-block",),
                        ]
                    ),
                dbc.Col(
                            [
                                dcc.Graph(id="graph-wallet", figure=fig_graph, className="border", style= {"display": "none", "position": "relative", "top": "90px", "left": "100px"})
                            ],
                            width=8,
                            style={"position": "relative", "top": "0px", "left": "500px"},
                        ),
                
            ],id="Live1",
        ),

    ],fluid=True
)
# Définir la fonction de callback
@app.callback(dash.dependencies.Output('log-output', 'value'),
              dash.dependencies.Input('interval-component', 'n_intervals'))
def update_logs(n):
    global log_file
    max_lines = 7  # Nombre maximal de lignes à afficher

    # Lisez les messages de journal depuis le fichier ou toute autre source
    with open(log_file, 'r') as log_file_handle:
        logs = log_file_handle.readlines()

    # Affichez les dernières lignes jusqu'au nombre maximal défini
    display_logs = logs[-max_lines:]

    # Retournez les messages de journal pour les afficher
    return ''.join(display_logs)


@app.callback(
    Output('message-bis', 'children'),
    [Input('trade-button', 'n_clicks'),
     Input('stop-trade-button', 'n_clicks'),
     Input('strat-dropdown', 'value'),
     Input('pair-dropdown', 'value'),
     Input('slider-wallet','value'),],
    [State('message-bis', 'children')]
)
def trade(n_clicks_trade, n_clicks_stop, strat_live, pair_live, percentage, previous_message):
    """
    Callback to handle starting and stopping trades.
    """
    if n_clicks_trade is not None and n_clicks_trade > previous_state['trade']:
        previous_state['trade'] = n_clicks_trade
        trading_logic['stop_flag'] = False
        start_trade(trading_logic, "5m", pair_live, strat_live, percentage)
        return 'Trade started'# TODO resolve print
    elif n_clicks_stop is not None and n_clicks_stop > previous_state['stop']:
        previous_state['stop'] = n_clicks_stop
        stop_trade(trading_logic)
        return 'Trade stopped'
    else:
        # No button clicks
        return previous_message
@app.callback(
    dash.dependencies.Output('output-date', 'children'),
    [dash.dependencies.Input('input-date', 'value')]
)
def update_output(value):
    global date
    if not value:
        raise PreventUpdate  # Ne rien faire si la valeur est vide

    try:
        # Tentez de convertir la valeur en objet datetime
        datetime_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        date = str(datetime_obj)
        logging.info(date)
        logging.info(type(date))
        return 'Vous avez saisi une date valide : {}'.format(datetime_obj.strftime('%Y-%m-%d %H:%M:%S'))
    except ValueError:
        return 'Format de date invalide. Entrez une date au format YYYY-MM-DD HH:MM:SS.'

# Separate callback for color switch
@app.callback(
    Output("graph-wallet", "style"),
    Input('wallet-button', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_graph_visibility(n_clicks):
    style = {"display": "block" if n_clicks % 2 == 1 else "none"}
    return style

@callback( #Output("graph2", "figure")
    [Output("graph", "figure"),
     Output("graph-wallet", "figure")],
    [Input("color-mode-switch", "value"),
     Input('strat-backtest-dropdown', 'value'),
     Input('pair-backtest-dropdown', 'value'),
     Input("backtest-button", "n_clicks"),
     Input('slider', 'value'),
     Input('wallet-button', 'n_clicks'),
     Input("graph-wallet", "style")],
    allow_duplicate=True
)
def update_figures(switch_on, selected_strat, selected_pair, n_clicks_backtest, slider_value, n_clicks_wallet, wallet_style):
    """
    Callback to update figures based on selected parameters.
    """
    global date
    global fig # Use global to update these global variables
    global fig_graph
    if n_clicks_backtest is not None and n_clicks_backtest > previous_backtest_button['backtest_buton']:
        previous_backtest_button['backtest_buton'] = n_clicks_backtest
        # Make sure your run_strategy function returns a Plotly figure
        # fig = run_SimpleSMA(slider_value, selected_pair)
        fig = backtest(slider_value, "5m", selected_pair,selected_strat,date)
    # Update the theme template for Plotly Express
    if n_clicks_wallet is not None and wallet_style["display"] == "block":
        previous_wallet_button['wallet_buton'] = n_clicks_wallet
        df_account = api.get_info_account()
        fig_graph = api.plot_info_account(df_account)

    template = "minty" if switch_on else "minty_dark"
    fig.update_layout(template=template)
    fig_graph.update_layout(template=template)

    return fig, fig_graph #,fig2

@app.callback(
    [Output("Analyse", "style"),
     Output("Live1", "style"),
     Output("logs", "style")],
    [Input("test-mode-switch", "value"),
     Input("logs-switch", "value")],
    allow_duplicate=True,
)
def update_page_logs(switch_value, logs_button):
    """
    Callback to dynamically adjust the layout based on the test mode and logs visibility.
    """
    logs_style = {"display": "none"}
    analyse_top = "-100px" if logs_button else "0px"
    live_top = "0px" if logs_button else "0px"
    analyse_display = "block" if switch_value else "none"
    live_display = "block" if not switch_value else "none"

    if logs_button:  # Show logs
        logs_style = {"position": "relative", "top": "0px", "left": "0px", "width": "100%", "z-index": 1}

    live = {"display": live_display, "position": "relative", "top": live_top}
    analyse = {"display": analyse_display, "position": "relative", "top": analyse_top}

    return analyse, live, logs_style


@callback(
    Output('selected-message', 'children'),
    Input('strat-dropdown', 'value'),
    Input('pair-dropdown', 'value'), 
)
def update_selected_message(selected_strat, selected_pair):
    """
    Callback to update the message indicating the selected strategy and pair.
    """
    return f"Vous avez choisi la stratégie {selected_strat} sur la paire {selected_pair}."

@callback(
    Output('percentage-message', 'children'),
    Input('pair-dropdown', 'value'),
)
def update_percentage_message(selected_pair):
    return f"Quel risque pour {selected_pair} souhaitez-vous utiliser ?"

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

if __name__ == "__main__":
    app.run_server(debug=True)
