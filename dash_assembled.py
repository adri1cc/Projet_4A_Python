from dash import Dash, html, dcc, Input, Output, Patch, clientside_callback, callback, State
import plotly.express as px
import plotly.io as pio
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from backtest import *
from dash.exceptions import PreventUpdate
import api
#from strat_live import *


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

### LES FIGURES ###
fig = go.Figure()
fig_graph = go.Figure()


### LES BOUTONS ###
trade_button = dbc.Button("Lancer le bot", id="trade-button", n_clicks=0, color="primary",size="lg")
stop_trade_button = dbc.Button("Stopper le bot", id="stop-trade-button", n_clicks=0, color="secondary",size="lg")
previous_state = {'trade': 0, 'stop': 0}
backtest_button = dbc.Button("Voir le backtest", id="backtest-button", n_clicks=0, color="primary",size="lg")
wallet_button =  dbc.Button("Afficher portefeuille", id="wallet-button", n_clicks=0, color="success",size="lg")

### LES LISTES DEROULANTES ###

pair = dcc.Dropdown(
                    options=[
                        {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                        {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                        {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                            ],value='Paire',id='pair-dropdown',
                    )

strat = dcc.Dropdown(
                    options=[
                        {'label': 'Stratégie 1', 'value': 'Stratégie 1'},
                        {'label': 'Stratégie 2', 'value': 'Stratégie 2'},
                        {'label': 'Stratégie 3', 'value': 'Stratégie 3'},
                            ],value='Stratégie',id='strat-dropdown',
                    )
pair_backtest = dcc.Dropdown(
                    options=[
                        {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                        {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                        {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                            ],value='BTC/USDT',id='pair-backtest-dropdown',
                    )

strat_backtest = dcc.Dropdown(
                    options=[
                        {'label': 'SimpleSMA', 'value': 'SimpleSMA'},
                        {'label': 'Stratégie 2', 'value': 'Stratégie 2'},
                        {'label': 'Stratégie 3', 'value': 'Stratégie 3'},
                            ],value='Stratégie',id='strat-backtest-dropdown',
                    )

selected_message = html.Div(id='selected-message', style={"position": "absolute", "top": "250px", "left": "500px"})
message_bis = html.Div(id='message-bis', children='En attente', style={"position": "absolute", "top": "300px", "left": "500px"})

#trading_logic = create_trading_logic()

# Utilisez dbc.Row et dbc.Col pour organiser les éléments
app.layout = dbc.Container(
    [
        html.Div(["DASHBOARD TRADING"], className="bg-primary text-white h3 p-2",),
        dbc.Row(
            [
                dbc.Col(color_mode_switch, width=2),  # Replace with actual content
                dbc.Col(test_mode_switch, width=2),  # Replace with actual content
            ],
        ),
        dbc.Container(
            [
                 dbc.Col(
                            [
                                dcc.Graph(id="graph-wallet", figure=fig_graph, className="border"),
                            ],
                            width=10,
                            style={"position": "relative", "top": "500px", "left": "100px"},
                        ),
            ]
        ),
        dbc.Container( # PARTIE ANALYSE
            [
                dbc.Row(
                    [
                        dbc.Col([
                            html.Div([backtest_button], style={"position": "absolute", "top": "100px", "left": "120px"},className="d-grid gap-2 d-md-block",)

                            ]),
                            
                        dbc.Col(pair_backtest, style={"position": "absolute", "top": "200px", "left": "100px"}, width=2),
                        dbc.Col(strat_backtest, style={"position": "absolute", "top": "300px", "left": "100px"}, width=2),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(id="graph", figure=fig, className="border"),
                                dcc.Slider(id='slider',min=2,max=50,step=1,value=25,tooltip={'placement': 'bottom', 'always_visible': True})
                            ],
                            width=10,
                            style={"position": "relative", "left": "250px"},
                        ),
                        # dbc.Col(dcc.Graph(id="graph2", figure=fig2, className="border"), width=7, style={"position": "relative", "left": "500px"}),

                    ]
                ),
            ],
            className="mt-4",id="Analyse",  # Adjust margin-top as necessary
        ),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(pair, style={"position": "absolute", "top": "200px", "left": "500px"}, width=2),
                        dbc.Col(strat, style={"position": "absolute", "top": "200px", "left": "900px"}, width=2),
                    ]
                ),
                dbc.Row(
                    [
                        selected_message,
                        message_bis,
                    ],
                ),
            ],id="Live1",
        ),
        dbc.Container(
            [
                html.Div([trade_button], style={"position": "absolute", "top": "250px", "left": "250px"},
    className="d-grid gap-2 d-md-block",),
                html.Div([stop_trade_button], style={"position": "absolute", "top": "350px", "left": "250px"},
    className="d-grid gap-2 d-md-block",),
                html.Div([wallet_button], style={"position": "absolute", "top": "450px", "left": "250px"},
    className="d-grid gap-2 d-md-block",),
            ],id="Live2",
        ),
    ]
)
# Définir la fonction de callback
@app.callback(
    Output('message-bis', 'children'),
    [Input('trade-button', 'n_clicks'),
     Input('stop-trade-button', 'n_clicks')],
    [State('message-bis', 'children'),]
)
def trade(n_clicks_trade, n_clicks_stop, previous_message):
    if n_clicks_trade is not None and n_clicks_trade > previous_state['trade']:
        previous_state['trade'] = n_clicks_trade
        trading_logic['stop_flag'] = False
        start_trade(trading_logic)
        return 'Trade started'
    elif n_clicks_stop is not None and n_clicks_stop > previous_state['stop']:
        previous_state['stop'] = n_clicks_stop
        stop_trade(trading_logic)
        return 'Trade stopped'
    else:
        # No button clicks
        return previous_message
    
