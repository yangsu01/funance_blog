import yfinance as yf
import pandas as pd

def get_fundamentals(ticker: str) -> dict:
    """Gets fundamental metrics for a given stock ticker

    Args:
        ticker (str): ticker of the stock

    Returns:
        dict: {
            stock_info: {
                ticker: str,
                industry: str,
                sector: str,
                current_price: float,
                analyst_low_price: float,
                analyst_median_price: float,
                analyst_high_price: float,
            },
            
            metrics: {
                sector: str,
                beta: float,
                risk_rating: float,
                forward_pe: float,
                peg_ratio: float,
                pb_ratio: float,
                ev_ebitda: float,
                revenue_growth: float,
                earnings_growth: float,
                profit_margin: float,
                roe: float,
                cash_per_share: float,
                short_ratio: float,
                analyst_median_growth: float,
                recommendation_mean: float,
            }
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        'stock_info': {
            'ticker': ticker,
            'industry': info.get('industry', 'n/a'),
            'sector': info.get('sector', 'n/a'),
            'current_price': info.get('currentPrice', None),
            'analyst_low_price': info.get('targetLowPrice', None),
            'analyst_median_price': info.get('targetMedianPrice', None),
            'analyst_high_price': info.get('targetHighPrice', None),
        },
        
        'metrics': {
            'sector': info.get('sector', 'n/a'),
            
            # risk metrics
            'beta': info.get('beta', 1), # market risk (lower = less risky)
            'risk_rating': info.get('overallRisk', None), # risk rating out of 10 (lower = better)
            
            # valuation metrics
            'forward_pe': info.get('forwardPE', None), # projected price to earnings (lower = better)
            'peg_ratio': info.get('trailingPegRatio', None), # price to earnings adjusted for growth (lower = better, ideally < 1)
            'pb_ratio': info.get('priceToBook', None), # price to book ratio (lower = better)
            'ev_ebitda': info.get('enterpriseToEbitda', None), # enterprise value to ebitda (lower = better)
            
            # growth metrics
            'revenue_growth': info.get('revenueGrowth', None), # percent growth in revenue (higher = better)
            'earnings_growth': info.get('earningsGrowth', None), # percent growth in earnings (higher = better)
            
            # profitability metrics
            'profit_margin': info.get('profitMargins', None), # percent of revenue that is profit (higher = better)
            'roe': info.get('returnOnEquity', None), # percent return on equity (higher = better)
            
            # financial health metrics
            'cash_per_share': info.get('totalCashPerShare', None), # cash per share (higher = better)
            'short_ratio': info.get('shortRatio', None), # number of days to cover short positions (lower = better)
            
            # analyst expectations. take it with a grain of salt
            'analyst_median_growth': round(100*(info.get('targetMedianPrice', 0)/info.get('currentPrice', 1) - 1), 2),
            'recommendation_mean': info.get('recommendationMean', None), # 1 to 5, with 1 being a strong buy and 5 being a strong sell
        }
    }
    
    
def get_price_history(tickers: list, start_date: str, end_date: str, period='1d') -> pd.DataFrame:
    """Gets historical prices for a list of stock tickers

    Args:
        tickers (list): list of stock tickers
        start_date (str): start date for historical data
        end_date (str): end date for historical data

    Returns:
        pd.DataFrame: historical prices of the stocks
    """
    data = yf.download(tickers, start=start_date, end=end_date, period=period)
    data = data['Adj Close']
    
    return data


def get_tickers(filename: str) -> list:
    """Gets a list of stock tickers from a csv file in the /data folder

    Args:
        filename (str): name of the text file

    Returns:
        list: list of stock tickers
    """
    return pd.read_csv(f'../data/{filename}.csv')['ticker'].tolist()