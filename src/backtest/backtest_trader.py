import pandas as pd
import numpy as np
from scipy.stats import gmean
from typing import Tuple, List, Dict

from ..strategies import Strategy
from ..utils import plot_time_series, plot_returns_distribution, get_risk_free_rate

class BacktestTrader:
    def __init__(
        self,
        strategy: Strategy,
        data: pd.Series,
        data_freq: str='D',
        starting_cash: float=10000,
        transaction_fee: float=10,
        borrow_rate: float=0.02,
    ):
        """ Initializes a BacktestTrader object

        Args:
            strategy (Strategy): trading strategy to backtest
            data (pd.Series): historical price data of stock
            data_freq (str, optional): frequency of data. Defaults to 'D'.
            starting_cash (float, optional): starting cash for trading. Defaults to 10000.
            transaction_fee (float, optional): cost per transaction. Defaults to 10.
            borrow_rate (float, optional): annual rate for borrowing (shorting). Defaults to 0.02.
        """
        self.strategy = strategy
        self.data = data
        self.data_freq = data_freq
        self.starting_cash = starting_cash
        self.transaction_fee = transaction_fee
        self.borrow_rate = borrow_rate
        self.portfolio_value = pd.Series(dtype=float)
        self.portfolio_returns = pd.Series(dtype=float)
        self.bootstrap_results = pd.DataFrame(index=['mean', 'median', 'std', '95 upper', '95 lower'])
  
                     
    def _calculate_performance(self, price_data: pd.Series) -> Tuple[pd.Series, pd.Series]:
        signals = self.strategy.generate_signals(price_data)
        
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
        portfolio_values = pd.Series(portfolio_values, index=self.data.index)
        # Calculate daily returns
        portfolio_returns = portfolio_values.pct_change(fill_method=None).dropna()

        return portfolio_values, portfolio_returns


    def _stationary_bootstrap(
        self, 
        initial_price: float, 
        returns_data: pd.Series, 
        n_iterations: int, 
        block_size: int
    ) -> List[List[float]]:
        data_len = len(returns_data)
        bootstrap_samples = []
        
        for _ in range(n_iterations):
            sample = []
            i = np.random.randint(0, data_len)
            
            while len(sample) < data_len:
                sample.append(returns_data.iloc[i])
                
                if np.random.rand() < 1/block_size:
                    i = np.random.randint(0, data_len) # new block
                else:
                    i = (i+1) % data_len # same next value in block
            
            # reconstruct price series
            sample_prices = [initial_price]
            sample_prices.extend(np.cumprod(1+np.array(sample)))
            bootstrap_samples.append(sample_prices)
        
        return bootstrap_samples


    def _calculate_stats(self, returns_data: pd.Series) -> Dict[str, float]:
        average_returns = gmean(np.array(returns_data)+1)-1
        risk_free_rate = get_risk_free_rate(self.data.index[0], self.data.index[-1])
        
        if self.data_freq == 'D':
            annual_returns = (1+average_returns)**252 - 1
            annual_std = np.std(returns_data) * np.sqrt(252)
        elif self.data_freq == 'W':
            annual_returns = (1+average_returns)**52 - 1
            annual_std = np.std(returns_data) * np.sqrt(52)
        elif self.data_freq == 'MS':
            annual_returns = (1+average_returns)**12 - 1
            annual_std = np.std(returns_data) * np.sqrt(12)
        else:
            annual_returns = average_returns
            annual_std = np.std(returns_data)
        
        sharpe_ratio = (annual_returns - risk_free_rate.mean()) / annual_std
        
        return {
            'average_returns': average_returns,
            'annual_returns': annual_returns,
            'annual_std': annual_std,
            'sharpe_ratio': sharpe_ratio,
        }
        
    
    def _check_backtest_ran(self) -> None:
        if len(self.portfolio_value) == 0:
            raise ValueError('First run the backtest using run_backtest()')
        
        
    def run_backtest(self) -> None:
        """ Runs the backtest using the strategy and data provided
        """
        values, returns = self._calculate_performance(self.data)
        self.portfolio_value = values
        self.portfolio_returns = returns
        
        
    def run_bootstrap(self, n_iterations: int=1000, block_size: int=10) -> pd.DataFrame:
        """ Runs a stationary bootstrap on the backtest results

        Args:
            n_iterations (int, optional): Number of bootstrap iterations. Defaults to 1000.
            block_size (int, optional): Expected length of bootstrap block. Defaults to 10.

        Returns:
            pd.DataFrame: dataframe of statistics from the bootstrap
        """
        initial_price = self.data.iloc[0]
        returns = self.data.pct_change(fill_method=None).dropna()
        samples = self._stationary_bootstrap(initial_price, returns, n_iterations, block_size)
        sample_stats = {}
        
        for sample in samples:
            _, sample_returns = self._calculate_performance(
                pd.Series(sample, index=self.data.index)
            )
            stats = self._calculate_stats(sample_returns)
            
            for key, value in stats.items():
                sample_stats.setdefault(key, []).append(value)
            
        for key, value in sample_stats.items():
            ci = np.percentile(value, [2.5, 97.5])
            self.bootstrap_results.loc['mean', key] = np.mean(value)
            self.bootstrap_results.loc['median', key] = np.median(value)
            self.bootstrap_results.loc['std', key] = np.std(value)
            self.bootstrap_results.loc['95 lower', key] = ci[0]
            self.bootstrap_results.loc['95 upper', key] = ci[1]
        
        return self.bootstrap_results.T


    def get_results(self) -> Dict[str, float]:
        """ Gets the summary of backtest results

        Returns:
            Dict[str, float]: backtest results
        """
        self._check_backtest_ran
        
        stats = self._calculate_stats(self.portfolio_returns)
        stats['total_returns'] = (self.portfolio_value.iloc[-1]-self.starting_cash)/self.starting_cash
        stats['portfolio_value'] = self.portfolio_value.iloc[-1]
        
        return stats
    
    
    def get_data(self) -> Tuple[pd.Series, pd.Series]:
        """ Gets the backtested portfolio value and returns

        Returns:
            Tuple[pd.Series, pd.Series]: Backtested portfolio value and returns
        """
        
        self._check_backtest_ran
        return self.portfolio_value, self.portfolio_returns
        

    def plot_results(self, title: str='Backtest Results') -> None:
        """ Plots the time series of backtested portfolio value

        Args:
            title (str, optional): title of plot. Defaults to 'Backtest Results'.
        """
        self._check_backtest_ran
        plot_time_series(
            self.portfolio_value,
            title=title,
            ylabel='Portfolio Value ($)'
        )
        
    
    def plot_analysis(self, title: str='Backtest Returns Distribution', hist_bins: int=50) -> None:
        """ Plots a histogram and QQ plot of the backtested returns distribution

        Args:
            title (str, optional): title of plots. Defaults to 'Backtest Returns Distribution'.
            hist_bins (int, optional): number of bins for histogram. Defaults to 50.
        """
        self._check_backtest_ran
        plot_returns_distribution(
            self.portfolio_returns,
            title=title,
            hist_bins=hist_bins,
        )