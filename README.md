# Calculate the *current, up to date* VIX vol index on a ticker of your choosing.

### Author's notes
I followed the VIX whitepaper to the letter and attempted to explain the process throughout the code. The VIX whitepaper is not necessarily the easiest thing to follow, but I'm about 98% certain the math is correct. 

Be aware that some tickers have issues, I'm not entirely sure why yet. It's either because TD Ameritrade's API isn't always 
consistent or because some option chains are just too small to run the VIX on (this is my guess). I haven't had the time to look into it, but I will eventually find out why. 

**Generally speaking, penny stocks don't work yet.**

Also, you'll notice the math starts to break down on extremely volatile tickers, for reasons I don't entirely understand yet. I get the impression the CBOE didn't intend to use this on anything but the S&P500. 

In my personal opinion, some of the conceptual logic behind the final VIX equation is pretty weak. I think their process for which option contracts to use is pretty interesting and makes sense to me, and the standard deviation equation they use is pretty cool. But when it's all said and done, the final VIX calculation that all of these variables get tossed into feels like it ruins the party. It becomes a soup of multiplying/dividing datetimes in such a way that truly only a genius could understand.

All that being said, it doesn't matter if their logic is correct. All the fintech algorithms use the VIX, making it correct. 
And I learned a lot making this, and will certainly use parts of CBOE's VIX process in the future.

#### The math seems to come to reasonable conclusions on a lot of big name stocks. 
#### For example, as of this writing (02-13-2021):
```
# SPDR S&P500 ETF Trust
python run.py vix SPY

# VIX: 19.988 
# Despite using the ETF $SPY, the VIX still mirrors that of the real S&P range 
# because the option prices on SPY and the S&P500 are so similar.
# True VIX close as reported by Google 02-13-2021: 19.97

# Apple
python run.py vix AAPL

# VIX: 33.394

# General Motors
python run.py vix GM

# VIX: 52.29

#Now here's where the math starts to break down.
#Gamestop
python run.py vix GME

# VIX: 8998.274
# As of this writing, we're about two weeks out from the historic Gamestop short squeeze. 

```

## Technical Details:

### Installing Python, (the right way). If you're a complete beginner, this short 7 minute video will help answer a lot of your initial questions:
https://www.youtube.com/watch?v=28eLP22SMTA

### Step 1 Free TD Ameritrade API Key:
Acquire a TD Ameritrade api key. They are free and easy to acquire. Click register, fill out the form, and grab the "Consumer Key" they give you after verifying your account.
https://developer.tdameritrade.com/authentication/apis

### Step 2 ENV:
To the beginner, this is where you will put your sensitive information, (like your API keys).
Create a file called ```.env``` in the root project folder and place this in it:
(Check out the .env.example file for help)
```
TDAMER_KEY=somevalue
```

### Step 3 Packages:
Run ```pip list -r requirements.txt```


### Step 4 Do it to it:
To run the VIX on a ticker:
```
python run.py vix SPY
```



Run this command to view available commands. Currently there's only one so it shouldn't be hard to remember.


```python run.py list```

```
Command                   Description
------------------------  --------------------------------------------
vix [<ticker>] [--debug]  Runs the VIX volatility equation on a ticker
```

