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
from typing import Tuple

from .strategy import Strategy

class EWMAC(Strategy):
    def __init__(
        self,
        data: pd.DataFrame,
        short_window: int,
        long_window: int,
        enable_shorting: bool=False
    ):
        """Initializes the EWMAC strategy

        Args:
            data (pd.DataFrame): historical price data of stocks
            short_window (int): window size for short-term EWMAC
            long_window (int): window size for long-term EWMAC
            enable_shorting (bool, optional): enable shorting stocks. Defaults to False.
        """
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.enable_shorting = enable_shorting
    
    def generate_portfolio(self, _):
        raise NotImplementedError('This is a trading strategy. Use generate_signals instead.')
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generates trading signals for each stock based on the EWMAC strategy

        Args:
            data (pd.DataFrame): historical price data of stocks

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: signals and weights for each stock
        """
        signals = pd.DataFrame(index=data.index, columns=data.columns)
        weights = pd.DataFrame(index=data.index, columns=data.columns)
        
        for ticker in data.columns:
            short_ewmac = data[ticker].ewm(span=self.short_window, adjust=False).mean()
            long_ewmac = data[ticker].ewm(span=self.long_window, adjust=False).mean()
            
            ticker_signals = []
            for short, long in zip(short_ewmac, long_ewmac):
                if short > long:
                    ticker_signals.append(1)
                elif short < long and self.enable_shorting:
                    ticker_signals.append(-1)
                elif short < long and not self.enable_shorting:
                    ticker_signals.append(0)
                else:
                    ticker_signals.append(2)
            
            signals[ticker] = ticker_signals
            weights[ticker] = 1/len(data.columns) # assume equal weights if multiple stocks
        
        return signals, weights
