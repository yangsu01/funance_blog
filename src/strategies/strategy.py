from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    @abstractmethod
    def generate_portfolio(self, data: pd.DataFrame) -> dict:
        """ Generates a portfolio with tickers and weights based on the strategy

        Args:
            data (pd.DataFrame): historical data of stocks for fitting

        Returns:
            dict: {ticker: weight} for each stock in the portfolio
        """
        raise NotImplementedError
    
    @abstractmethod
    def generate_signals(self, data: pd.Series) -> pd.Series:
        """ Generates trading signals for a stock based on the strategy
            1: long, -1: short, 0: exit, 2: hold

        Args:
            data (pd.Series): historical data of stock for generating signals

        Returns:
            pd.Series: signals for the stock
        """
        raise NotImplementedError