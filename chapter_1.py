#%%
from dotenv import load_dotenv
import pandas as pd
import polars as pl
import yfinance as yf
from serpapi import GoogleSearch
import os

load_dotenv()

#%%
# Loading Apple Data from Yahoo Finance
df = yf.download(tickers="AAPL", start="2014-01-01", end="2025-05-01", progress=True)

# Converting pandas to polars df
df = pl.from_pandas(df)

# Downloads (latest 30 days) individual ticker w/ more dedicated info
# aapl = yf.Ticker("AAPL")

# %%
# Loading from SerpAPI
params = {
    # "q": "AAPL:NASDAQ",
    "q": "ADA-USD", # Cardano
    "engine": "google_finance",
    "window": "6M",
    "api_key": os.getenv("SERP_API")
}

search = GoogleSearch(params)
results = search.get_dict()

# results.get("graph") outputs list of dicts with data. For example, when results["graph"][0]
# {'price': 234.93,
#  'currency': 'USD',
#  'date': 'Nov 27 2024, 04:00 PM UTC-04:00',
#  'volume': 33498439}

# %%
