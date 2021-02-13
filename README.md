This will calculate the *current, up to date* VIX vol index on a ticker. I followed the VIX whitepaper to the letter and attempted to explain the process throughout the code. The VIX whitepaper is not necessarily the easiest thing to follow, but I'm about 90% certain the math is correct. 


Be aware that some tickers have issues, I'm not entirely sure why yet. It's either because TD Ameritrade's API isn't always 
consistent or because some option chains are just too small to run the VIX on, (I haven't had the time to look into it, but I will eventually find out why.) Generally speaking, penny stocks won't work. 

Also, you'll notice the math starts to break down on extremely volatile tickers. I think the option prices get so crazy that the math just doesn't work the same. To the best I can figure, the math was specifically geared to create an index representation of *specifically* the S&P500 and not much else. 

That being said, the math does seem to come to reasonable conclusions on a lot of big name stocks. 
For example, as of this writing (02-13-2021):
```
#SPDR S&P500 ETF Trust
python run.py vix SPY
#VIX: 19.988 
# Despite using the ETF $SPY, the VIX still mirrors that of the real S&P range because the option prices on SPY and the S&P500
# are so similar.

#Apple
python run.py vix AAPL
#VIX: 33.394

#General Motors
python run.py vix GM
#VIX: 52.29

#Now here's where the math starts to break down.

#Gamestop
python run.py vix GME
#VIX: 8998.274
# As of this writing, this is about a week and a half out from the historic Gamestop short squeeze. 

```

Technical Details:

Must have a TD Ameritrade api key. They are free and easy to acquire.
https://developer.tdameritrade.com/option-chains/apis/get/marketdata/chains

Help installing Python (the right way):
https://www.youtube.com/watch?v=28eLP22SMTA


Make sure to run ```pip list -r requirements.txt```

Check out the .env.example file.

```
TDAMER_KEY=somevalue
```

Run this command to view available commands. Currently there's only one so it shouldn't be hard to remember.


```python run.py list```

```


```
Command                   Description
------------------------  --------------------------------------------
vix [<ticker>] [--debug]  Runs the VIX volatility equation on a ticker
```

To run the VIX on a ticker:
```
python run.py vix SPY

 (as of 2021)

python run.py vix AAPL

#output
```