@app.callback(
    Output("graph-wallet", "figure"),
    [Input('wallet-button', 'n_clicks')]
)
def print_wallet(n_clicks):
    if n_clicks is not None:
        def plotAccountInfo(df_account):
            fig = px.bar(df_account, x='Currency', y='Total', title='Account Balance by Currency')
            return fig
        #return str(api.getInfoAccount())
        df_account = api.getInfoAccount()
        fig_graph = plotAccountInfo(df_account)
        return fig_graph
    
@callback( #Output("graph2", "figure")
    [Output("graph", "figure"),
     ],
    [Input("color-mode-switch", "value"),
     Input('strat-backtest-dropdown', 'value'), # if value == SimpleSMA... else if value == ...
     Input('pair-backtest-dropdown', 'value'),
     Input("backtest-button", "n_clicks"),
     Input('slider', 'value')],
    allow_duplicate=True
)
def update_figures(switch_on, selected_strat, selected_pair, n_clicks, slider_value):
    global fig # Utilisez global pour mettre à jour ces variables globales
    if n_clicks > 0:
        # Assurez-vous que votre fonction run_strategy renvoie une figure Plotly
        fig = run_SimpleSMA(slider_value, selected_pair)
        
    # Mettez à jour le modèle de thème pour Plotly Express
    template = "minty" if switch_on else "minty_dark"
    fig.update_layout(template=template)
    # fig2.update_layout(template=template)

    return [fig] #,fig2

@callback(
    Output("Analyse", "style"),
    Output("Live1", "style"),
    Output("Live2", "style"),
    Input("test-mode-switch", "value"),
    allow_duplicate=True,
)
def hide_graph(switch_value):
    if switch_value:
        # If the switch is on, show the graph and the button
        return {"display": "block"}, {"display": "none"}, {"display": "none"}
    else:
        # If the switch is off, hide the graph and the button
        return {"display": "none"}, {"display": "block"}, {"display": "block"}

@callback(
    Output('selected-message', 'children'),
    Input('strat-dropdown', 'value'),
    Input('pair-dropdown', 'value'),
)
def update_selected_message(selected_strat, selected_pair):
    return f"Vous avez choisi la stratégie {selected_strat} sur la paire {selected_pair}."


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
