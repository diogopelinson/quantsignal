import pandas as pd


def validate_features(features: pd.DataFrame) -> bool:
    assert not features.empty, "Feature matrix is empty"
    assert features.isnull().sum().sum() == 0, "Feature matrix contains NaN values"
    assert len(features) >= 10, f"Too few tickers to train: {len(features)}"

    for col in features.columns:
        assert features[col].std() > 0, f"Feature '{col}' has zero variance"

    return True