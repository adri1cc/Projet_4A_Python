from __future__ import annotations

from multiprocessing.sharedctypes import Value

import re
import numpy as np
import pandas as pd
from .utils import min_max_scaling, z_scaling, no_scaling
import talib
import pandas as pd
import numpy as np
import re
import logging
logger = logging.getLogger(__name__)


class UserStatsCalculator:
    def __init__(self):
        self.features_dict = {
            'deltaSma': self._compute_delta_sma,
            'ratioSma': self._compute_ratio_sma,
            'hourOtd': self._compute_hour,
            'candleBody': self._compute_candle_body,
            'upperWick': self._compute_upper_wick,
            'lowerWick': self._compute_lower_wick,
            'rsi': self._compute_rsi,
            'volatility': self._compute_volatility,
            'volumeSma': self._compute_volume_sma,
            'forceIndex': self._compute_force_index
        }

    def calculate(self, data, feature):

        parts = feature.split('_')
        
        # Base indicator name
        base_indicator = parts[0]  
        params = parts[1:]

        if base_indicator in self.features_dict:
            
            if base_indicator == 'deltaSma':
                return self._compute_delta_sma(data, params, feature)
                
            elif base_indicator == 'ratioSma':
                return self._compute_ratio_sma(data, params, feature)
                
            elif base_indicator == 'hourOtd':
                return self._compute_hour(data, params, feature)

            elif base_indicator == 'candleBody':
                return self._compute_candle_body(data, params, feature)
            
            elif base_indicator == 'upperWick':
                return self._compute_upper_wick(data, params, feature)
            
            elif base_indicator == 'lowerWick':
                return self._compute_lower_wick(data, params, feature)
            
            elif base_indicator == 'rsi':
                return self._compute_rsi(data, params, feature)
            
            elif base_indicator == 'volatility':
                return self._compute_volatility( data, params, feature)
            
            elif base_indicator == 'volumeSma':
                return self._compute_volume_sma(data, params, feature)
            
            elif base_indicator == 'forceIndex':
                return self._compute_force_index(data, params, feature)

        else:
            raise ValueError('Invalid indicator')

    def _compute_delta_sma(self, data, params, feature):
                
        if len(params) != 2:
            raise ValueError("delta_sma requires a long and a short window")
        shorter_window = int(params[0])
        longer_window = int(params[1])
        try:
            sma1 = data[f'close_{shorter_window}_sma']
        except KeyError:
            sma1 = data['close'].rolling(window=shorter_window).mean()
        try:
            sma2 = data[f'close_{longer_window}_sma']
        except KeyError:
            sma2 = data['close'].rolling(window=longer_window).mean()

        df = pd.DataFrame({'date': data['date'], 'deltaSma': sma1 - sma2})

        return df

    def _compute_ratio_sma(self, data, params, feature):
        short_period = params[0]
        long_period = params[1]
        
        short_ema = talib.EMA(data['close'].values, timeperiod=short_period)
        long_ema = talib.EMA(data['close'].values, timeperiod=long_period)
        
        ratio = short_ema / long_ema
        df = pd.DataFrame({'date': data['date'], 'ratioSma': ratio - 1})
        return df

    def _compute_hour(self, data, params, feature):
        hours = talib.FUNC_HOUR(data['date'].values)
        df = pd.DataFrame({'date': data['date'], 'hour': hours})
        return df

    def _compute_candle_body(self, data, params, feature):
        real_body = talib.REAL_BODY(data['open'].values, data['high'].values, data['low'].values, data['close'].values)
        df = pd.DataFrame({'date': data['date'], 'realBody': real_body})
        return df

    def _compute_upper_wick(self, data, params, feature):
        try:
            # Calculate upper wick
            upper_wick = talib.UPPER_WICK(
                data['open'].values,
                data['high'].values,
                data['low'].values,
                data['close'].values
            )

            # Create a DataFrame with the upper wick and date
            df = pd.DataFrame({
                'date': data['date'],
                'upperWick': upper_wick
            })

            return df

        except Exception as e:
            print(f"Error in _compute_upper_wick: {e}")
            return None

    def _compute_lower_wick(self, data, params, feature):
        try:
            # Calculate lower wick
            lower_wick = talib.LOWER_WICK(
                data['open'].values,
                data['high'].values,
                data['low'].values,
                data['close'].values
            )

            # Create a DataFrame with the lower wick and date
            df = pd.DataFrame({
                'date': data['date'],
                'lowerWick': lower_wick
            })

            return df

        except Exception as e:
            print(f"Error in _compute_lower_wick: {e}")
            return None

    def _compute_rsi(self, data, params, feature):
        try:
            # Calculate RSI
            rsi = talib.RSI(data['close'].values)

            # Create a DataFrame with the RSI and date
            df = pd.DataFrame({
                'date': data['date'],
                'rsi': rsi
            })

            return df

        except Exception as e:
            print(f"Error in _compute_rsi: {e}")
            return None

    def _compute_volatility(self, data, params, feature):
        try:
            # Calculate volatility
            data_float = data['close'].values.astype(np.float64)
            volatility = talib.STDDEV(data_float, timeperiod=20, nbdev=1)

            # Create a DataFrame with the volatility and date
            df = pd.DataFrame({
                'date': data['date'],
                'volatility': volatility
            })

            return df

        except Exception as e:
            print(f"Error in _compute_volatility: {e}")
            return None

    def _compute_volume_sma(self, data, params, feature):
        try:
            # Calculate volume SMA
            volume_sma = talib.SMA(data['volume'].values, timeperiod=30)

            # Create a DataFrame with the volume SMA and date
            df = pd.DataFrame({
                'date': data['date'],
                'volumeSma': volume_sma
            })

            return df

        except Exception as e:
            print(f"Error in _compute_volume_sma: {e}")
            return None

    def _compute_force_index(self, data, params, feature):
        try:
            # Calculate force index
            force_index = talib.OBV(data['close'].values, data['volume'].values)

            # Create a DataFrame with the force index and date
            df = pd.DataFrame({
                'date': data['date'],
                'forceIndex': force_index
            })

            return df

        except Exception as e:
            print(f"Error in _compute_force_index: {e}")
            return None
    

class FeatureEngineer:
    """ Provides methods for preprocessing the stock price data """

    def __init__(
        self,
        features,
    ):
        self.features = features
        self.user_stats_calculator = UserStatsCalculator()
        self.scaling_dict = {
            'minmax' : min_max_scaling,
            'z' : z_scaling,
            'no': no_scaling
        }

    def preprocess_data(self, data):
        """main method to do the feature engineering"""
        
        def _extract_numbers(s):
            nums = re.findall(r'\d+', s) 
            return [int(num) for num in nums]    
       
        lag = 1
        df = data.copy()
        features = self.features.copy()

        for feature, scaling in features:
            new_feature_df = pd.DataFrame()
            try:
                new_feature_df = self.user_stats_calculator.calculate(data, feature)
                scaling_func = self.scaling_dict[scaling]
                new_feature_df = scaling_func(new_feature_df, feature) 
                print(f"Successfully added {feature} to DataFrame")

                # Concaténer les DataFrames côte à côte
                combined_df = pd.concat([df,new_feature_df[1:]], axis=1)

                # Supprimer les colonnes en double
                combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

            except KeyError:
                print(f"{feature} not supported")
                continue
            df = combined_df

        # print(df)
        # Merge only if new_feature_df is not empty
        
        # df = df.merge(pd.DataFrame(new_feature_df), on="date", how="left")
        df = df.ffill().bfill()
        length = len(df) - lag
        print(df)
        return df.tail(length).reset_index(drop=True)
