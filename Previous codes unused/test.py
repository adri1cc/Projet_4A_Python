from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt

class MovingAverageCrossStrategy(bt.Strategy):
    params = (
        ("short_period", 2),
        ("long_period", 8),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_period
        )

        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            # L'ordre a été exécuté
            print(
                f"Order {'Buy' if order.isbuy() else 'Sell'} "
                f"executed at {order.executed.price:.2f}, "
                f"Cost: {order.executed.value:.2f}, "
                f"Commission: {order.executed.comm:.2f}"
            )

    def next(self):
        if self.crossover > 0:
            # Signal d'achat : croisement de la moyenne mobile courte au-dessus de la moyenne mobile longue
            self.buy()

        elif self.crossover < 0:
            # Signal de vente : croisement de la moyenne mobile courte en dessous de la moyenne mobile longue
            self.sell()

def run_backtest():
    # Téléchargez les données depuis Yahoo Finance
    data = yf.download('BTC-USD', '2021-01-01', '2021-04-01', auto_adjust=True)

    # Créez un objet PandasData avec les données téléchargées
    data = bt.feeds.PandasData(dataname=data)

    # Configurer le moteur Backtrader
    cerebro = bt.Cerebro()

    # Ajoutez les données et la stratégie
    cerebro.adddata(data)
    cerebro.addstrategy(MovingAverageCrossStrategy)

    # Paramètres du broker
    cerebro.broker.set_cash(100)
    start_portfolio_value = cerebro.broker.getvalue()
    cerebro.addsizer(bt.sizers.SizerFix, stake=1)

    # Exécutez le backtest
    cerebro.run()

    end_portfolio_value = cerebro.broker.getvalue()
    pnl = end_portfolio_value - start_portfolio_value
    print(f'Starting Portfolio Value: {start_portfolio_value:.2f}')
    print(f'Final Portfolio Value: {end_portfolio_value:.2f}')
    print(f'PnL: {pnl:.2f}')
    # Affichez les résultats
    cerebro.plot()

    for strategy in cerebro.runstrats:
        # Vérifiez si c'est une liste
        if isinstance(strategy, list):
            for sub_strategy in strategy:
                plot_custom_chart(sub_strategy.orders_info)
        else:
            # Sinon, c'est une seule stratégie
            plot_custom_chart(strategy.orders_info)

def plot_custom_chart(orders_info):
    # Extraire les informations sur les ordres
    buy_points = [order['price'] for order in orders_info if order['action'] == 'Buy']
    sell_points = [order['price'] for order in orders_info if order['action'] == 'Sell']

    # Créer un graphique avec Matplotlib
    plt.figure(figsize=(10, 6))
    plt.plot(buy_points, 'go', label='Buy')
    plt.plot(sell_points, 'ro', label='Sell')
    plt.title('Custom Chart - Buy and Sell Points')
    plt.xlabel('Bar Index')
    plt.ylabel('Price')
    plt.legend()
    plt.show()
if __name__ == '__main__':
    run_backtest()
