from bs4 import BeautifulSoup
import requests
import sys
import json
import os


def scrape3mTreasury():
    """
    Scrapes the St Louis Fed website for the current 3m treasury yield.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    url = 'https://fred.stlouisfed.org/series/DTB3'
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    trate = soup.find("span", {"class": "series-meta-observation-value"}).text

    return float(trate)