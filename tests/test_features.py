from pipeline.ingest import MARKET_TICKERS


def test_all_markets_defined():
    for market in ["US", "BR", "UK", "JP"]:
        assert market in MARKET_TICKERS


def test_each_market_has_tickers():
    for market, tickers in MARKET_TICKERS.items():
        assert len(tickers) >= 5, f"{market} has too few tickers"


def test_us_has_major_tickers():
    us = MARKET_TICKERS["US"]
    for ticker in ["AAPL", "MSFT", "NVDA"]:
        assert ticker in us


def test_br_tickers_have_sa_suffix():
    for ticker in MARKET_TICKERS["BR"]:
        assert ticker.endswith(".SA"), f"{ticker} missing .SA suffix"


def test_uk_tickers_have_l_suffix():
    for ticker in MARKET_TICKERS["UK"]:
        assert ticker.endswith(".L"), f"{ticker} missing .L suffix"


def test_jp_tickers_have_t_suffix():
    for ticker in MARKET_TICKERS["JP"]:
        assert ticker.endswith(".T"), f"{ticker} missing .T suffix"
