import numpy as np
import pandas as pd
import yfinance as yf
import os
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
returns: pandas DataFrame with dates and daily returns (adjusted) for one or more tickers
param tickers: list of strings of ticker symbols for individual securities
param period: ticker returns data goes back for 'period' amount of time
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
    if len(tickers) == 1:
        prices = pd.DataFrame(prices)
        prices.columns = tickers

    # compute returns (vectorized)
    returns = prices.pct_change()
    returns.index = returns.index.strftime('%Y-%m-%d')

    return returns.dropna()

"""
returns: pandas DataFrame with dates and daily returns of factor portfolios

note that 'factors.pk' spans 2025, so it is artificially setting the regression time range constraint (since merged table is inner join)
"""
def load_factors():
    factors = pd.read_pickle('data.pk')
    return factors

"""
returns: DataFrame with factor betas for the ticker(s)
param df: DataFrame containing aligned factor returns and ticker returns data. ticker columns come before factor columns
"""
def compute_betas(df):
    # if including growth:
    # factor_cols = ['mktrf', 'hml', 'umd', 'VUG']

    # if not including growth:
    # factor_cols = ['mktrf', 'hml','umd']
    # df = df.drop(columns='VUG')

    # using data.pk -- reconstructed FF factors
    factor_cols = ['momentum','growth','value','mkt']
    
    ticker_cols = [col for col in df.columns if col not in factor_cols + ['date']]
    
    results = []
    X = df[factor_cols]
    
    for ticker in ticker_cols:
        model = LinearRegression()
        y = df[ticker]
        model.fit(X, y)
        results.append({
            'ticker': ticker,
            'alpha': model.intercept_,
            'beta_momentum': model.coef_[0],
            'beta_growth': model.coef_[1],
            'beta_value': model.coef_[2],
            'beta_market': model.coef_[3],
            'R^2': model.score(X, y)
        })
    
    return pd.DataFrame(results)

"""
returns: DataFrame with factor betas for one or more tickers
param tickers: list of strings of ticker symbols for individual securities
"""
def run_analysis(tickers):

    # get factor data
    factors = load_factors()

    # get ticker data
    tick = load_returns(tickers)

    # merge data into one table
    df = tick.merge(factors, left_index=True, right_on='date', how='inner')
    df.index = df['date']

    # regression
    return compute_betas(df)


if __name__ == "__main__":

    tickers = ['AAPL','TSLA']

    print(run_analysis(tickers))
