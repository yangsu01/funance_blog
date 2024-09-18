"""
Trading strategy based on Exponential Weighted Moving Average Crossover model

Objective:
    Capture market trends (momentum) while putting more weight on recent data

Intended trading frequency: 1 day

Steps:
    1. Calculate a long-term EWMAC and a short-term EWMAC
    2. Buy when short-term EWMAC crosses above long-term EWMAC
    3. Sell when short-term EWMAC crosses below long-term EWMAC
"""
import pandas as pd

from .strategy import Strategy

class EWMAC(Strategy):
    def __init__(
        self,
        short_window: int,
        long_window: int,
        enable_shorting: bool=False
    ):
        """Initializes the EWMAC strategy

        Args:
            short_window (int): window size for short-term EWMAC
            long_window (int): window size for long-term EWMAC
            enable_shorting (bool, optional): enable shorting stocks. Defaults to False.
        """
        self.short_window = short_window
        self.long_window = long_window
        self.enable_shorting = enable_shorting
    
    def generate_portfolio(self, _):
        raise NotImplementedError('This is a trading strategy. Use generate_signals instead.')
    
    def generate_signals(self, data: pd.Series) -> pd.Series:
        """Generates trading signals for each stock based on the EWMAC strategy

        Args:
            data (pd.Series): historical price data of stocks

        Returns:
            pd.Series: trading signals
        """
        signals = pd.Series(0, index=data.index)
        
        short_ewmac = data.ewm(span=self.short_window, adjust=False).mean()
        long_ewmac = data.ewm(span=self.long_window, adjust=False).mean()
        
        # buy when short SMA is greater than long SMA
        signals[short_ewmac > long_ewmac] = 1
        
        # short if short SMA is less than long SMA and shorting is enabled
        if self.enable_shorting:
            signals[short_ewmac < long_ewmac] = -1
        # else, exit positions when short SMA is less than long SMA
        else:
            signals[short_ewmac < long_ewmac] = 0
        
        return signals
