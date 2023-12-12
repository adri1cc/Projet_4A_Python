from pyalgotrade import barfeed
from pyalgotrade import bar

class DataFrameBarFeed(barfeed.BaseBarFeed):
    """
    Expects a pandas dataframe in the following format:
    Open, High, Low, Close in that order as float64
    datetime64[ns] as dataframe index,
    check dataframe with df.dtypes.
    """
    def __init__(self, dataframe, instrument, frequency):
        super(DataFrameBarFeed, self).__init__(frequency)
        self.registerInstrument(instrument)
        #make a list of lists containing all information for fast iteration
        self.__df = dataframe.values.tolist()
        self.__instrument = instrument
        self.__next = 0
        self.__len = len(self.__df)

    
    def setUseAdjustedValues(self, useAdjusted):
        #does this have a function? I still have to use adjusted closes below twice
        return False
    
    def reset(self):
        super(DataFrameBarFeed, self).reset()
        self.__next = 0

    def peekDateTime(self):
        return self.getCurrentDateTime()

    def getCurrentDateTime(self):
        if not self.eof():
            rowkey = self.__df[self.__next][5]
            #rowkey does not need to call todatetime, it should already be in that format
        else :
            rowkey = []
        return rowkey

    def barsHaveAdjClose(self):
        return False

    def getNextBars(self):
        ret = None
        if not self.eof():
            # Convert the list of lists into a bar.BasicBar
            # iteration through list of lists is 4x faster then using a dataframe because
            # a lot of functions get called every iteration
            bar_dict = {
                self.__instrument: bar.BasicBar(
                    self.__df[self.__next][5],
                    self.__df[self.__next][0],
                    self.__df[self.__next][1],
                    self.__df[self.__next][2],
                    self.__df[self.__next][3],
                    self.__df[self.__next][4],
                    #is there another class I can use besides BasicBar that does 
                    #not need an adjusted close(i.e. forex)?
                    #unused data will slow down the script
                    #dirty fix: use close as adjusted close
                    self.__df[self.__next][3],
                    self.getFrequency()
                )
            }
            ret = bar.Bars(bar_dict)
            self.__next += 1
        return ret

    def eof(self):
        #any particular reason to not get len() upon init? 
        #would prob. be faster for multiple requests, about -7ms
        return self.__next >= self.__len

    def start(self):
        pass

    def stop(self):
        pass

    def join(self):
        pass