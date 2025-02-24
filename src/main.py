from dashboard import dash_app
from stocks import extract_and_insert_data

"""
gapohi 2025.

This is the main script of a project that retrieves stock data from Yahoo Finance and stores it in a MongoDB database. (stocks.py)
MongoDB's data is used to build a dashboard with Dash to visualize the current situation of the selected stocks. (dashboard.py)


!!!Disclaimer on Financial Decisions:!!!

The use of this software and the provided data should not be considered as financial 
advice. No responsibility is assumed for any financial decisions made based on the 
data or results obtained from the software. Users are responsible for conducting their 
own research and making informed decisions.
"""

def main():
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
        "META", "NVDA", "BRK-B", "V", "UNH",
        "JNJ", "WMT", "MA", "PYPL", "DIS",
        "BA", "HD", "PFE", "INTC", "KO", 
        "GS", "IBM", "CVX", "XOM", "ABT", 
        "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", 
        "ADA-USD", "DOGE-USD", "SOL-USD", "XLM-USD"
    ]
    try:
        print('Retrieving and inserting stock data into MongoDB...')
        extract_and_insert_data(tickers)
        print('Launching the Dash app to display the stock dashboard...')
        app = dash_app()
        app.run_server(debug=False)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()