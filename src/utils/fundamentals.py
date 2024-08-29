import pandas as pd

from .data_loader import get_fundamentals

def compare_to_market(ticker: str, market_tickers: list) -> dict:
    """ Compares the fundamentals of a stock to the average of the market and sector

    Args:
        ticker (str): ticker of the stock
        market_tickers (list): list of tickers in the market

    Returns:
        dict: stock info and metrics compared to market and sector
    """
    info = get_fundamentals(ticker)
    market_info = calculate_market_sector_mean(market_tickers, info["stock_info"]["sector"])
    stock_metrics = info['metrics']
    
    market_info[ticker] = stock_metrics
    market_info['Sector Diff'] = (market_info[ticker] - market_info['Sector']) / market_info['Sector']
    market_info['Market Diff'] = (market_info[ticker] - market_info['Market']) / market_info['Market']
    market_info = market_info[[ticker, 'Sector', 'Sector Diff', 'Market', 'Market Diff']]
    
    return {
        'stock_info': info['stock_info'],
        'risk_metrics': market_info.loc[['beta', 'risk_rating']],
        'valuation_metrics': market_info.loc[['forward_pe', 'peg_ratio', 'pb_ratio', 'ev_ebitda']],
        'growth_metrics': market_info.loc[['revenue_growth', 'earnings_growth']],
        'profitability_metrics': market_info.loc[['profit_margin', 'roe']],
        'financial_health_metrics': market_info.loc[['cash_per_share', 'short_ratio']],
        'analyst_expectations': market_info.loc[['analyst_median_growth', 'recommendation_mean']],
    }
    
def calculate_market_sector_mean(tickers: list, sector: str) -> pd.DataFrame:
    """Calculates the average metrics of a list of stocks and average of a given sector

    Args:
        tickers (list): list of stock tickers
        sector (str): sector to calculate the averages for

    Returns:
        pd.DataFrame: average metrics of the stocks and sector. uses metrics from get_metrics()
    """
    data = [get_metrics(ticker) for ticker in tickers]
    df = pd.DataFrame([d['metrics'] for d in data])
    
    average = {}
    sector_df = df[df['sector'] == sector].copy()
    sector_df.drop(columns='sector', inplace=True)
    df.drop(columns='sector', inplace=True)

    average['Market'] = df.mean()
    average['Sector'] = sector_df.mean()

    return pd.DataFrame(average)