import re

from loguru import logger

try:
    import yfinance as yf  # type: ignore
except ImportError as e:
    logger.error("{}. Please install yfinance by running 'pip install yfinance'", e)


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


def query_tickers(s: str | list[str]) -> str:
    if isinstance(s, str):
        s = [s]
    s = [t.upper().strip() for t in s]

    return "\n".join([ticker_repr(yf.Ticker(t)) for t in s])


def ticker_repr(t: yf.Ticker) -> str:
    symbol = t.info.get("symbol")
    if symbol is None:
        return f"{t.ticker} not found."

    short_name = t.info.get("shortName")
    open_price = t.info.get("open")
    high_price = t.info.get("dayHigh")
    low_price = t.info.get("dayLow")
    last_price = t.info.get("currentPrice")
    previous_close = t.info.get("previousClose")
    fifty_two_week_low = t.info.get("fiftyTwoWeekLow")
    fifty_two_week_high = t.info.get("fiftyTwoWeekHigh")
    ask_price = t.info.get("ask")
    bid_price = t.info.get("bid")
    volume = t.info.get("volume")

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
    )
