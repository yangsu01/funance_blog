"""
Investment strategy based on Factor Models and Dimensionality Reduction

Objective:
    Prioritize growth while maintaining a diversified portfolio that capture market trends

Intended holding period: 1 month

Steps:
    1. For each stock, fit a regression model to find loadings on Carhart four factors
    2. Use ARIMA models to forecast future values of the factors
    3. Calculate expected returns for selected stocks using forecasted factors
    4. Use PCA to reduce dimensionality of stock returns
    5. Use K-means clustering to group stocks based on significant PCs
    6. Select stocks with highest expected returns in each cluster
    7. Construct a portfolio using Modern Portfolio Theory
"""
import pandas as pd
import numpy as np

from ..utils.stats import pca, fit_regression, forecast_arima, cluster_kmeans
from ..utils.optimize_portfolio import optimize_portfolio
from ..utils.tools import daily_to_monthly

def pca_fa( 
    returns: pd.DataFrame,
    factors: pd.DataFrame,
    tickers_per_cluster: int=1,
    pc_variance_threshold: float=0.9
) -> dict:
    """ Constructs a portfolio using the pca_fa strategy
    Intended holding period: 1 month
    Training data: 5 years

    Args:
        returns (pd.DataFrame): historical returns of stocks
        factors (pd.DataFrame): daily values of Carhart four factors and risk-free rate
        tickers_per_cluster (int, optional): tickers to filter in each cluster. Defaults to 1.
        pc_variance_threshold (float, optional): fraction of market variance to capture. Defaults to 0.9.

    Returns:
        dict: weights of selected stocks in portfolio
    """
    start_date = returns.index[0]
    end_date = returns.index[-1]
    
    # splice factors data to match time period
    factors = factors.loc[start_date:end_date] # match with returns length
    
    # forecast factors using ARIMA
    factor_forecasts = {}
    monthly_factors = daily_to_monthly(factors)
    for col in monthly_factors.columns:
        factor_forecasts[col] = forecast_arima(monthly_factors[col])['forecast']
    
    expected_returns = []
    betas = [] # used for calculating covariance matrix
    alphas = [] # intercepts of regression
    mse = [] # mean squared error of regression
    x = monthly_factors[['Mkt-RF', 'SMB', 'HML', 'Mom']] # Carhart factors
    
    # fit regression and calculate expected returns for each stock
    cols_to_drop = []
    for col in returns.columns:
        stock_returns = returns[col].dropna()
        
        if len(stock_returns) != len(factors):
            cols_to_drop.append(col)
            continue
        else:
            y = returns[col] - factors['RF'] # excess returns
        
            # convert to monthly returns
            y = daily_to_monthly(y)
            # fit regression model
            res = fit_regression(x, y)
            
            expected_returns.append(
                res['params']['const'] + \
                res['params']['Mkt-RF'] * factor_forecasts['Mkt-RF'] + \
                res['params']['SMB'] * factor_forecasts['SMB'] + \
                res['params']['HML'] * factor_forecasts['HML'] + \
                res['params']['Mom'] * factor_forecasts['Mom'] + \
                factor_forecasts['RF']
            )
            betas.append(res['params'].values[1:].tolist())
            mse.append(res['mse'])
            alphas.append(res['params']['const'])
    
    # drop columns with missing data
    filtered_returns = returns.drop(cols_to_drop, axis=1)
    
    # convert expected returns to dataframe
    df = pd.DataFrame(
        [expected_returns, betas, mse, alphas],
        index=['expected return', 'beta', 'mse', 'alpha'],
        columns=filtered_returns.columns
    ).T
    num_stocks = len(df)

    # pca on returns
    filtered_returns = daily_to_monthly(filtered_returns) # convert to monthly returns
    pca_res = pca(filtered_returns)
    num_pcs = np.argmax(np.cumsum(pca_res['variance']) > pc_variance_threshold) + 1
    reduced_loadings = pca_res['loadings'].iloc[:num_pcs, :]
    
    # kmeans clustering
    kmeans = cluster_kmeans(reduced_loadings.T, num_stocks-1)
    labels = kmeans['optimal_labels']
    num_clusters = len(set(labels))
    df['label'] = labels
    
    # select top stock from each cluster
    selected_stocks = []
    for i in range(num_clusters):
        cluster = df[df['label'] == i]
        # select stocks with expected return > 1%
        positive_returns = cluster[
            (cluster['expected return'] > 0.01) &
            (cluster['alpha'] > 0)
        ].copy()
        
        for i in range(tickers_per_cluster):
            if positive_returns.empty:
                break
            stock = positive_returns['expected return'].idxmax()
            selected_stocks.append(stock)
            positive_returns.drop(stock, inplace=True)
    
    asset_returns = df.loc[selected_stocks]['expected return'].to_list()
    
    # compute covariance matrix
    sigma_f = np.cov(x.T) # sample cov matrix of factors
    beta_matrix = np.array(df.loc[selected_stocks]['beta'].to_list())
    sigma_e = np.diag(df.loc[selected_stocks]['mse'].to_list())
    
    cov_matrix = beta_matrix @ sigma_f @ beta_matrix.T + sigma_e
    
    # optimize portfolio weights
    weights, _ = optimize_portfolio(
        asset_returns,
        cov_matrix,
        factor_forecasts['RF'],
        [(0, 1) * len(asset_returns)] # no shorting
    )
    
    allocation = dict(zip(selected_stocks, weights.round(4)))
    # delete stocks with zero allocation
    allocation = {k: v for k, v in allocation.items() if v > 0}
    
    return allocation
    