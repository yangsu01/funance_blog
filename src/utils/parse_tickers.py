import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup

def parse_tickers(file_name: str, file_path: str, save_path: str) -> None:
    """ Parses tickers from an html table and saves them to a csv file.

    Args:
        file_name (str): name of the file containing the html table
        file_path (str): path of the folder containing the html file
        save_path (str): path of the folder to save the csv file
    """
    soup = BeautifulSoup(open(f'{file_path}{file_name}.html'), 'html.parser')
    
    # extract tickers. update accordingly
    tickers = []
    rows = soup.find_all('tr')
    for row in rows:
        td = row.find_all('td')
        
        if len(td) > 2:
            tickers.append(td[2].find('a').text)
        
    df = pd.DataFrame(tickers, columns=['ticker'])
    
    # add columns
    columns = ['longName', 'sector', 'industry']
    for col in columns:
        df[col] = None
        
    for ticker in tickers:
        data = yf.Ticker(ticker)
        info = data.info
        for col in columns:
            try:
                df.loc[df['ticker'] == ticker, col] = info[col]
            except:
                pass
            
    df.to_csv(f'{save_path}{file_name}.csv', index=False)