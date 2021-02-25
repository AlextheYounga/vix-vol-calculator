# Calculate the *current, up to date* VIX vol index on a ticker of your choosing.

### Author's notes
I followed the VIX whitepaper to the letter and attempted to explain the process throughout the code. The VIX whitepaper is not necessarily the easiest thing to follow, but I'm about 98% certain the math is correct. 

You'll notice the math starts to break down on extremely volatile tickers. I get the impression the CBOE didn't intend to use this on anything but the S&P500. The VIX is supposed to suggest where the SPX will be a month from now, and for SPX, the math works. For example, if the VIX is at 28, that suggests that SPX will be up or down 28 points within 30 days. But if the stock's option prices are absurd, such as using GME (in February 2021), it's possible to see ouput greater than 500.

#### Examples; as of this writing (02-13-2021):
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

# Shopify
python run.py vix SHOP

# VIX: 59.713

# Microsoft
python run.py vix MSFT

# VIX: 26.89

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


### Do it to it:
To run the VIX on a ticker, cd into the root of the project and run the following command. The file run.py is the controlling file here
```
python run.py vix SPY
```



Run this command to view available run.py commands. Currently there's only one so it shouldn't be hard to remember.


```python run.py list```

```
Command                   Description
------------------------  --------------------------------------------
vix [<ticker>] [--debug]  Runs the VIX volatility equation on a ticker
```

