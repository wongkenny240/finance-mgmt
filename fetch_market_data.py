"""
Author: KCKW
Description: fetch finance data for pandas dataframe and write to Excel

"""

import pandas_datareader.data as web
import matplotlib.pyplot as plt
import pandas as pd
import datetime

if __name__ == '__main__':
    # Define the instruments to download. We would like to see Apple, Microsoft and the S&P500 index.
    tickers = ['AAPL', 'AMZN']
    # We would like all available data from 01/01/2000 until 12/31/2016.
    start_date = '1980-01-01'
    end_date = '2020-10-05'

    for ticker in tickers:
        # User pandas_reader.data.DataReader to load the desired data. As simple as that.
        df = web.DataReader(ticker, 'yahoo', start_date, end_date)
        print(df)