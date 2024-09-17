import pandas as pd
import numpy as np
from scipy.stats import gmean

from ..strategies import Strategy
from ..utils import plot_time_series, plot_returns_distribution

class BacktestTrader:
    def __init__(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        starting_cash: float=10000,
        transaction_fee: float=10,
        borrow_rate: float=0.02,
    ):
        """ Initializes a BacktestTrader object

        Args:
            strategy (Strategy): trading strategy to backtest
            data (pd.DataFrame): historical price data of stocks
            starting_cash (float, optional): starting cash for trading. Defaults to 10000.
            transaction_fee (float, optional): cost per transaction. Defaults to 10.
            borrow_rate (float, optional): annual rate for borrowing (shorting). Defaults to 0.02.
        """
        self.strategy = strategy
        self.data = data
        self.starting_cash = starting_cash
        self.transaction_fee = transaction_fee
        self.borrow_rate = borrow_rate
        self.portfolio = {ticker: 0 for ticker in self.data.columns}
        self.portfolio_value = pd.Series(dtype=float)
        self.portfolio_returns = pd.Series(dtype=float)
    
    def run_backtest(self):
        signals, weights = self.strategy.generate_signals(self.data)
        cash = self.starting_cash
        daily_borrow_rate = self.borrow_rate/252
        
        for date in self.data.index:
            daily_signals = signals.loc[date]
            daily_weights = weights.loc[date]
            daily_prices = self.data.loc[date]
            total_cash = cash
            
            for ticker in self.data.columns:
                price = daily_prices[ticker]
                signal = daily_signals[ticker]
                weight = daily_weights[ticker]
                curr_shares = self.portfolio.get(ticker)
                
                # update positions based on signals and weights
                if signal == 1: # long
                    max_shares = np.floor((total_cash*weight-self.transaction_fee)/price)
                    if max_shares > 0:
                        self.portfolio[ticker] = curr_shares + max_shares
                        cash -= max_shares*price + self.transaction_fee
                    
                elif signal == -1: # short
                    if curr_shares > 0: # exit long positions
                        cash += curr_shares*price - self.transaction_fee
                        total_cash = cash
                        self.portfolio[ticker] = 0
                        curr_shares = 0
                    
                    if curr_shares == 0: # short if not already short
                        max_shares = -np.floor((total_cash*weight-self.transaction_fee)/price)
                        self.portfolio[ticker] = curr_shares + max_shares
                        cash -= max_shares*price + self.transaction_fee
                
                elif signal == 0: # exit positions
                    if curr_shares != 0:
                        cash += curr_shares*price - self.transaction_fee
                        self.portfolio[ticker] = 0
                
                elif signal == 2: # hold / do nothing
                    pass
                
                # pay borrowing costs for short positions
                if self.portfolio.get(ticker) < 0:
                    cash -= np.abs(self.portfolio[ticker]*price*daily_borrow_rate)
                
            # calculate portfolio value
            value = pd.Series(
                [cash+np.sum([self.portfolio[ticker]*price for ticker in self.data.columns])],
                index=[date]
            )
            self.portfolio_value = pd.concat([self.portfolio_value, value])
            
        # calculate daily returns
        self.portfolio_returns = self.portfolio_value.pct_change(fill_method=None).dropna()
        
    def get_results(self, risk_free_rate: pd.Series, data_freq: str='D'):
        if len(self.portfolio_value) == 0:
            raise ValueError('First run the backtest')

        total_returns = (self.portfolio_value.iloc[-1]-self.portfolio_value.iloc[0])/self.portfolio_value.iloc[0]
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
        

    def plot_results(self, title: str='Backtest Results'):
        plot_time_series(
            self.portfolio_value,
            title=title,
        )
        
    
    def plot_analysis(self, title: str='Backtest Returns Distribution', hist_bins: int=50):
        plot_returns_distribution(
            self.portfolio_returns,
            title=title,
            hist_bins=hist_bins,
        )