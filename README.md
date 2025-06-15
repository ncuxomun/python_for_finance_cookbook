# This is my version of learning and implementing "Python for Finance Cookbook". I will focus on using `polars` as much as possible.

# Table of Contents:
## Chapter 1: Acquiring Financial Data
The chapter focuses on a few most popular sources of financial data, inc. Yahoo Finance, Nasdaq Data Link, Intrinio, and Alpha Vantage, for which we leverage dedicated Python libraries to load and process data for further analysis. 

### APIs (and loaded) explored:
 - SerpAPI (FREE: 100 calls per month)
 - AlphaVantage (FREE: 25 calls per day + some other limitations)
 - NewsAPI for News Sentiment
 - Intrinio, Tiigo (AlphaVantage alternatives)

 ## Chapter 2: Data Processing
 The chapter covers data (timeseries) preprocessing, i.e., data wrangling and manipulation before it can actually be usable. Chapter covers the following:
 - Converting prices to returns
 - Adjusting the returns for inflation
 - Changing the frequency of the timeseries data
 - Different ways of imputing the missing data
 - Changing currencies and Different ways of aggregating the data

 ## Chapter 3: Visualizing Financial Time Series
 The chapter covers:
 - Basic visualization
 - Visualizing seasonal patterns
 - Creating interactive visualizations
 - Creating candlestick charts