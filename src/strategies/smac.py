"""
Trading strategy based on Simple Moving Average Crossover model

Objective:
    Capture market trends (momentum)

Intended trading frequency: daily

Steps:
    1. Calculate a long-term SMA and a short-term SMA
    2. Buy when short-term SMA crosses above long-term SMA
    3. Sell when short-term SMA crosses below long-term SMA
"""
import pandas as pd

from .strategy import Strategy

class SMAC(Strategy):
    def __init__(
        self,
        short_window: int,
        long_window: int,
        enable_shorting: bool=False
    ):
        """Initializes the SMAC strategy

        Args:
            short_window (int): window size for short-term SMAC
            long_window (int): window size for long-term SMAC
            enable_shorting (bool, optional): enable shorting stocks. Defaults to False.
        """
        self.short_window = short_window
        self.long_window = long_window
        self.enable_shorting = enable_shorting
    
    def generate_portfolio(self, _):
        raise NotImplementedError('This is a trading strategy. Use generate_signals() instead.')
    
    def generate_signals(self, data: pd.Series) -> pd.Series:
        """Generates trading signals for each stock based on the SMAC strategy

        Args:
            data (pd.Series): historical price data of stocks

        Returns:
            pd.Series: signals for each stock
        """
        signals = pd.Series(0, index=data.index)
        
        short_sma = data.rolling(window=self.short_window).mean()
        long_sma = data.rolling(window=self.long_window).mean()
        
        # buy when short SMA is greater than long SMA
        signals[short_sma > long_sma] = 1
        
        # short if short SMA is less than long SMA and shorting is enabled
        if self.enable_shorting:
            signals[short_sma < long_sma] = -1
        # else, exit positions when short SMA is less than long SMA
        else:
            signals[short_sma < long_sma] = 0
    
        return signals