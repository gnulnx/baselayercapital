import argparse
from decimal import Decimal
from datetime import datetime, UTC
import boto3
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

ENV_NAME = os.getenv("ENV_NAME", "dev")

HistoricalDataTableName = f"{ENV_NAME}-HistoricalData"


def init_env():
    global ENV_NAME, AWS_REGION, HistoricalDataTable, HistoricalDataTableName

    ENV_NAME = os.getenv("ENV_NAME", "dev")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    HistoricalDataTableName = f"{ENV_NAME}-HistoricalData"

    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    HistoricalDataTable = dynamodb.Table(HistoricalDataTableName)

    print(f"✅ Using DynamoDB table: {HistoricalDataTableName} in {AWS_REGION}")


def now_utc_iso() -> str:
    return datetime.now(UTC).isoformat()


def get_yahoo_history(ticker: str) -> pd.DataFrame:
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(period="max", auto_adjust=False)

    df = df.reset_index()
    df.columns = [col.lower().replace(" ", "") for col in df.columns]
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    write_to_dynamo(df, ticker=ticker, sk_prefix="PRICE#")
    return df


def write_to_dynamo(df: pd.DataFrame, ticker: str, ts: str, sk_prefix: str = "PRICE#"):
    with HistoricalDataTable.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as batch:
        for _, row in df.iterrows():
            if pd.isna(row["close"]):
                continue

            date_str = row["date"].strftime("%Y-%m-%d")
            item = {
                "PK": ticker,
                "SK": f"{sk_prefix}{date_str}",
                "last_updated": ts,
                "open": Decimal(str(row["open"])) if not pd.isna(row["open"]) else None,
                "high": Decimal(str(row["high"])) if not pd.isna(row["high"]) else None,
                "low": Decimal(str(row["low"])) if not pd.isna(row["low"]) else None,
                "close": Decimal(str(row["close"])),
                "adjclose": Decimal(str(row["adjclose"]))
                if not pd.isna(row["adjclose"])
                else None,
                "volume": int(row["volume"]) if not pd.isna(row["volume"]) else None,
                "dividend": Decimal(str(row["dividends"]))
                if not pd.isna(row["dividends"])
                else None,
                "stocksplits": Decimal(str(row["stocksplits"]))
                if not pd.isna(row["stocksplits"])
                else None,
                "capitalgains": Decimal(str(row["capitalgains"]))
                if not pd.isna(row["capitalgains"])
                else None,
            }

            # Remove any None values for a clean DynamoDB write
            item = {k: v for k, v in item.items() if v is not None}

            batch.put_item(Item=item)

    print(f"Wrote {len(df)} items to {HistoricalDataTableName}.")


def fetch_yield_max_distributions(ticker: str, ts: str) -> pd.DataFrame:
    """
    Scrapes YieldMax distribution table from the given URL and returns a DataFrame.
    """
    source = f"https://www.yieldmaxetfs.com/our-etfs/{ticker}/"
    response = requests.get(source)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find table by matching column headers
    tables = soup.find_all("table")
    target_table = None

    for table in tables:
        headers = [th.text.strip().lower() for th in table.find_all("th")]
        # print(headers)
        # input()
        if (
            "distribution per share" in headers
            and "declared date" in headers
            and "ex date" in headers
            and "record date" in headers
            and "payable date" in headers
        ):
            target_table = table
            break

    if not target_table:
        raise ValueError("Could not find distribution table on page.")

    rows = target_table.find("tbody").find_all("tr")
    records = []

    for row in rows:
        cols = [td.text.strip() for td in row.find_all("td")]
        if len(cols) < 6:
            continue

        _, amount, declared, ex, record, payable = cols
        try:
            records.append(
                {
                    "ticker": ticker,
                    "amount": float(amount),
                    "last_updated": ts,
                    "declared_date": pd.to_datetime(declared).strftime("%Y-%m-%d"),
                    "ex_date": pd.to_datetime(ex).strftime("%Y-%m-%d"),
                    "record_date": pd.to_datetime(record).strftime("%Y-%m-%d"),
                    "payable_date": pd.to_datetime(payable).strftime("%Y-%m-%d"),
                }
            )
        except Exception as e:
            print(f"⚠️ Skipping row: {cols} ({e})")

    df = pd.DataFrame(records)

    with HistoricalDataTable.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as batch:
        for _, row in df.iterrows():
            if pd.isna(row["amount"]) or row["amount"] <= 0:
                print(f"⚠️ Skipping row with invalid amount: {row['amount']}")
                # input("Press Enter to continue...")
                continue

            item = {
                "PK": ticker,
                "SK": f"DIST#{row['declared_date']}",
                "amount": Decimal(str(row["amount"])),
                "declared_date": row["declared_date"],
                "ex_date": row["ex_date"],
                "record_date": row["record_date"],
                "payable_date": row["payable_date"],
            }

            # Remove any None values for a clean DynamoDB write
            item = {k: v for k, v in item.items() if v is not None}

            batch.put_item(Item=item)

    return pd.DataFrame(records)


