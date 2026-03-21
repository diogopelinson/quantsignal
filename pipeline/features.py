import pandas as pd
import numpy as np
from typing import Dict

from utils.timer.wrapper import timer

def _momentum(close: pd.Series, windown: int) -> float:
    if len(close) < windown:
        return np.nan
    return (close.iloc[-1] / close.iloc[-windown]) - 1
    

def _volatility(close: pd.Series, window: int = 21) -> float:
    returns = close.pct_change().dropna()
    if len(returns) < window:
        return np.nan
    return returns.tail(window).std() * np.sqrt(252)

def _volume_trend(volume: pd.Series, short: int = 5, long: int = 21) -> float:
    if len(volume) < long:
        return np.nan
    return volume.tail(short).mean() / volume.tail(long).mean()

@timer
def build_features(market_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []

    for ticker, df in market_data.items():
        close = df["Close"]
        volume = df["Volume"]

        row ={
            "ticker": ticker,
            "momentum_1m": _momentum(close, 21),
            "momentum_3m": _momentum(close, 63),
            "momentum_6m": _momentum(close, 126),
            "momentum_12m": _momentum(close, 252),
            "volatility_1m": _volatility(close, 21),
            "volatility_3m": _volatility(close, 63),
            "volume_trend": _volume_trend(volume),
            "price_to_52w_high": close.iloc[-1] / close.tail(252).max(),
            "price_to_52w_low": close.iloc[-1] / close.tail(252).min(),
        }
        rows.append(row)

    features = pd.DataFrame(rows).set_index("ticker")
    features = features.dropna()
    # z-score cross-sectional — padrão em quant finance
    features = (features - features.mean()) / features.std()

    return features


if __name__ == "__main__":
    from pipeline.ingest import fetch_market_data

    data = fetch_market_data(market="US", period="2y")
    print(f"tickers retornados: {list(data.keys())}")
    features = build_features(data)
    print(features.shape)
    print(features.head())