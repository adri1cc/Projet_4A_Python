"""
This script contains the code for a trading dashboard using Dash.
"""
# TODO Améliorer l'interface graphique
# TODO Débuger l'interafce graphique


from datetime import datetime
import os
import api
import logging
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, clientside_callback, callback, State
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate

from strategy_gestion import start_trade, create_trading_logic, backtest, stop_trade, get_investment

# Log file creation
log_file = os.path.join(os.getcwd(), 'app.log')

# Configure logging
logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
# Load templates for Plotly figures
load_figure_template(["minty", "minty_dark"])

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

live_analysis_switch = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Label("Live"), width="auto"),
                dbc.Col(dbc.Switch(id="live-analysis-switch", value=False, className="d-inline-block ms-1", persistence=True), width="auto"),
                dbc.Col(html.Label("Analysis"), width="auto"),
            ],
            className="align-items-center",
        ),
    ],
    style={"position": "absolute", "top": "50px", "left": "200px", "fontSize": "22px"}
)

logs_switch = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Label("Logs"), width="auto"),
                dbc.Col(dbc.Switch(id="logs-switch", value=False, className="d-inline-block ms-1", persistence=True), width="auto"),
            ],
            className="align-items-center",
        ),
    ],
    style={"position": "absolute", "top": "50px", "right": "200px", "fontSize": "22px"}
)

backtest_figure = go.Figure()
wallet_figure = go.Figure()

trade_button = dbc.Button("Start bot", id="trade-button", n_clicks=0, color="primary",size="lg")
stop_trade_button = dbc.Button("Stop bot", id="stop-trade-button", n_clicks=0, color="secondary",size="lg")
wallet_button = dbc.Button("Display portfolio", id="wallet-button", n_clicks=0, color="primary",size="lg")
previous_state = {'trade': 0, 'stop': 0}
backtest_button = dbc.Button("See backtest", id="backtest-button", n_clicks=0, color="primary",size="lg")
previous_backtest_button = {'backtest_buton': 0}
previous_wallet_button = {'wallet_buton': 0}

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
                        {'label': 'RSIStrategy', 'value': 'RSISrategy'},
                        {'label': 'MACD', 'value': 'MACD'},
                        {'label': 'SMA & RSI', 'value': 'SMA_RSI'},
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
                        {'label': 'RSIStrategy', 'value': 'RSIStrategy'},
                        {'label': 'MACD', 'value': 'MACD'},
                        {'label': 'SMA & RSI', 'value': 'SMA_RSI'},
                            ],value='SimpleSMA',id='strat-backtest-dropdown',style={'color': 'black'}
                    )

user_choice = html.Div(id='user-choice')
trading_status = html.Div(id='trading-status', children='Waiting')
percentage_message = html.Div(id='percentage-message')

# Default date
date = '2022-06-11 00:00:00'

# Initialization of trading logic : no live trade
trading_logic = create_trading_logic()