def fetch_bitwise_distributions(ticker: str, url: str, ts: str) -> pd.DataFrame:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Narrow to only the main distributions section
    root = soup.find("div", id="distributions")
    if not root:
        print("❌ Could not find #distributions section.")
        return pd.DataFrame()

    root = soup.find("div", id="distributions")

    # Filter only divs with exactly 5 inner divs (data rows)
    records = []
    for row in root.find_all("div", recursive=True):
        children = row.find_all("div", recursive=False)
        if len(children) != 5:
            continue

        try:
            declared, ex, record, payable, amount = [c.text.strip() for c in children]
            if "$" not in amount:
                continue

            records.append(
                {
                    "ticker": ticker,
                    "amount": float(amount.replace("$", "").replace(",", "")),
                    "declared_date": pd.to_datetime(declared).strftime("%Y-%m-%d"),
                    "ex_date": pd.to_datetime(ex).strftime("%Y-%m-%d"),
                    "record_date": pd.to_datetime(record).strftime("%Y-%m-%d"),
                    "payable_date": pd.to_datetime(payable).strftime("%Y-%m-%d"),
                }
            )
        except Exception as e:
            print(f"⚠️ Skipping malformed row: {[c.text for c in children]} ({e})")

    df = pd.DataFrame(records)

    with HistoricalDataTable.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as batch:
        for _, row in df.iterrows():
            if pd.isna(row["amount"]) or row["amount"] <= 0:
                continue

            item = {
                "PK": ticker,
                "SK": f"DIST#{row['declared_date']}",
                "amount": Decimal(str(row["amount"])),
                "declared_date": row["declared_date"],
                "ex_date": row["ex_date"],
                "record_date": row["record_date"],
                "payable_date": row["payable_date"],
            }

            batch.put_item(Item={k: v for k, v in item.items() if v is not None})

    print(f"Wrote {len(df)} Bitwise distribution records for {ticker}.")
    return df


YMTickers = ["YMAX", "MSTY", "AMZY", "NVDY", "CONY"]

BitWiseTickers = {
    "IMST": "https://imstetf.com/",
    "IMRA": "https://imraetf.com/",
}


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and store Yahoo Finance history."
    )
    parser.add_argument(
        "--ticker", type=str, default="MSTY", help="Ticker symbol, e.g. MSTY"
    )
    args = parser.parse_args()

    print(f"Fetching price and dividend history for {args.ticker}...")
    df = get_yahoo_history(args.ticker)

    ts = now_utc_iso()

    if args.ticker in YMTickers:
        df = fetch_yield_max_distributions(args.ticker, ts=ts)
    elif args.ticker in BitWiseTickers:
        url = BitWiseTickers[args.ticker]
        df = fetch_bitwise_distributions(args.ticker, url, ts=ts)

    print(f"Write {len(df)} distribution records to DynamoDB.")


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv(f"cdk/.env.{os.getenv('ENV_NAME', 'dev')}", override=True)
    init_env()
    main()
