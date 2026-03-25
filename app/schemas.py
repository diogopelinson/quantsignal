from pydantic import BaseModel


class StockSignal(BaseModel):
    ticker: str
    score: float
    rank: int
    market: str

class SignalsResponse(BaseModel):
    signals: list[StockSignal]
    model_version: str
    market: str
    top_n: int
    last_trained: str

class FeatureContribution(BaseModel):
    feature: str
    value: float
    contribution: float

class ExplainResponse(BaseModel):
    ticker: str
    score: float
    contributions: list[FeatureContribution]
    summary: str

class ModelInfoResponse(BaseModel):
    model_name: str
    version: str
    stage: str
    last_trained: str
    metrics: dict[str, float]