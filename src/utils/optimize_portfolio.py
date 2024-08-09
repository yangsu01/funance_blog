import numpy as np
from scipy.optimize import minimize
from typing import Tuple

def optimize_portfolio(
    expected_returns: np.array, 
    cov_matrix: np.array, 
    risk_free_rate: float,
    bounds: list=None
) -> Tuple[np.array, float]:
    """ Finds tangent portfolio using Modern Portfolio Theory

    Args:
        expected_returns (np.array): expected returns of assets in portfolio
        cov_matrix (np.array): covariance matrix of assets in portfolio
        risk_free_rate (float): risk free rate
        bounds (list, optional): constraints on each weight (min, max). Defaults to None.

    Returns:
        np.array: weights and expected return of tangent portfolio
    """
    n_assets = len(expected_returns)
    
    # objective function
    def neg_sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate):
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
        return -sharpe_ratio

    # weights need to sum to 1
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

    # weights must be between 0 and 1 (no short selling)
    bounds = [(0, 1)] * n_assets

    # initial guess
    initial_guess = [1/n_assets] * n_assets

    # minimize negative sharpe ratio (maximize sharpe ratio)
    results = minimize(
        neg_sharpe_ratio,
        initial_guess,
        args=(expected_returns, cov_matrix, risk_free_rate),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    return results.x, np.dot(results.x, expected_returns)