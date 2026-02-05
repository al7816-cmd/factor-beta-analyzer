import wrds
import numpy as np
import pandas as pd
import yfinance as yf
import os
# import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

"""
Author: Andy Li
Last Edited: 02/05/2026

objective: return the beta exposures (market, value, growth, momentum) for an individual ticker

logical flow:
1. load data
2. match ticker returns trailing 6m aligned w most recent available 6m of data for the factors (value, growth, momentum)
3. regression using statsmodels
4. return betas, output in table format
"""

#####################################################################################################################


"""
returns: pandas DataFrame with two columns: dates and daily returns (adjusted)
param ticker: list of strings of ticker symbols for individual securities --> *** PRELIMINARY VERSION. ONLY HANDLING ONE TICKER AT A TIME DUE TO CONSTRAINTS FROM REGRESSION. ***
"""
def load_returns(tickers, period="1y"):
    df = yf.download(
        tickers,
        period=period,
        auto_adjust=False,
        progress=False
    )

    # extract Adj Close
    prices = df['Adj Close']

    # compute returns (vectorized)
    returns = prices.pct_change()
    returns.index = returns.index.strftime('%Y-%m-%d')

    return returns.dropna()

"""
returns: pandas DataFrame with dates and daily returns of factor portfolios
param starting_date: when the returns are computed starting from
param conn: wrds Connection object --> eliminates redundancy to only use one connection object in the code
"""
def load_factors(starting_date = "2025-01-01", conn = None):
    if conn == None:
        conn = wrds.Connection(wrds_username="andyli26")

    query = "SELECT * FROM ff.fivefactors_daily WHERE date > '2025-01-01'"
    factors = conn.raw_sql(query)
    factors['mkt'] = factors['mktrf'] + factors['rf']
    factors = factors.drop(columns={'smb', 'rmw', 'cma', 'rf', 'mktrf'})
    return factors

"""
returns: DataFrame with factor betas for the ticker
param df: DataFrame containing aligned factor returns and ticker returns data. first column should be the ticker
"""
def compute_betas(df):
    model = LinearRegression()
    dep_column_name = df.columns[0]
    y = df[dep_column_name]

    X = df[['mkt', 'hml', 'umd']]
    model.fit(X, y)
    perf = pd.DataFrame([{
        'ticker': dep_column_name,
        'alpha': model.intercept_,
        'beta_market': model.coef_[0],
        'beta_value': model.coef_[1],
        'beta_momentum': model.coef_[2],
        'R^2': model.score(X, y)
    }])
    return perf

"""
returns: DataFrame with factor betas for the ticker
param ticker: list of strings of ticker symbols for individual securities --> *** PRELIMINARY VERSION. ONLY HANDLING ONE TICKER AT A TIME DUE TO CONSTRAINTS FROM REGRESSION. ***
"""
def run_analysis(tickers, conn=None):
    if(conn == None):
        conn = wrds.Connection(wrds_username="andyli26")

    # get factor data
    factors = load_factors(conn=conn)

    # get ticker data
    tick = load_returns(tickers)

    # merge data into one table
    df = tick.merge(factors, left_index=True, right_on='date', how='inner')
    df.index = df['date']

    # regression
    return compute_betas(df)


if __name__ == "__main__":

    conn = wrds.Connection(wrds_username="andyli26")
    tickers = ['AAPL']

    print(run_analysis(tickers, conn))
