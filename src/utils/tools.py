import pandas as pd 

def daily_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Converts daily data to monthly data
    
    Args:
        df (pd.DataFrame): daily returns (in decimals)
    
    Returns:
        pd.DataFrame: monthly data (in decimals)
    """
    return df.resample('ME').apply(lambda x: (1 + x).prod() - 1)