import backtrader as bt
class MaCrossStrategy(bt.Strategy):
 
    params = (
        ('fast_length', 1),
        ('slow_length', 5),
        ("optimize", False),
    )
     
    def __init__(self):
        ma_fast = bt.ind.SMA(period = self.params.fast_length)
        ma_slow = bt.ind.SMA(period = self.params.slow_length)
         
        self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)
 
    def next(self):
        if not self.position:
            if self.crossover > 0: 
                self.buy()
        elif self.crossover < 0: 
            self.close()

class MAcrossover(bt.Strategy): 
    # Moving average parameters
    params = (('pfast',2),('pslow',5),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization

    def __init__(self):
        self.dataclose = self.datas[0].close
        
		# Order variable will contain ongoing order details/status
        self.order = None

        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
                        period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
                        period=self.params.pfast)
def next(self):
        
    self.log(f'Close: {self.dataclose[0]}, Fast SMA: {self.fast_sma[0]}, Slow SMA: {self.slow_sma[0]}')

    if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] <= self.slow_sma[-1]:
        # Buy signal
        self.log('BUY SIGNAL')
        self.buy()

    elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] >= self.slow_sma[-1]:
        # Sell signal
        self.log('SELL SIGNAL')
        self.sell()


