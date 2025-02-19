import requests

# Lista de tickers
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "V", "UNH",
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "SOL-USD", "XLM-USD"
]

# Función para obtener el logo de la empresa a partir del dominio
def get_logo_via_clearbit(domain):
    url = f"https://logo.clearbit.com/{domain}"
    response = requests.get(url)
    if response.status_code == 200:
        return url
    return None

# Diccionario de dominios de empresas/criptomonedas
company_domains = {
    "AAPL": "apple.com",
    "MSFT": "microsoft.com",
    "GOOGL": "google.com",
    "AMZN": "amazon.com",
    "TSLA": "tesla.com",
    "META": "meta.com",
    "NVDA": "nvidia.com",
    "BRK-B": "berkshirehathaway.com",
    "V": "visa.com",
    "UNH": "unitedhealthgroup.com",
    "BTC-USD": "bitcoin.org",  # Bitcoin no tiene una página oficial como tal, pero se puede usar este
    "ETH-USD": "ethereum.org",
    "BNB-USD": "binance.org",
    "XRP-USD": "ripple.com",
    "ADA-USD": "cardano.org",
    "DOGE-USD": "dogecoin.com",
    "SOL-USD": "solana.com",
    "XLM-USD": "stellar.org"
}

# Obtener logos para todas las empresas/criptomonedas
logos = {}
for ticker in tickers:
    domain = company_domains.get(ticker)
    if domain:
        logo_url = get_logo_via_clearbit(domain)
        logos[ticker] = logo_url

# Mostrar los resultados
for ticker, logo in logos.items():
    if logo:
        print(f"{ticker}: {logo}")
    else:
        print(f"{ticker}: No logo found.")