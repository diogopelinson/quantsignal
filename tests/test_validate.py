import numpy as np
import pandas as pd
import pytest

from pipeline.validate import validate_features


def _make_valid_features(n=15) -> pd.DataFrame:
    np.random.seed(42)
    data = np.random.randn(n, 9)
    cols = [
        "momentum_1m", "momentum_3m", "momentum_6m", "momentum_12m",
        "volatility_1m", "volatility_3m", "volume_trend",
        "price_to_52w_high", "price_to_52w_low",
    ]
    tickers = [f"TICK{i}" for i in range(n)]
    return pd.DataFrame(data, index=tickers, columns=cols)


def test_valid_features_passes():
    features = _make_valid_features()
    assert validate_features(features) is True


def test_empty_dataframe_raises():
    with pytest.raises(AssertionError, match="empty"):
        validate_features(pd.DataFrame())


def test_too_few_tickers_raises():
    features = _make_valid_features(n=5)
    with pytest.raises(AssertionError, match="Too few"):
        validate_features(features)


def test_nan_values_raises():
    features = _make_valid_features()
    features.iloc[0, 0] = np.nan
    with pytest.raises(AssertionError, match="NaN"):
        validate_features(features)


def test_zero_variance_raises():
    features = _make_valid_features()
    features["momentum_1m"] = 0.0
    with pytest.raises(AssertionError, match="zero variance"):
        validate_features(features)