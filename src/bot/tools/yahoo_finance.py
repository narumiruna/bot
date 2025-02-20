import re

from loguru import logger

try:
    import yfinance as yf  # type: ignore
except ImportError as e:
    logger.error("{}. Please install yfinance by running 'pip install yfinance'", e)


class TickerError(Exception):
    def __init__(self, symbol: str) -> None:
        super().__init__(f"Failed to get ticker for {symbol}")


def escape_markdown(text: str | None) -> str:
    """Escape special characters for Telegram MarkdownV2 format.

    Args:
        text: Text to escape, can be None

    Returns:
        Escaped text string, or empty string if input is None
    """
    if text is None:
        return ""

    pattern = r"([_*\[\]()~`>#+=|{}.!-])"
    return re.sub(pattern, r"\\\1", text)


def query_tickers(symbols: str | list[str]) -> str:
    if isinstance(symbols, str):
        symbols = [symbols]
    symbols = [s.upper().strip() for s in symbols]

    results = []
    for symbol in symbols:
        try:
            results += [ticker_repr(yf.Ticker(symbol))]
        except TickerError as e:
            logger.info("Failed to get ticker for {}, got error: {}", symbol, e)
            continue

    return "\n".join(results).strip()


def get_info(t: yf.Ticker) -> dict:
    try:
        info = t.info
    except Exception as e:
        raise TickerError(f"{t.ticker}, got {e}") from e
    return info


def ticker_repr(t: yf.Ticker) -> str:
    info = get_info(t)

    symbol = info.get("symbol")
    short_name = info.get("shortName")
    open_price = info.get("open")
    high_price = info.get("dayHigh")
    low_price = info.get("dayLow")
    last_price = info.get("currentPrice")
    previous_close = info.get("previousClose")
    fifty_two_week_low = info.get("fiftyTwoWeekLow")
    fifty_two_week_high = info.get("fiftyTwoWeekHigh")
    ask_price = info.get("ask")
    bid_price = info.get("bid")
    volume = info.get("volume")

    if open_price is None and high_price is None and low_price is None:
        raise TickerError(symbol or "")

    mid_price = (ask_price + bid_price) / 2 if ask_price and bid_price else None

    effective_last_price = last_price if last_price is not None else mid_price

    net_change = (
        ((effective_last_price / previous_close - 1.0) * 100) if effective_last_price and previous_close else 0.0
    )
    net_change_symbol = "🔺" if net_change > 0 else "🔻" if net_change < 0 else "⏸️"

    return (
        f"📊 *{escape_markdown(short_name)} \\({escape_markdown(symbol)}\\)*\n"
        f"Open: `{escape_markdown(f'{open_price}')}`\n"
        f"High: `{escape_markdown(f'{high_price}')}`\n"
        f"Low: `{escape_markdown(f'{low_price}')}`\n"
        f"Last: `{escape_markdown(f'{effective_last_price}')}`\n"
        f"Change: {net_change_symbol} `{escape_markdown(f'{net_change:.2f}%')}`\n"
        f"Volume: `{escape_markdown(f'{volume}')}`\n"
        f"52 Week Low: `{escape_markdown(f'{fifty_two_week_low}')}`\n"
        f"52 Week High: `{escape_markdown(f'{fifty_two_week_high}')}`\n"
    ).strip()
