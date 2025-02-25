import re

from loguru import logger

try:
    import yfinance as yf  # type: ignore
except ImportError as e:
    logger.error("Missing dependency: {}. Please install yfinance with 'pip install yfinance'", e)


class TickerError(Exception):
    """Exception raised for errors in ticker retrieval or processing."""

    def __init__(self, symbol: str, reason: str = "") -> None:
        message = f"Failed to get ticker for {symbol}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


def escape_markdown(text: object | None) -> str:
    """Escape special characters for Telegram MarkdownV2 format.

    Args:
        text: Text to escape, can be None or any type

    Returns:
        Escaped text string, or empty string if input is None
    """
    if text is None:
        return ""

    # Convert to string first
    text_str = str(text)
    pattern = r"([_*\[\]()~`>#+=|{}.!-])"
    return re.sub(pattern, r"\\\1", text_str)


def format_value(value: object) -> str:
    """Format and escape a value for display.

    Args:
        value: Value to format and escape

    Returns:
        Formatted and escaped string ready for Markdown
    """
    return escape_markdown(str(value) if value is not None else "N/A")


def query_tickers(symbols: str | list[str]) -> str:
    """Query multiple ticker symbols and return formatted information.

    Args:
        symbols: Single ticker symbol or list of symbols

    Returns:
        Formatted string with ticker information
    """
    if isinstance(symbols, str):
        symbols = [s.strip() for s in symbols.split(",") if s.strip()]

    symbols = [s.upper().strip() for s in symbols]

    results = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            results.append(format_ticker_info(ticker))
        except Exception as e:
            logger.info("Failed to get ticker for {}, got error: {}", symbol, e)

    return "\n\n".join(results).strip()


def get_info(ticker: yf.Ticker) -> dict:
    """Get ticker information safely.

    Args:
        ticker: yfinance Ticker object

    Returns:
        Dictionary with ticker information

    Raises:
        TickerError: If ticker information cannot be retrieved
    """
    try:
        info = ticker.info
        # Check if we got valid data
        if not info or not isinstance(info, dict):
            raise TickerError(ticker.ticker, "Received empty or invalid data") from None
        return info
    except Exception as e:
        raise TickerError(ticker.ticker, str(e)) from e


def format_ticker_info(ticker: yf.Ticker) -> str:
    """Generate a formatted representation of ticker information.

    Args:
        ticker: yfinance Ticker object

    Returns:
        Formatted string with ticker information
    """
    info = get_info(ticker)

    # Extract basic information
    symbol = info.get("symbol", "Unknown")
    short_name = info.get("shortName", symbol)

    # Extract price information
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

    # Check for essential data
    if all(p is None for p in [open_price, high_price, low_price]):
        raise TickerError(symbol, "Missing essential price data")

    # Calculate derived values
    mid_price = (ask_price + bid_price) / 2 if (ask_price and bid_price) else None
    effective_last_price = last_price if last_price is not None else mid_price

    # Calculate price change
    net_change = 0.0
    if effective_last_price and previous_close:
        net_change = (effective_last_price / previous_close - 1.0) * 100

    # Determine change indicator
    net_change_symbol = "⏸️"
    if net_change > 0:
        net_change_symbol = "🔺"
    elif net_change < 0:
        net_change_symbol = "🔻"

    # Build the formatted output
    return (
        f"📊 *{escape_markdown(short_name)} \\({escape_markdown(symbol)}\\)*\n"
        f"Open: `{format_value(open_price)}`\n"
        f"High: `{format_value(high_price)}`\n"
        f"Low: `{format_value(low_price)}`\n"
        f"Last: `{format_value(effective_last_price)}`\n"
        f"Change: {net_change_symbol} `{escape_markdown(f'{net_change:.2f}%')}`\n"
        f"Volume: `{format_value(volume)}`\n"
        f"52 Week Low: `{format_value(fifty_two_week_low)}`\n"
        f"52 Week High: `{format_value(fifty_two_week_high)}`"
    )
