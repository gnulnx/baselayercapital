from fetch_symbol_div_info import (
    get_yahoo_history,
    fetch_yield_max_distributions,
    fetch_bitwise_distributions,
    init_env,
)

YMTickers = ["MSTY"]
BitWiseTickers = {
    "IMST": "https://imstetf.com/",
}


def handler(event=None, context=None):
    init_env()
    tickers = YMTickers + list(BitWiseTickers.keys())

    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        get_yahoo_history(ticker)

        if ticker in YMTickers:
            fetch_yield_max_distributions(ticker)
        elif ticker in BitWiseTickers:
            fetch_bitwise_distributions(ticker, BitWiseTickers[ticker])

    return {"status": "success", "tickers": tickers}
