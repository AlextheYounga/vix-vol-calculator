# Vix Volatility Calculator
## Calculate the *current* VIX vol index on any ticker of your choosing.
![Screenshot 2022-12-08 at 4 45 50 PM](https://user-images.githubusercontent.com/20220366/206574035-3b5ab371-cede-4d21-afb1-c7f69676adc2.png)

## October 2023 Update: TD Ameritrade being lame
This repo is built upon the TD Ameritrade API, which has put accepting new API registrations on hold as they migrate over to a Charles Schwab API. I am not looking forward to rewriting the code to parse ~10MB option chain responses, but I will.

I am looking for alternative sources for this as I begin converting this repo into a pip package. I'm not entirely confident Schwab will be as cool as TD Ameritrade was in letting basically anyone ping their servers for 10MB responses with virtually no limit.

Please check back later. I am actively working on this.  

- [Vix Volatility Calculator](#vix-volatility-calculator)
  - [Calculate the *current* VIX vol index on any ticker of your choosing.](#calculate-the-current-vix-vol-index-on-any-ticker-of-your-choosing)
  - [October 2023 Update: TD Ameritrade being lame](#october-2023-update-td-ameritrade-being-lame)
  - [Author's notes](#authors-notes)
  - [Caveats](#caveats)
    - [TD Ameritrade](#td-ameritrade)
    - [Only stocks with option contracts](#only-stocks-with-option-contracts)
  - [Examples](#examples)
    - [Alternative Stocks](#alternative-stocks)
      - [Apple](#apple)
      - [Shopify](#shopify)
      - [Microsoft](#microsoft)
  - [Caching](#caching)
  - [Getting Started:](#getting-started)
    - [Beginners: Installing Python, (the right way)](#beginners-installing-python-the-right-way)
    - [Step 1 Free TD Ameritrade API Key (Deprecated):](#step-1-free-td-ameritrade-api-key-deprecated)
    - [Step 2 ENV:](#step-2-env)
    - [Step 3 Packages:](#step-3-packages)
  - [Run:](#run)



## Author's notes
I followed the VIX whitepaper to the letter and attempted to explain the process throughout the code. I'm 99% certain the math is correct. 

The math starts to break down on extremely volatile tickers. I get the impression the CBOE didn't intend to use this on anything but the S&P500. However, for stocks with average volatility, you get surprisingly accurate and interesting results using this equation.

The VIX is supposed to suggest a possible range of where the SPX will be a month from now, i.e., if the VIX is at 28, that suggests that SPX will be up or down 28 points within 30 days. For the S&P it's surprisingly accurate.

But if a stock's option prices are absurd, (such as $GME in February 2021), it's possible to see output greater than 500. 
What I've found when experimenting with this equation is that this number seems to be a good measure of potential energy, with a higher output generally meaning there is greater potential movement. 

## Caveats
### TD Ameritrade
This equation requires using a TD Ameritrade API key, which unfortunately is on hold as they transition to a new Charles Schwab API. Please see update message above.
### Only stocks with option contracts
**This equation will only work if the stock has an option contract that expires within the next 3 months**. Lower volume stocks may only have a few expirations per year, or every 6 months. If that's the case, the code will fail, because the VIX equation was never designed to calculate more than a month ahead. I tweaked the equation to allow for up to 3 months. 


## Examples
*(as of this writing: 02-13-2021)*

**VIX Close 02-13-2021:** `19.97`

**SPDR S&P500 ETF Trust (SPY):**
```
python run.py vix SPY
=> VIX: 19.988 
```
Despite using the ETF $SPY, the VIX still mirrors that of the real S&P VIX value because the option prices on SPY and the S&P500 are so similar. 

### Alternative Stocks

#### Apple
```
python run.py vix AAPL
=> VIX: 33.394
```

#### Shopify
```
python run.py vix SHOP
=> VIX: 59.713
```

#### Microsoft
```
python run.py vix MSFT
=> VIX: 26.89
```

## Caching
Option chain responses are unusually large- ~10MB json response for every requested ticker. To help save resources, I automatically cache the chain response for one day. You can turn this off if you need perfectly accurate responses to the second, by setting `Vix(enable_caching=false)`. As I convert this to a pip package, this will be one of the options users can easily pass in the params. 

I also scrape the current 3m treasury rate from the Federal Reserve's website and cache this rate for one day, but this datapoint is only updated daily anyway. 

These are stored under `storage/cache/`


## Getting Started:
### Beginners: Installing Python, (the right way)
I have shared this repo with many people who are not as technically inclined. I am hoping this helps them get started. 
If you're a complete beginner, this short 7 minute video will help answer a lot of your initial questions:
https://www.youtube.com/watch?v=28eLP22SMTA

### Step 1 Free TD Ameritrade API Key (Deprecated):
>Acquire a TD Ameritrade api key. They (were) free and easy to acquire. Click register, fill out the form, and grab the "Consumer Key" they give you after verifying your account.

The TD Ameritrade API has put new registrations on hold for the moment, please see 2023 update message. I am looking for alternatives. Please check back later. 
https://developer.tdameritrade.com/authentication/apis

### Step 2 ENV:
To the beginner, this is where you will put your sensitive information, (like your API keys).
Create a file called ```.env``` in the root project folder and place this in it:
(Check out the .env.example file for help)
```
TDAMER_KEY=somevalue
```

### Step 3 Packages:
Run ```pip install -r requirements.txt```


## Run:
To run the VIX on a ticker, cd into the root of the project and run the following command. The file run.py is the CLI file here
```
python run.py vix SPY
```
