import os
import mlflow
import mlflow.lightgbm
import lightgbm as lgb
import pandas as pd
import numpy as np
from mlflow.tracking import MlflowClient
from pipeline.ingest import fetch_market_data
from pipeline.features import build_features
from sklearn.metrics import ndcg_score

def build_labels(market_data: dict[str, pd.DataFrame], forward_days: int = 21) -> pd.Series:
    labels = {}
    for ticker, df in market_data.items():
        close = df["Close"]
        if len(close) <= forward_days:
            raise ValueError(f"Ticker {ticker} has insufficient data: {len(close)} rows")
        
        price_now = close.iloc[-1]
        price_21days = close.iloc[-forward_days - 1]
        labels[ticker] = (price_now / price_21days) - 1
    
    return pd.Series(labels)

def train(market: str = 'US'):
    try:
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
        mlflow.set_experiment("quantsignal")
        raw = fetch_market_data(market=market, period="2y")
        features = build_features(raw)
        labels = build_labels(raw)

        labels = labels.reindex(features.index).dropna()
        features = features.loc[labels.index]

        with mlflow.start_run():
            params = {
                "objective": "lambdarank",
                "metric": "ndcg",
                "num_leaves": 31,
                "learning_rate": 0.05,
                "n_estimators": 200,
            }

            mlflow.log_params(params)
            mlflow.log_param("market", market)
            mlflow.log_param("n_tickers", len(features))
            X = features.values
            y = pd.qcut(labels, q=5, labels=False).values.astype(int)
            groups = [len(X)]

            model = lgb.LGBMRanker(**params)
            model.fit(X, y, group=groups)
            preds = model.predict(X)
            ndcg = ndcg_score([y], [preds])
            mlflow.log_metric("ndcg_train", ndcg)
            print(f"NDCG: {ndcg:.4f}")

            model_info = mlflow.lightgbm.log_model(
                model,
                artifact_path="model",
            )
            mlflow.register_model(
                model_uri=model_info.model_uri,
                name="quantsignal-ranker",
            )
    except Exception as e:
        raise RuntimeError(f"Failed to connect to MLFlow: {e}")
    

if __name__ == "__main__":
    train(market="US")