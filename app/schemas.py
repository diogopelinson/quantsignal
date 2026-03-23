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