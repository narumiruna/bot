from bot.yahoo_finance import query_tickers


def test_query_tickers() -> None:
    s = query_tickers("AAPL")
    assert "AAPL" in s
