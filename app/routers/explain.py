from fastapi import APIRouter, HTTPException, Request
from app.schemas import ExplainResponse, FeatureContribution
from pipeline.ingest import fetch_market_data
from pipeline.features import build_features
import shap

router = APIRouter()

@router.get("/{ticker}", response_model=ExplainResponse)
def get_explanation(ticker: str, request: Request):
    try:
        model = request.app.state.model
        raw = fetch_market_data(market="US", period="2y")
        features = build_features(raw)

        if ticker not in features.index:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

        X = features.loc[[ticker]]
        score = float(model.predict(X.values)[0])

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        contributions = [
            FeatureContribution(
                feature=col,
                value=round(float(X[col].iloc[0]), 4),
                contribution=round(float(shap_values[0][i]), 4),
            )
            for i, col in enumerate(features.columns)
        ]
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)

        top = contributions[0]
        summary = f"Score driven mainly by {top.feature} (contribution: {top.contribution:+.3f})"

        return ExplainResponse(
            ticker=ticker.upper(),
            score=round(score, 4),
            contributions=contributions,
            summary=summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))