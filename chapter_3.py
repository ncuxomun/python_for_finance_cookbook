#%%
from dotenv import load_dotenv
import pandas as pd
import polars as pl
import yfinance as yf
from serpapi import GoogleSearch
import os
import requests
import plotly.express as px

#%%
# Using YahooFinance!
df = yf.download(tickers="ADA-USD", start="2014-01-01", end="2025-05-01",
                 auto_adjust=True, interval="1wk", progress=True)

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

# Simple return
df = df.with_columns(pl.col('close').pct_change().alias('simple_return'))

# %%
#* Simple plots

# Plotting using plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# define figure
fig = make_subplots(rows=3, cols=1, shared_xaxes=True)

# adding the first data the plot
fig.add_trace(go.Line(x=df.get_column('date'), y=df.get_column('close'), name="close"),
              row=1, col=1)

# adding the second plot
fig.add_trace(go.Scatter(x=df.get_column('date'), y=df.get_column('simple_return'), 
                         mode="markers", name="simple_return"),
              row=2, col=1
              )

# adding the third plot
fig.add_trace(go.Scatter(x=df.get_column('date'), y=df.get_column('volume'), name="volume"),
              row=3, col=1)

# layout and other edits
fig.update_layout(height=600, width=600, title_text='Simple subplots')
# %%
#* Create seasonal plots
# Using Unemployment rate from Alpha Vantage
# Alpha Vantage query setup example
AV_API_URL = "https://www.alphavantage.co/query"

# search parameters
params = {
    "function": "UNEMPLOYMENT",
    "apikey": os.getenv("ALPHA_VINTAGE_API")
    }

r = requests.get(url=AV_API_URL, params=params)
data = r.json()
# %%
df_un_rate = (pl.DataFrame(data.get("data"))
              ).rename({'value': 'unemp_rate_%'}
                       ).with_columns(pl.col('date').str.to_date(),
                                      pl.col('unemp_rate_%').cast(pl.Float32))
                       
df_un_rate = df_un_rate.filter(pl.col('date').dt.year() > 2015, pl.col('date').dt.year() <= 2024)
# %%
# Seasonal plot
df_un_rate = df_un_rate.with_columns(pl.col('date').dt.strftime("%b").alias('month'),
                                     pl.col('date').dt.year().alias('year'))

fig = px.line(data_frame=df_un_rate,
              x='month',
              y='unemp_rate_%',
              color='year',
              line_dash='year',
              color_discrete_sequence=px.colors.qualitative.G10
              )

fig.update_layout(legend_title_text="Year")
fig.show()
# %%
# Alternative seasonal plots
from statsmodels.graphics.tsaplots import month_plot, quarter_plot

# monthly plot
month_plot(df_un_rate.to_pandas().set_index('date')['unemp_rate_%'])
# %%
# polar plot
month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

fig = px.line_polar(data_frame=df_un_rate,
                    r="unemp_rate_%",
                    theta="month",
                    color="year",
                    width=600, height=500,
                    # direction="counterclockwise",
                    category_orders={"month": month_order},
                    line_close=True,
                    range_r=[3, 8]
                   )
fig.show()
# %%
#* Candlestick chart
fig = go.Figure(data=[go.Candlestick(x=df['date'],
                                     open=df['open'],
                                     high=df['high'],
                                     low=df['low'],
                                     close=df['close'],
                                     name="ADA/USD"),
                      ]
                )
# 3. Add a Volume Bar Chart (optional but common for financial charts)
#    This will be a secondary Y-axis.
fig.add_trace(go.Bar(x=df['date'],
                     y=df['volume'],
                     name='Volume',
                     marker_color='rgba(0, 128, 0, 0.5)',  # Greenish for volume
                     yaxis='y2' # Assign to secondary y-axis
                    ))

# 4. Customize the Layout
fig.update_layout(
    title='ADA/USD Candlestick Chart',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    xaxis_rangeslider_visible=False, # Hide the default range slider below the chart
    xaxis_autorange=True,
    yaxis=dict(
        title='Price (USD)',
        # Keep `fixedrange` as False to allow zooming on price axis
        fixedrange=False,
    ),
    yaxis2=dict(
        title='Volume',
        overlaying='y', # Overlay on the primary y-axis
        side='right',    # Place on the right side
        fixedrange=False,
        showgrid=False # Don't show grid lines for volume axis
    ),
    # Add a global range slider beneath the plot for better navigation
    xaxis=go.layout.XAxis(
        rangeslider=dict(
            visible=True
        ),
        type='date'
    ),
    hovermode='x unified', # Shows all data for a given X-coordinate on hover
    height=500, # Adjust height for better visibility
    template='plotly_white' # Use a clean white background template
)

# Show the plot
fig.show()

# %%
