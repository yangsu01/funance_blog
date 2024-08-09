from ..utils.fundamentals import get_metrics, calculate_market_sector_mean

def compare_to_market(ticker: str, market_tickers: list) -> dict:
    """ Compares the fundamentals of a stock to the average of the market and sector

    Args:
        ticker (str): ticker of the stock
        market_tickers (list): list of tickers in the market

    Returns:
        dict: stock info and metrics compared to market and sector
    """
    info = get_metrics(ticker)
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