Must have an IEX Console API token. Some commands will not work without a premium subscription.
https://iexcloud.io/



Make sure to run ```pip list -r requirements.txt```

Check out the .env.example file. If you have a Twitter developer account, you can hook up your twitter to post the output.


```
DJANGO_SETTINGS_MODULE='lab.settings'
DJANGO_SETTINGS_MODULE=lab.settings
IEX_TOKEN=pk_somevalue
IEX_SANDBOX_TOKEN=Tpk_somevalue
IEX_URL=https://cloud.iexapis.com/v1/
IEX_SANDBOX_URL=https://sandbox.iexapis.com/v1/
TWITTER_API_KEY='somevalue'
TWITTER_SECRET_KEY='somevalue'
TWITTER_ACCESS_KEY='somevalue'
TWITTER_ACCESS_SECRET='somevalue'
TWITTER_BEARER_TOKEN='somevalue'
```

Run this command to view available commands. All commands must be prepended with python run.py.


```python run.py list```

```
Command                                               Description
------------------------------------------------------------------------------------------------------------------------------
donchian [<ticker>]                                   Runs a donchian range calculation on a ticker
financials [<ticker>]                                 Returns financials data for ticker, including some custom indicators not provided by IEX.
macro:trends [--timeframe=1m] [--gain=20]             Scans all ETFs and returns the ETFs with the performance above an int (gain) within a timerange (5d, 1m, 3m, 1y)
macro:gainers                                         Scans all ETFs and returns ETFs with highest day change.
news:scrape [--query=insert+string]                   Searches a query and searches first 10 articles for stocks mentioned in article
hurst [<ticker>] [--output=table]                     Runs a rescaled range analysis on a ticker. Output defaults to table.
range [<ticker>] [--tweet]                            Runs a volatility range analysis on a ticker.
historicalprices:get [<ticker>]                       Fetches historical prices for a ticker and saves them to db.
inflation:calculate [--update]                        Inflation index using etfs
inflation:graph [--update]                            Graph inflation index using etfs
inflation:functions [--refresh]                       Grabs max historical prices for all etfs in sectors list, updates with fresh data.
trend:chase [--pennies]                               Scans all stocks and returns todays gainers with above certain thresholds (weeds out the penny stocks).
trend:search [--string=]                              Scans stocks with string in stock name and looks for gainers
trend:earnings                                        Scans all stocks and returns todays gainers who have consistently good earnings.
trend:streak [<ticker>]                               Determines the current winning/losing streak for a ticker
trend:gainers                                         Grabs todays gainers and checks their earnings.
pricedingold [<ticker>][--timespan=5y][--test=False]  Graphs and assets price in gold.
volume:chase                                          Scans all stocks and returns todays gainers with abnormally high volume.
volume:anomaly                                        Scans all stocks and returns stocks who are accumulating extremely high volume over the last week. Finds market singularities.
vix [<ticker>]                                        Runs the VIX volatility equation on a ticker
```
