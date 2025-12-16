import yfinance as yf

def get_fundamentals(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    fundamentals = {
        'Beta': info.get('beta'),
        'Trailing P/E': info.get('trailingPE'),
        'Forward P/E': info.get('forwardPE'),
        'Market Cap': info.get('marketCap'),
        'EPS (Trailing)': info.get('trailingEps'),
        'Revenue Growth': info.get('revenueGrowth'),
        'Profit Margin': info.get('profitMargins'),
        # Add more as needed
    }
    return fundamentals