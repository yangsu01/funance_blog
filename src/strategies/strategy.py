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
        pass