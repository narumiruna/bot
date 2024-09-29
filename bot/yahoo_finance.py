import yfinance as yf  # type: ignore
from loguru import logger


def query_tickers(s: str | list[str]) -> str:
    if isinstance(s, str):
        s = [s]
    s = [t.upper().strip() for t in s]

    return "\n".join([ticker_repr(yf.Ticker(t)) for t in s])


def ticker_repr(t: yf.Ticker) -> str:
    symbol = t.info.get("symbol")
    if symbol is None:
        return f"{t.ticker} not found."

    logger.info("symbol: {}, info: {}", symbol, t.info)

    short_name = t.info.get("shortName")

    open_price = t.info.get("open")
    high_price = t.info.get("dayHigh")
    low_price = t.info.get("dayLow")
    current_price = t.info.get("currentPrice")
    previous_close = t.info.get("previousClose")
    fifty_two_week_low = t.info.get("fiftyTwoWeekLow")
    fifty_two_week_high = t.info.get("fiftyTwoWeekHigh")
    ask_price = t.info.get("ask")
    bid_price = t.info.get("bid")

    format_string = f"▪️{short_name}({symbol})"
    format_string += f", Open: {open_price}"
    format_string += f", High: {high_price}"
    format_string += f", Low: {low_price}"

    last_price = None
    # append current price
    if current_price:
        format_string += f", Current: {current_price}"
        last_price = current_price

    # append mid price
    if ask_price and bid_price:
        mid_price = (ask_price + bid_price) / 2
        format_string += f", Mid: {mid_price:.2f}"
        last_price = mid_price

    if last_price and previous_close:
        net_change = last_price - previous_close
        net_change_percentage = net_change / previous_close * 100
        format_string += f", Net Change: {net_change_percentage:.2f}%"

    format_string += f", 52 Week Low: {fifty_two_week_low}"
    format_string += f", 52 Week High: {fifty_two_week_high}"

    return format_string
