#%%
from dotenv import load_dotenv
import pandas as pd
import polars as pl
import yfinance as yf
from serpapi import GoogleSearch
import os
import requests

load_dotenv()
#%%
# Alpha Vantage query setup example
AV_API_URL = "https://www.alphavantage.co/query"

# search parameters
# for current online price
params = {
    "function": "CURRENCY_EXCHANGE_RATE",
    "from_currency": "ADA",
    "to_currency": "USD",
    "apikey": os.getenv("ALPHA_VINTAGE_API")
    }


params = {
    "function": "DIGITAL_CURRENCY_DAILY",
    "symbol": "ADA",
    "market": "USD",
    "apikey": os.getenv("ALPHA_VINTAGE_API"),
    "datatype": "csv"
    }

r = requests.get(url=AV_API_URL, params=params)
data = r.json()
    

#%%
#* Converting prices to return
# Using YahooFinance!
df = yf.download(tickers="ADA-USD", start="2014-01-01", end="2025-05-01", progress=True)

# Converting pandas to polars df
df = pl.from_pandas(df.reset_index())

# %%
# Renaming columns for simplicity
df = df.rename({
    "('Date', '')": 'date',
    "('Open', 'ADA-USD')": 'open',
    "('High', 'ADA-USD')": 'high',
    "('Low', 'ADA-USD')": 'low',
    "('Close', 'ADA-USD')": 'close',
    "('Volume', 'ADA-USD')": 'volume'
    }).with_columns(pl.col('date').cast(pl.Date()))
# %%
# Calculate the simple and log returns on Close prices
df = df.with_columns(pl.col('close').pct_change(n=1).alias('simple_return'),
                     (pl.col('close') / pl.col('close').shift(n=1)).log().alias('log_return'))

# %%
