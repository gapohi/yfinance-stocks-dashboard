import yfinance as yf
ticker = 'AAPL'
data = yf.download(ticker, period="10d", interval="1d")
#print(data)
#print(data.info())

print(yf.Ticker(ticker).info)


"""
amzn = yf.Ticker(ticker)
#print(amzn.news)

articles = amzn.news[:3]

for article in articles:
    title = article['content']['title']
    summary = article['content']['summary']
    print(f"Title: {title}")
    print(f"Summary: {summary[0:200]}")
    print("----")
"""