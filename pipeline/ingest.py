from typing import Dict
import yfinance as yf
import pandas as pd

from utils.timer.wrapper import timer

MARKET_TICKERS = {
    'US': [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "AVGO", "ORCL", "CRM", "ADBE",
        "CSCO", "ACN", "IBM", "INTC", "AMD", "QCOM", "TXN", "NOW", "INTU", "AMAT",
        "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK",
        "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
        "WMT", "PG", "KO", "PEP", "COST", "MCD", "NKE", "SBUX", "TGT", "HD",
        "XOM", "CVX", "COP", "SLB", "EOG", "PSX",
        "CAT", "GE", "HON", "UPS", "RTX", "BA", "DE", "LMT",
        "PLD", "AMT", "EQIX", "SPG", "PSA", "O"
    ],
    'BR': [
        "PETR4.SA", "PETR3.SA", "PRIO3.SA", "CSAN3.SA", "UGPA3.SA",
        "ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "SANB11.SA", "B3SA3.SA", "BBSE3.SA",
        "ABEV3.SA", "WEGE3.SA", "LREN3.SA", "MGLU3.SA", "RADL3.SA", "RENT3.SA",
        "VALE3.SA", "CSNA3.SA", "GGBR4.SA", "USIM5.SA", "SUZB3.SA",
        "VIVT3.SA", "ELET3.SA", "EQTL3.SA", "CMIG4.SA"
    ],
    'UK': [
        "SHEL.L", "BP.L",
        "HSBA.L", "LLOY.L", "BARC.L", "NWG.L", "STAN.L", "LSEG.L",
        "AZN.L", "GSK.L",
        "ULVR.L", "DGE.L", "RKT.L", "BATS.L",
        "RIO.L", "AAL.L", "GLEN.L", "BA.L", "RR.L", "VOD.L"
    ],
    'JP': [
        "7203.T", "7267.T", "7269.T",
        "6758.T", "6861.T", "6501.T", "6902.T", "6752.T",
        "8306.T", "8316.T", "8411.T", "8766.T",
        "9432.T", "9433.T", "9434.T",
        "9983.T", "7974.T",
        "9984.T", "4502.T", "4503.T"
    ]
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