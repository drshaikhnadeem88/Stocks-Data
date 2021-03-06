# -*- coding: utf-8 -*-
"""Copy of yfinance_tutorial.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jPr8-k7jmX3FNqgJss97eGpb2esD8Nei

# [Predict The Future Stock Prices](https://youtu.be/OcpAkACOwW0)

# Select a ticker
"""

symbols = ['HDFCBANK.NS', '^NSEBANK', '^NSEI']

symbol = symbols[0]

history_years = 3
# set the number of days to predict
periods = 100

# Import the library  https://pypi.org/project/yfinance/
# uncomment the next line in the first try
!pip install yfinance --upgrade --no-cache-dir
import yfinance as yf
# select the market
msft = yf.Ticker(symbol)

# get stock info
print(msft.info)

# show actions (dividends, splits)
print(msft.actions)

# show dividends
print(msft.dividends)

# show splits
print(msft.splits)

# show yearly financials
print(msft.financials)

# show quarterly financials
print(msft.quarterly_financials)

# show major holders
print(msft.major_holders)

# show institutional holders
print(msft.institutional_holders)

# show yearly balance sheet
print(msft.balance_sheet)

# show quarterly balance sheet
print(msft.quarterly_balance_sheet)

# show cashflow
print(msft.cashflow)

# show quarterly cashflow
print(msft.quarterly_cashflow)

# show yearly earnings
print(msft.earnings)

# show quarterly earnings
print(msft.quarterly_earnings)

# show sustainability
print(msft.sustainability)

# show analysts recommendations
print(msft.recommendations)

# show next event (earnings, etc)
print(msft.calendar)

# show ISIN code - *experimental*
# ISIN = International Securities Identification Number
print('International Securities Identification Number: ' + msft.isin)

# show options expirations
print(msft.options)

# get option chain for specific expiration
# opt = msft.option_chain('2021-12-17')
# data available via: opt.calls, opt.puts

# get historical market data
df = msft.history(period="2y")
print(df)

import datetime
# get today date
end_date = datetime.date.today()
# find the time range
days = datetime.timedelta(history_years * 365)
# get the start date
start_date = end_date - days
print('Price history loaded from ' + str(start_date) + ' to ' + str(end_date))

df = yf.download(symbol, str(start_date), str(end_date))

# drod columns and reset index
df = df.drop(['Open', 'High', 'Low', 'Adj Close',
              'Volume'], axis=1).reset_index()
# rename columns for using in Prophet
df.rename(columns={'Close': 'y'}, inplace=True)
df.rename(columns={'Date': 'ds'}, inplace=True)

print(df)

# display statistics
df.describe()

import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

# the histogram of the data
plt.figure(figsize=(8, 6))
n, bins, patches = plt.hist(df['y'], density=True, facecolor='g', alpha=0.75)

plt.title(symbol + ' Close Price Distribution')
plt.xlabel('Close Price ($)')
plt.ylabel('Probability')
# plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
# plt.xlim(40, 160)
# plt.ylim(0, 0.03)
plt.grid(True)
plt.show()

import math
# calculate the yarly return and its standard deviation
simple_return = df['y'].pct_change(1).dropna()
# calculate the yarly return and its standard deviation
av_return = simple_return.mean(skipna=True) * 25200
std_return = simple_return.std(skipna=True) * math.sqrt(252) * 100

print('Averaged yearly return: ' + str(round(av_return)) + '%, its standard deviation: ' + str(round(std_return)), '%')

"""# Fitting Prophet Model"""

# uncomment the next line in the first try
#!pip install prophet --upgrade --no-cache-dir
from prophet import Prophet
# initialize the model
m = Prophet(
        growth='linear', 
        changepoints=None, 
        n_changepoints=25, 
        changepoint_range=0.8, 
        yearly_seasonality=True, 
        weekly_seasonality=False, 
        daily_seasonality=False, 
        holidays=None,
        seasonality_mode='additive', 
        seasonality_prior_scale=10, 
        holidays_prior_scale=10, 
        changepoint_prior_scale=0.05, 
        mcmc_samples=0, 
        interval_width=0.8, 
        uncertainty_samples=1000, 
        stan_backend=None
            )
# fit the model
m.fit(df)
# create the dataframe
future = m.make_future_dataframe(periods=periods)
# future.tail()
# predict the future prices
forecast = m.predict(future)

# plot components
m.plot_components(forecast)

# plot the observed and predicted date
fig1 = m.plot(forecast)

# crop the table
forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
# show the results
forecast

# save the predicted prices to a json-file
forecast.to_json((symbol+'_forecast.json'))

"""# Predicted Prices"""

# the histogram of the data
plt.figure(figsize=(10, 8))

plt.plot(forecast['ds'], forecast['yhat'])
plt.plot(forecast['ds'], forecast['yhat_lower'])
plt.plot(forecast['ds'], forecast['yhat_upper'])
plt.title(symbol + ' Close Price Forecast')
plt.xlabel('Day')
plt.ylabel('Predicted Price ($)')
plt.grid(True)
plt.show()