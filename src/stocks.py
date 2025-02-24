import pandas as pd
import requests
import yfinance as yf
from pymongo import MongoClient

def connect_mongodb():
    """
    Connects to MongoDB and returns stocks collection (where Yahoo Finance data will be inserted).
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["yfinance"]
        collection = db["stocks"]
        collection.delete_many({}) ## clear the stocks collection previous data
        return collection
    except Exception as e:
        raise RuntimeError(f"Error connecting to MongoDB: {e}")

def usd_to_eur_conversion():
    """
    Obtains the exchange rate from USD to EUR.
    """
    try:
        usd_eur = yf.download("EURUSD=X", period="1d", interval="1d")
        return usd_eur['Close'].iloc[-1].item()
    except Exception as e:
        raise RuntimeError(f"Error converting usd to eur: {e}")
    
def get_logo_url(ticker):
    """
    Gets the company URL logo from a Clearbit Http request and returns it for the selected stock ticker.
    """
    company_domains = {
        "AAPL": "apple.com", "MSFT": "microsoft.com", "GOOGL": "google.com", "AMZN": "amazon.com",
        "TSLA": "tesla.com", "META": "meta.com", "NVDA": "nvidia.com", "BRK-B": "berkshirehathaway.com",
        "V": "visa.com", "UNH": "unitedhealthgroup.com", "JNJ": "jnj.com", "WMT": "walmart.com",
        "MA": "mastercard.com", "PYPL": "paypal.com", "DIS": "thewaltdisneycompany.com", "BA": "boeing.com",
        "HD": "homedepot.com", "PFE": "pfizer.com", "INTC": "intel.com", "KO": "coca-cola.com",
        "GS": "goldmansachs.com", "IBM": "ibm.com", "CVX": "chevron.com", "XOM": "exxonmobil.com",
        "ABT": "abbott.com", "BTC-USD": "bitcoin.org", "ETH-USD": "ethereum.org", "BNB-USD": "binance.org",
        "XRP-USD": "ripple.com", "ADA-USD": "cardano.org", "DOGE-USD": "dogecoin.com", "SOL-USD": "solana.com",
        "XLM-USD": "stellar.org"
    }
    try:
        domain = company_domains.get(ticker)
        if domain:
            url = f"https://logo.clearbit.com/{domain}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return url
        print(f"Company domain not found for ticker: {ticker}")
        return 'N/A'
    except Exception as e:
        raise RuntimeError(f"Http request error while getting the {ticker} URL logo: {e}")

def create_document(ticker, usd_to_eur):
    """
    Creates the document to be inserted in the MongoDB with stock information extracted from Yahoo Finance.
    """
    try:
        ## obtain data (price, volume), for the last 10 days at 1-day intervals
        data = yf.download(ticker, period="10d", interval="1d")

        ## close prices for the last 5 days in eur
        ## get the last 5 closing prices, filling missing values with None if there is not enough data
        close_prices = (
            data['Close']
            .astype(float)
            .round(2)
            .reindex(data.index[-5:], fill_value=None)
            .to_numpy()
            .flatten()
            .tolist()
        )

        ## convert prices from usd to eur, rounding to two decimal places and handling None values
        close_prices_eur = [round(price / usd_to_eur, 2) if price is not None else None for price in close_prices]

        ## unpack the converted prices into individual variables
        close_today_eur, close_yesterday_eur, close_2_eur, close_3_eur, close_4_eur = close_prices_eur

        ## price change % from yesterday and moving average from last 5 days
        yesterday_price_change = round(((close_today_eur - close_yesterday_eur) / close_yesterday_eur) * 100, 2) if close_yesterday_eur is not None else None
        close_moving_avg_5d = round(float(data['Close'].tail(5).mean().iloc[0]) / usd_to_eur, 2) if len(data['Close']) >= 5 else None

        ## price open, low and high today in eur
        if len(data) > 0:
            open_today_eur, low_today_eur, high_today_eur = (
                data.iloc[-1][['Open', 'Low', 'High']].astype(float).div(usd_to_eur).round(2).tolist()
            )
        else:
            open_today_eur = low_today_eur = high_today_eur = None

        ## get the last 5 volume values, filling missing values with None if there is not enough data
        volume_values = (
            data['Volume']
            .astype(float)
            .reindex(data.index[-5:], fill_value=None)
            .to_numpy()
            .flatten()
            .tolist()
        )

        ## unpack the volume values into individual variables
        today_volume, yesterday_volume, volume_2, volume_3, volume_4 = volume_values

        ## volume change % from yesterday
        yesterday_volume_change = round(((today_volume - yesterday_volume) / yesterday_volume) * 100, 2) if yesterday_volume is not None else None

        ## company info
        ticker_obj = yf.Ticker(ticker)
        ticker_info = ticker_obj.info
        company_name = ticker_info.get('shortName', 'N/A')
        company_logo_url = get_logo_url(ticker)
        high_52wk_eur = round(ticker_info.get('fiftyTwoWeekHigh', 0) / usd_to_eur, 2)
        low_52wk_eur = round(ticker_info.get('fiftyTwoWeekLow', 0) / usd_to_eur, 2)

        ## news
        news = ticker_obj.news[:2] if ticker_obj.news else None
        news_titles = [
            f"{article['content'].get('title', 'No title available')}: {article['content'].get('summary', 'No summary available')[:200]}"
            for article in news
        ] if news else ["No recent news available for this ticker."]

        ## analyst recommendation
        recommendation = ticker_info.get('recommendationKey', 'N/A')

        ## json document to be inserted in MongoDB
        document = {
            "ticker": ticker.replace('-USD',''),
            "date": pd.to_datetime('today').strftime('%Y-%m-%d'),
            "company_name": company_name.replace(' USD',''),
            "company_logo_url": company_logo_url,
            "price": {
                "open_today": open_today_eur,
                "low_today": low_today_eur,
                "high_today": high_today_eur,
                "low_52wk": low_52wk_eur,
                "high_52wk": high_52wk_eur,
                "close_today": close_today_eur,
                "close_yesterday": close_yesterday_eur,
                "close_2": close_2_eur,
                "close_3": close_3_eur,
                "close_4": close_4_eur,
                "close_moving_avg_5d": close_moving_avg_5d,
                "yesterday_change": yesterday_price_change
            },
            "volume": {
                "close_today": today_volume,
                "close_yesterday": yesterday_volume,
                "close_2": volume_2,
                "close_3": volume_3,
                "close_4": volume_4,
                "yesterday_change": yesterday_volume_change
            },
            "news": news_titles,
            "analyst_recommendation": recommendation
        }
        return document
    except Exception as e:
        raise RuntimeError(f"{ticker} Error creating the MongoDB document with YFinance data: {e}")

def extract_and_insert_data(tickers):
    """
    Extracts data from Yahoo Finance and inserts it in MongoDB.
    """
    collection = connect_mongodb()
    usd_to_eur = usd_to_eur_conversion()
    documents = []
    for ticker in tickers:
        print(f"Processing {ticker}...")
        document = create_document(ticker, usd_to_eur)
        documents.append(document)
    collection.insert_many(documents)
    print("Data successfully inserted into MongoDB")