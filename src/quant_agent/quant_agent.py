import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import gmean
import statsmodels.api as sm
from typing import Tuple

class QuantAgent:
    def __init__(
        self,
        ticker: str,
    ):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        self.ticker = ticker
        self.end_date = end_date.strftime('%Y-%m-%d')
        self.start_date = start_date.strftime('%Y-%m-%d')
        self.prices, self.returns = self._get_prices()
        
        
    def _get_prices(self) -> Tuple[pd.Series, pd.Series]:
        # download past year of adj close prices
        prices = yf.download(self.ticker, start=self.start_date, end=self.end_date)['Adj Close']
        returns = prices.pct_change().dropna()
        
        return prices, returns
    
    
    def _get_iv(self, strike) -> float:
        ticker = yf.Ticker(self.ticker)
        expire_dates = ticker.options
        
        # get expire date closest to 30 days from now
        expire_date = min(
            expire_dates, key=lambda x: abs(datetime.now() + timedelta(days=30) - datetime.strptime(x, '%Y-%m-%d'))
        )
        
        # average call and put iv for the strike price
        call_iv = ticker.option_chain(expire_date).calls
        put_iv = ticker.option_chain(expire_date).puts
        call_strikes = call_iv['strike'].values
        put_strikes = put_iv['strike'].values
        atm_call = min(call_strikes, key=lambda x: abs(x - strike))
        atm_put = min(put_strikes, key=lambda x: abs(x - strike))
        
        call_iv = call_iv[call_iv['strike'] == atm_call]['impliedVolatility'].iloc[0]
        put_iv = put_iv[put_iv['strike'] == atm_put]['impliedVolatility'].iloc[0]
        
        return (call_iv + put_iv) / 2
    
    
    def _get_alpha_beta(self) -> Tuple[float, float]:
        # risk-free rate (daily)
        rf = yf.download(
            '^TNX', start=self.start_date, end=self.end_date
        )['Adj Close'].values / (100*252)
        rf = np.delete(rf, 0) # match length of returns
        
        # market returns
        rm = yf.download(
            '^GSPC', start=self.start_date, end=self.end_date
        )['Adj Close'].pct_change().dropna().values
        
        # excess returns
        rm = rm - rf
        ri = self.returns - rf
        
        # regression to fit alpha and beta
        X = sm.add_constant(rm)
        model = sm.OLS(ri, X)
        results = model.fit()
        
        alpha = results.params.iloc[0]
        beta = results.params.iloc[1]
        
        return alpha, beta


    def _get_rf(self) -> float:
        return yf.Ticker('^TNX').info['previousClose'] / 100
        
    
    def _run_analysis(self) -> dict:
        # ewma 5, 20, 50, 200 days
        ewma_5 = self.prices.ewm(span=5, adjust=False).mean().iloc[-1]
        ewma_20 = self.prices.ewm(span=20, adjust=False).mean().iloc[-1]
        ewma_50 = self.prices.ewm(span=50, adjust=False).mean().iloc[-1]
        ewma_200 = self.prices.ewm(span=200, adjust=False).mean().iloc[-1]
        
        # annualized historical returns and volatility
        mean_returns = gmean(self.returns + 1)**252 - 1
        volatility = self.returns.std() * (252**0.5)
        rf = self._get_rf()
        sharpe_ratio = (mean_returns - rf) / volatility
        
        # implied volatility for ATM option
        implied_volatility = self._get_iv(self.prices.iloc[-1].round(0))
        
        # alpha and beta
        alpha, beta = self._get_alpha_beta()
        
        return { 
            'ticker': self.ticker,
            'generated at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '5 day ewma': ewma_5.round(2),
            '20 day ewma': ewma_20.round(2),
            '50 day ewma': ewma_50.round(2),
            '200 day ewma': ewma_200.round(2),
            'annualized historical returns (1 year)': mean_returns.round(4),
            'annualized volatility (1 year)': volatility.round(4),
            'sharpe ratio': sharpe_ratio.round(4),
            'implied volatility (average of 30 day ATM call and put)': implied_volatility.round(4),
            'alpha': alpha.round(4),
            'beta': beta.round(4)
        }
        
    
    def generate_output(self) -> None:
        output = self._run_analysis()
        file_name = f'quant_agent/outputs/{self.ticker}_output.json'
        
        with open(file_name, 'w') as f:
            json.dump(output, f, indent=4)
            
        print(f'Output saved to {file_name}')


if __name__ == '__main__':
    print('Enter ticker to analyze:')
    ticker = input("> ")
    print(f'Analyzing {ticker}...')
    agent = QuantAgent(ticker)
    agent.generate_output()