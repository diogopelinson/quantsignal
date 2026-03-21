from typing import Dict
import yfinance as yf
import pandas as pd

from utils.timer.wrapper import timer

MARKET_TICKERS = {
    'US': ["NVDA", "AAPL", "GOOGL", "GOOG", "MSFT", "AMZN", "TSLA", "BRK-B", "JPM"],
    'BR': ["PETR4.SA", "CSAN3.SA", "ITSA4.SA", "GOLL54.SA", "ABEV3.SA"],
    'UK': ["VOD.L", "LLOY.L", "GLEN.L", "TW.L", "BP.L", "BARC.L", "NWG.L"],
    'JP': ["7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9432.T", "6098.T"]
}

@timer
def fetch_market_data(market: str, period: str) -> Dict[str, pd.DataFrame]:
    tickers = MARKET_TICKERS.get(market, [])

    if not tickers:
        raise ValueError(f"Market '{market}' not supported. Choose from {list(MARKET_TICKERS.keys())}")
    raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    result = {}

    for ticker in tickers:
        #extrai o df
        try:
            df = raw.xs(ticker, axis=1, level=1)[["Open", "High", "Low", "Close", "Volume"]]
            df = df.dropna()
            if len(df) > 20:
                result[ticker] = df
        except KeyError as e:
            print(f"[WARN] ticker {ticker} not found in response, skipping")
    return result
        


if __name__ == "__main__":
    data = fetch_market_data(market="US", period="3mo")
    for ticker, df in data.items():
        print(ticker, df.shape)