from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

def plot_time_series(
    data: pd.Series,
    title: str,
    ylabel: str='Price ($)',
    xlabel: str='Date',
) -> None:
    """ Plot time series data

    Args:
        data (pd.Series): series of dates and values
        title (str): title of the plot
        ylabel (str, optional): y axis label. Defaults to 'Price ($)'.
        xlabel (str, optional): x axis label. Defaults to 'Date'.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(data)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.grid()
    plt.show()

def plot_returns_distribution(
    data: pd.Series,
    title: str,
    hist_bins: int=50,
) -> None:
    """ Plot histogram/KDE and normal QQ plot of data

    Args:
        data (pd.Series): data to plot
        title (str): title of the plot
    """
    mean = np.mean(data)
    std = np.std(data)
    kde = stats.gaussian_kde(data)
    x_values = np.linspace(min(data), max(data), 1000)
    kde_values = kde(x_values)
    normal_values = stats.norm.pdf(x_values, mean, std)

    fig, axs = plt.subplots(2, 1, figsize=(10, 10))
    # histogram and KDE
    axs[0].hist(data, bins=hist_bins, density=True, edgecolor='black')
    axs[0].plot(x_values, normal_values, color='blue', linestyle='--', label='Normal Distribution')
    axs[0].plot(x_values, kde_values, color='magenta', linestyle='--', label='Kernel Density Estimation')
    axs[0].axvline(mean, color='red', linestyle='--', label=f'Mean Returns: {100*mean:.4f}%')
    axs[0].set_xlabel('Daily Returns')
    axs[0].set_ylabel('Frequency')
    axs[0].set_title('Histogram and KDE')
    axs[0].legend()
    # QQ plot
    stats.probplot(data, dist="norm", plot=axs[1])
    axs[1].set_title('Normal QQ Plot')

    fig.suptitle(title)
    fig.tight_layout()