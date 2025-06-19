from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression


def get_nasdaq_history(ticker):
    today = datetime.now().strftime("%Y-%m-%d")
    url = (
        f"https://api.nasdaq.com/api/quote/{ticker}/historical"
        f"?assetclass=etf&fromdate=2015-06-19&todate={today}&limit=9999"
    )
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.nasdaq.com/market-activity/etf/{ticker.lower()}/historical",
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch data: {r.status_code}")
    rows = r.json()["data"]["tradesTable"]["rows"]
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df["close"] = pd.to_numeric(df["close"].str.replace(",", ""))
    df = df.sort_values("date")
    return df[["date", "close"]]


def plot_nav_trend(prices, years_forward=3):
    df = prices.copy()
    df["months"] = (df["date"] - df["date"].min()).dt.days / 30.44
    X = df["months"].values.reshape(-1, 1)
    y = df["close"].values

    model = LinearRegression().fit(X, y)
    trend = model.predict(X)
    r2 = model.score(X, y)

    slope = model.coef_[0]
    intercept = model.intercept_

    print("\n=== Price Summary ===")
    print(df["close"].describe())
    print(f"\nRegression Slope: {slope:.5f}")
    print(f"Regression Intercept: {intercept:.2f}")
    print(f"R²: {r2:.3f}")
    print(f"Start Date: {df['date'].min()}, End Date: {df['date'].max()}")
    print(
        f"Start Price: {df['close'].iloc[0]:.2f}, End Price: {df['close'].iloc[-1]:.2f}"
    )
    print(f"Observed Duration: {df['months'].iloc[-1]:.2f} months")

    # === Rolling 30-Day Mean ===
    df["rolling30"] = df["close"].rolling(window=30).mean()

    # === Trendline Projection ===
    months_future = int(years_forward * 12)
    last_month = df["months"].iloc[-1]
    future_months = np.arange(last_month + 1, last_month + months_future + 1)
    future_dates = [
        df["date"].max() + pd.DateOffset(months=i) for i in range(1, months_future + 1)
    ]
    future_trend = model.predict(future_months.reshape(-1, 1))

    # === Plot NAV trend ===
    plt.figure(figsize=(14, 6))
    plt.plot(df["date"], df["close"], "bo", markersize=3, label="Close Price")
    plt.plot(df["date"], df["rolling30"], "k-", label="30-Day Rolling Avg")
    plt.plot(df["date"], trend, "r--", label=f"Trendline (R²={r2:.3f})")
    plt.plot(
        future_dates,
        future_trend,
        "g--",
        label=f"Trendline Projection ({years_forward}y)",
    )

    plt.xlabel("Date")
    plt.ylabel("NAV / Close Price")
    plt.title(f"{ticker} NAV Trend, R², and {years_forward}-Year Projection")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # === Histogram of Close Prices ===
    plt.figure(figsize=(10, 4))
    df["close"].hist(bins=25, edgecolor="black")
    plt.title(f"{ticker} Price Distribution")
    plt.xlabel("Close Price")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    import sys

    ticker = sys.argv[1] if len(sys.argv) > 1 else "MSTY"
    print(f"Fetching price history for {ticker}...")
    prices = get_nasdaq_history(ticker)
    print(prices.tail())

    print("Plotting NAV trend and projection...")
    plot_nav_trend(prices, years_forward=3)
