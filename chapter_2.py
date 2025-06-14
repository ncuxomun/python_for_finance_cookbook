#%%
from dotenv import load_dotenv
import pandas as pd
import polars as pl
import yfinance as yf
from serpapi import GoogleSearch
import os
import requests
import plotly.express as px

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


# params = {
#     "function": "DIGITAL_CURRENCY_DAILY",
#     "symbol": "ADA",
#     "market": "USD",
#     "apikey": os.getenv("ALPHA_VINTAGE_API"),
#     "datatype": "csv"
#     }

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
# df = df.with_columns(pl.col('close').pct_change(n=1).alias('simple_return'),
#                      (pl.col('close') / pl.col('close').shift(n=1)).log().alias('log_return'))

# %%
#* Adjusting the returns for inflation
params = {
    "function": "CPI",
    "interval": "monthly",
    "apikey": os.getenv("ALPHA_VINTAGE_API")
    }

r = requests.get(url=AV_API_URL, params=params)
data = r.json()
# %%
infl_df = pl.DataFrame(data.get("data")
                       ).rename({'value': 'cpi'}
                                ).with_columns(pl.col('date').cast(pl.Date()),
                                               pl.col('cpi').cast(pl.Float32))

# combining ADA and inflation dataframes
df = df.join(infl_df, on='date')
# %%
# Calculate simle and inflation returns
df = df.with_columns(
    pl.col('close').pct_change().alias('simp_rtrn'),
    pl.col('cpi').pct_change().alias('infl_rate')
    )

# Adjust the returns for inflation and calculate real returns 
df = df.with_columns(
    ((pl.col('simp_rtrn') + 1) / (pl.col('infl_rate') + 1) - 1).alias('real_rtn')
    )
# %%
#* USING CPI-library
import cpi

cpi_df = pl.from_pandas(cpi.series.get().to_dataframe()) # to load into dataframe

# changing the data types
cpi_df = cpi_df.rename({'value': 'cpi'}).with_columns(pl.col('date').cast(pl.Date()),
                                                      pl.col('cpi').cast(pl.Float32))

# Filter based on AV CPI data
cpi_df = cpi_df.filter((pl.col('period_type') == "monthly") & (pl.col('date') >= pl.date(2017, 12, 1)))

# %%
# Calculate realized volatility
df = df.with_columns((pl.col('close') / pl.col('close').shift(n=1)).log().alias('log_return'))

# Annual RV
df = df.with_columns(((pl.col('log_return').pow(2).rolling_sum(window_size=1).sqrt()) * (pl.lit(12).sqrt())).alias('rv'))

# %%
#* Different ways of imputing missing data
# Some naive ways - Backward and Forward filling

#* Converting currencies
# using forex_python lib
# %%
#* Data aggregation
# Using YahooFinance!
df = yf.download(tickers="ADA-USD", start="2014-01-01", end="2025-05-01",
                 interval="1wk", progress=True)

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

# bars
df = (df.with_row_index('row_count') # nice trick
      ).with_columns((pl.col('row_count') // 50).alias('tick_group'))

# %%
# aggregate by groups
df = df.group_by(['tick_group'], maintain_order=True).agg(pl.col('date').last(), pl.col('close').mean(), pl.col('volume').sum())
# %%
