import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime
from matplotlib import pyplot as plt
from scipy.stats import gmean

from ..strategies import Strategy

class Backtest:
    def __init__(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        trading_freq: str,
        fitting_window: int,
        fitting_window_units: str,
        starting_cash: float=10000,
    ):
        """ Initializes a backtest object

        Args:
            strategy (Strategy): trading strategy to backtest
            data (pd.DataFrame): historical price data of stocks
            trading_freq (str): how often to trade (D, W, MS, YS)
            fitting_window (int): window size for fitting the model
            fitting_window_units (str): units for fitting window (days, months, years)
            starting_cash (float, optional): starting cash for the portfolio. Defaults to 10000.
        """
        self.strategy = strategy
        self.data = data
        self.trading_freq = trading_freq
        self.fitting_window = fitting_window
        self.fitting_window_units = fitting_window_units
        self.starting_cash = starting_cash
        self.portfolios = []
        self.portfolio_values = [starting_cash]
        self.portfolio_returns = []
        
    def run_backtest(self):
        print('Running backtest...')
        
        delta_kwargs = {self.fitting_window_units: self.fitting_window}
        start_date = self.data.index[0]
        end_date = self.data.index[-1]
        backtest_start_date = start_date + relativedelta(**delta_kwargs)
        test_dates = pd.date_range(backtest_start_date, end_date, freq=self.trading_freq)
        
        # drop last date to avoid out of bounds error
        for i, date in enumerate(test_dates[:-1]):
            
            # splice data for fitting
            fit_start = (date - relativedelta(**delta_kwargs)).strftime('%Y-%m-%d')
            fit_end = date.strftime('%Y-%m-%d')
            fit_data = self.data.loc[fit_start:fit_end]
            
            allocation = self.strategy.generate_portfolio(fit_data)
            
            self.portfolios.append({
                'purchase_date': fit_end,
                'prediction_date': test_dates[i+1].strftime('%Y-%m-%d'),
                'portfolio': allocation
            })
            print(f'Test {i+1}/{len(test_dates)-1} complete')
    
    def calculate_performance(self, risk_free_rate: pd.Series):
        for portfolio in self.portfolios:
            tickers = list(portfolio['portfolio'].keys())
            weights = list(portfolio['portfolio'].values())
            
            # if no stocks selected, skip
            if not tickers:
                self.portfolio_values.append(self.portfolio_values[-1])
                self.portfolio_returns.append(0)
                continue
            
            holding_period = self.data.loc[
                portfolio['purchase_date']:portfolio['prediction_date'], 
                tickers
            ]
            start_price = holding_period.iloc[0]
            end_price = holding_period.iloc[-1]
            actual_returns = (end_price - start_price) / start_price
            
            self.portfolio_values.append(
                self.portfolio_values[-1] * (1 + np.dot(weights, actual_returns))
            )
            
            self.portfolio_returns.append(
                np.dot(weights, actual_returns)
            )
        
        total_returns = (self.portfolio_values[-1] - self.portfolio_values[0]) / self.portfolio_values[0]
        average_returns = gmean(np.array(self.portfolio_returns) + 1) - 1
        
        if self.trading_freq == 'D':
            annual_returns = (1+average_returns)**252 - 1
            annual_std = np.std(self.portfolio_returns) * np.sqrt(252)
        elif self.trading_freq == 'W':
            annual_returns = (1+average_returns)**52 - 1
            annual_std = np.std(self.portfolio_returns) * np.sqrt(52)
        elif self.trading_freq == 'MS':
            annual_returns = (1+average_returns)**12 - 1
            annual_std = np.std(self.portfolio_returns) * np.sqrt(12)
        else:
            annual_returns = average_returns
            annual_std = np.std(self.portfolio_returns)
            
        sharpe_ratio = (annual_returns - risk_free_rate.mean()) / annual_std
        
        return {
            'total_portfolio_value': self.portfolio_values[-1],
            'total_returns': total_returns,
            'average_returns': average_returns,
            'annual_returns': annual_returns,
            'annual_std': annual_std,
            'sharpe_ratio': sharpe_ratio,
            'portfolio_history': self.portfolio_values,
            'returns_history': self.portfolio_returns,
            'portfolios': self.portfolios
        }
    
    def plot_performance(self):
        if not self.portfolios:
            raise ValueError('First run the backtest and calculate performance')