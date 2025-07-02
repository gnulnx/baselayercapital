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
    tickers = YMTickers + list(BitWiseTickers.keys()) + ["MSTR"]

    for ticker in tickers:
        get_yahoo_history(ticker)

        if ticker in YMTickers:
            fetch_yield_max_distributions(ticker)
        elif ticker in BitWiseTickers:
            fetch_bitwise_distributions(ticker, BitWiseTickers[ticker])

    print("All tickers processed successfully.")

    return {"status": "success", "tickers": tickers}
