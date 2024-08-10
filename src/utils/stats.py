import pandas as pd
from sklearn.decomposition import PCA
from statsmodels.api import add_constant, OLS
from statsmodels.tsa.arima.model import ARIMA
from pmdarima.arima import auto_arima
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def pca(returns_df: pd.DataFrame) -> dict:
    """Performs PCA on given list of tickers

    Args:
        returns_df (pd.DataFrame): historical returns data (n_samples, n_features)

    Returns:
        dict: results of PCA
    """
    tickers = returns_df.columns.tolist()
    
    # standardize data (0 mean, 1 std)
    returns_df = (returns_df - returns_df.mean()) / returns_df.std()
    
    # perform PCA
    pca = PCA()
    principal_components = pca.fit_transform(returns_df)
    eigenvals = pca.explained_variance_ratio_
    eigenvecs = pca.components_
    
    return {
        'principal_components': principal_components,
        'variance': eigenvals,
        'loadings': pd.DataFrame(
            eigenvecs, 
            columns=tickers
        )
    }
    

def fit_regression(
    x: pd.DataFrame, 
    y: pd.Series, 
    add_intercept: bool=True, 
    print_summary: bool=False,
) -> dict:
    """Fits a linear regression model to the data

    Args:
        x (pd.DataFrame): dependent variable(s)
        y (np.array): independent variable
        add_intercept (bool, optional): add y-intercept to fit. Defaults to True.
        print_summary (bool, optional): print regression summary. Defaults to False.

    Returns:
        dict: model parameters and statistics
    """
    
    if add_intercept:
        x = add_constant(x)
    model = OLS(y, x).fit()
    
    if print_summary:
        print(model.summary())
        
    return {
        'params': model.params,
        'r_squared': model.rsquared,
        'residuals': model.resid,
        'p_values': model.pvalues,
        'mse': model.mse_resid
    }
    
def forecast_arima(data: pd.Series) -> dict:
    """Finds best order for ARIMA model and forecasts 1 step ahead

    Args:
        data (pd.Series): time series data

    Returns:
        dict: date of forecast and forecasted value
    """
    model_order = auto_arima(
        data,
        seasonal=False,
        stepwise=True,
        supress_warnings=True,
    ).order
    
    model = ARIMA(
        data,
        order=model_order
    ).fit()
    forecast = model.forecast(steps=1)
    
    return {
        'date': forecast.index[0].strftime('%Y-%m-%d'), 
        'forecast': forecast.iloc[0]
    }


def cluster_kmeans(data: pd.DataFrame, max_clusters: int) -> dict:
    """Clusters data using KMeans and returns the optimal fit and silhouette scores

    Args:
        data (pd.DataFrame): cluster data (n_samples, n_features)
        max_clusters (int): maximum number of clusters to test

    Returns:
        dict: inertias, silhouette scores, optimal cluster and labels
    """
    silhouette_scores = []
    inertias = []
    
    for k in range(2, max_clusters+1):
        kmeans = KMeans(n_clusters=k, random_state=0)
        labels = kmeans.fit_predict(data)
        inertias.append(kmeans.inertia_)
        s_s = silhouette_score(data, labels)
        
        # update clusters if silhouette score is higher
        if not silhouette_scores or s_s > max(silhouette_scores):
            optimal_labels = labels
            optimal_clusters = k
            
        silhouette_scores.append(s_s)
        
    return {
        'inertias': inertias,
        'silhouette_scores': silhouette_scores,
        'optimal_labels': optimal_labels,
        'optimal_clusters': optimal_clusters
    }