# Dash layout
app.layout = dbc.Container(
    [
        html.Div(["TRADING DASHBOARD"], className="bg-primary text-white h3 p-2",),
        dbc.Row(
            [
                dbc.Col(color_mode_switch, width=2),
                dbc.Col(live_analysis_switch, width=2),
                dbc.Col(logs_switch, width=2),
            ],
        ),
        dbc.Container([
            dbc.Col([html.Div([dcc.Interval(
                                        id='interval-component',
                                        interval=0.5*1000,  # in milliseconds
                                        n_intervals=0
                                    ),
                                    dcc.Textarea(id='log-output', style={"width": "100%", "height": "200px"}),
                                ])
                ])
        ],id = "logs", fluid = True
        ),
        # Analysis part
        dbc.Container(
            [
                dbc.Col(
                    [
                        dbc.Row([
                            html.Div([backtest_button], 
                                     style={"position": "relative", "top": "100px"}, 
                                     className="d-grid gap-2 d-md-block",)

                            ]),

                        dbc.Row(dbc.Col(pair_backtest, 
                                        style={"position": "relative", "top": "200px"}, width=2)),
                        dbc.Row(dbc.Col(strat_backtest, 
                                        style={"position": "relative", "top": "250px"}, width=2)),
                        dbc.Col(
                            [
                                html.Label('Enter a date (format : YYYY-MM-DD HH:MM:SS) :'),
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
                                dcc.Graph(id="backtest-figure", figure=backtest_figure, className="border"),
                                dcc.Slider(id='slider', min=2, max=50, step=1, value=25, 
                                           tooltip={'placement': 'bottom', 'always_visible': True})
                            ],
                            width=10,
                            style={"position": "relative", "left": "200px", "top": "-100px"},
                        ),
            ],
            className="mt-4", id="analysis",style={"position": "relative", "left": "00px", "top": "-100px"}
        ),
        # Live part
        dbc.Container(
            [   
                dbc.Row(
                    [
                        dbc.Col(pair, style={"position": "relative", "top": "100px", "left": "500px"}, width=2),
                        dbc.Col(strat, style={"position": "relative", "top": "100px", "left": "600px"}, width=2),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Row(user_choice),
                        dbc.Row(trading_status),
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
                                dcc.Graph(id="wallet-figure", figure=wallet_figure, className="border", style= {"display": "none", "position": "relative", "top": "90px", "left": "100px"})
                            ],
                            width=12,
                            style={"position": "relative", "top": "200px", "left": "100px"},
                        ),# TODO change position and size
            ],id="live",
        ),

    ],fluid=True
)

# Callbacks
@callback(
    Output('log-output', 'value'),
    Input('interval-component', 'n_intervals'))
def update_logs(n):
    """
    Callback to add or remove the logs window
    """
    global log_file
    # Max lines in the window
    max_lines = 7

    with open(log_file, 'r') as log_file_handle:
        logs = log_file_handle.readlines()

    display_logs = logs[-max_lines:]
    return ''.join(display_logs)

@callback(
    Output('trading-status', 'children'),
    [Input('trade-button', 'n_clicks'),
     Input('stop-trade-button', 'n_clicks'),
     Input('strat-dropdown', 'value'),
     Input('pair-dropdown', 'value'),
     Input('slider-wallet','value'),],
    [State('trading-status', 'children')]
)
def trade(n_clicks_trade, n_clicks_stop, strat_live, pair_live, percentage, previous_message):
    """
    Callback to handle starting and stopping trades.
    """
    if n_clicks_trade is not None and n_clicks_trade > previous_state['trade']:
        previous_state['trade'] = n_clicks_trade
        trading_logic['stop_flag'] = False
        start_trade(trading_logic, "5m", pair_live, strat_live, percentage)
        return 'Trade started'# TODO resolve return
    elif n_clicks_stop is not None and n_clicks_stop > previous_state['stop']:
        previous_state['stop'] = n_clicks_stop
        stop_trade(trading_logic)
        return 'Trade stopped'
    else:
        return previous_message
    
@callback(
    Output('output-date', 'children'),
    Input('input-date', 'value')
)
def update_output(value):
    """
    Callback to handle date.
    """
    global date

    if not value:
        raise PreventUpdate

    try:
        datetime_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        date = str(datetime_obj)
        logging.info(date)
        logging.info(type(date))
        return 'Valid format : {}'.format(datetime_obj.strftime('%Y-%m-%d %H:%M:%S'))
    except ValueError:
        return 'Invalid format. Enter a date with this format YYYY-MM-DD HH:MM:SS.'

@callback(
    Output("wallet-figure", "style"),
    Input('wallet-button', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_graph_visibility(n_clicks):
    """
    Callback to update the state of the wallet figure.
    """
    style = {"display": "block" if n_clicks % 2 == 1 else "none"}
    return style

@callback(
    [Output("backtest-figure", "figure"),
     Output("wallet-figure", "figure")],
    [Input("color-mode-switch", "value"),
     Input('strat-backtest-dropdown', 'value'),
     Input('pair-backtest-dropdown', 'value'),
     Input("backtest-button", "n_clicks"),
     Input('slider', 'value'),
     Input('wallet-button', 'n_clicks'),
     Input("wallet-figure", "style")],
    allow_duplicate=True
)
def update_figures(switch_on, selected_strat, selected_pair, n_clicks_backtest, slider_value, n_clicks_wallet, wallet_style):
    """
    Callback to update figures based on selected parameters.
    """
    global date
    global backtest_figure
    global wallet_figure

    if n_clicks_backtest is not None and n_clicks_backtest > previous_backtest_button['backtest_buton']:
        previous_backtest_button['backtest_buton'] = n_clicks_backtest
        backtest_figure = backtest(slider_value, "5m", selected_pair,selected_strat,date)
        
    if n_clicks_wallet is not None and wallet_style["display"] == "block":
        previous_wallet_button['wallet_buton'] = n_clicks_wallet
        df_account = api.get_info_account()
        wallet_figure = api.plot_info_account(df_account)

    template = "minty" if switch_on else "minty_dark"
    backtest_figure.update_layout(template=template)
    wallet_figure.update_layout(template=template)

    return backtest_figure, wallet_figure

@callback(
    [Output("analysis", "style"),
     Output("live", "style"),
     Output("logs", "style")],
    [Input("live-analysis-switch", "value"),
     Input("logs-switch", "value")],
    allow_duplicate=True,
)
def update_page_logs(switch_value, logs_button):
    """
    Callback to dynamically adjust the layout based on the test mode and logs visibility.
    """
    logs_style = {"display": "none"}
    analysis_top = "-100px" if logs_button else "0px"
    live_top = "0px" if logs_button else "0px"
    analysis_display = "block" if switch_value else "none"
    live_display = "block" if not switch_value else "none"

    if logs_button:
        logs_style = {"position": "relative", "top": "0px", "left": "0px", "width": "100%", "z-index": 1}

    live = {"display": live_display, "position": "relative", "top": live_top}
    analysis = {"display": analysis_display, "position": "relative", "top": analysis_top}

    return analysis, live, logs_style

@callback(
    Output('user-choice', 'children'),
    Input('strat-dropdown', 'value'),
    Input('pair-dropdown', 'value'), 
)
def update_user_choice(selected_strat, selected_pair):
    """
    Callback to update the message indicating the selected strategy and pair.
    """
    return f"You choose strategy {selected_strat} on {selected_pair}."

@callback(
    Output('percentage-message', 'children'),
    Input('pair-dropdown', 'value'),
)
def update_percentage_message(selected_pair):
    return f"What percentage of {selected_pair} do you want to use?"

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
