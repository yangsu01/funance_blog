import pandas as pd
import numpy as np
from scipy.stats import gmean

from ..strategies import Strategy
from ..utils import plot_time_series, plot_returns_distribution

class BacktestTrader:
    def __init__(
        self,
        strategy: Strategy,
        data: pd.Series,
        starting_cash: float=10000,
        transaction_fee: float=10,
        borrow_rate: float=0.02,
    ):
        """ Initializes a BacktestTrader object

        Args:
            strategy (Strategy): trading strategy to backtest
            data (pd.Series): historical price data of stock
            starting_cash (float, optional): starting cash for trading. Defaults to 10000.
            transaction_fee (float, optional): cost per transaction. Defaults to 10.
            borrow_rate (float, optional): annual rate for borrowing (shorting). Defaults to 0.02.
        """
        self.strategy = strategy
        self.data = data
        self.starting_cash = starting_cash
        self.transaction_fee = transaction_fee
        self.borrow_rate = borrow_rate
        self.portfolio_value = pd.Series(dtype=float)
        self.portfolio_returns = pd.Series(dtype=float)
    
    def run_backtest(self):
        signals = self.strategy.generate_signals(self.data)
        cash = self.starting_cash
        daily_borrow_rate = self.borrow_rate/252
        shares_held = 0
        portfolio_values = []
        
        for date in self.data.index:
            signal = signals.loc[date]
            price = self.data.loc[date]

            # update positions based on signals and weights
            if signal == 1:  # long
                if shares_held < 0:  # exit short positions
                    cash -= np.abs(shares_held)*price + self.transaction_fee
                    shares_held = 0
                
                if shares_held == 0:  # long if not already long
                    max_shares = int((cash-self.transaction_fee) / price)
                    cash -= max_shares*price + self.transaction_fee
                    shares_held = max_shares

            elif signal == -1:  # short
                if shares_held > 0:  # exit long positions
                    cash += shares_held*price - self.transaction_fee
                    shares_held = 0
                
                if shares_held == 0:  # short if not already short
                    max_shares = -int((cash-self.transaction_fee) / price)
                    cash += np.abs(max_shares)*price - self.transaction_fee
                    shares_held = max_shares

            elif signal == 0:  # exit positions
                if shares_held != 0:
                    cash += shares_held * price - self.transaction_fee
                    shares_held = 0

            # pay borrowing costs for short positions
            if shares_held < 0:
                cash -= np.abs(shares_held)*price*daily_borrow_rate
            
            # Calculate total portfolio value (cash + current stock holdings)
            portfolio_values.append(cash + shares_held*price)

        # Convert the portfolio values to a series after the loop
        self.portfolio_value = pd.Series(portfolio_values, index=self.data.index)
        # Calculate daily returns
        self.portfolio_returns = self.portfolio_value.pct_change(fill_method=None).dropna()


    def get_results(self, risk_free_rate: pd.Series, data_freq: str='D'):
        if len(self.portfolio_value) == 0:
            raise ValueError('First run the backtest')

        total_returns = (self.portfolio_value.iloc[-1]-self.starting_cash)/self.starting_cash
        average_returns = gmean(np.array(self.portfolio_returns)+1)-1
        
        if data_freq == 'D':
            annual_returns = (1+average_returns)**252 - 1
            annual_std = np.std(self.portfolio_returns) * np.sqrt(252)
        elif data_freq == 'W':
            annual_returns = (1+average_returns)**52 - 1
            annual_std = np.std(self.portfolio_returns) * np.sqrt(52)
        elif data_freq == 'MS':
            annual_returns = (1+average_returns)**12 - 1
            annual_std = np.std(self.portfolio_returns) * np.sqrt(12)
        else:
            annual_returns = average_returns
            annual_std = np.std(self.portfolio_returns)
        
        sharpe_ratio = (annual_returns - risk_free_rate.mean()) / annual_std
        
        return {
            'portfolio_value': self.portfolio_value.iloc[-1],
            'total_returns': total_returns,
            'average_returns': average_returns,
            'annual_returns': annual_returns,
            'annual_std': annual_std,
            'sharpe_ratio': sharpe_ratio,
        }
    
    
    def get_data(self):
        return self.portfolio_value, self.portfolio_returns
        

    def plot_results(self, title: str='Backtest Results'):
        plot_time_series(
            self.portfolio_value,
            title=title,
            ylabel='Portfolio Value ($)'
        )
        
    
    def plot_analysis(self, title: str='Backtest Returns Distribution', hist_bins: int=50):
        plot_returns_distribution(
            self.portfolio_returns,
            title=title,
            hist_bins=hist_bins,
        )