import os
import boto3
import requests
from datetime import datetime, UTC


ENV_NAME = os.getenv("ENV_NAME", "dev")

StrategyKPIsTableName = f"{ENV_NAME}-StrategyKPIs"


def init_env():
    global ENV_NAME, AWS_REGION, StrategyKPIsTableName, StrategyKPIsTable

    ENV_NAME = os.getenv("ENV_NAME", "dev")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    StrategyKPIsTable = dynamodb.Table(StrategyKPIsTableName)

    print(f"✅ Using DynamoDB table: {StrategyKPIsTableName} in {AWS_REGION}")


def fetch_json(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://www.strategy.com",
        "Referer": "https://www.strategy.com/",
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()


def fetch_all_data():
    now = datetime.utcnow().strftime("%Y-%m-%d")

    mstr_data = {}
    strf_data = {}
    strd_data = {}
    strk_data = {}

    # --- MSTR ---
    mstr_kpi_url = "https://api.microstrategy.com/btc/mstrKpiData"
    mstr_options_url = "https://api.microstrategy.com/btc/mstrOptionsData"

    mstr_kpi = fetch_json(mstr_kpi_url)[0]
    mstr_opt = fetch_json(mstr_options_url)

    mstr_data = {
        "date": now,
        "price": mstr_kpi["price"],
        "price_change_%": mstr_kpi["priceVarPerc"],
        "3m_return_%": mstr_kpi["threeMonth"],
        "1y_return_%": mstr_kpi["oneYear"],
        "market_cap": mstr_kpi["marketCap"],
        "debt": mstr_kpi["debt"],
        "pref": mstr_kpi["pref"],
        "historic_vol_30d": mstr_opt["historicVolatility"],
        "historic_vol_kpi": mstr_kpi["historicVolatility"],
        "annualized_vol_kpi": mstr_kpi["annualizedVolatility"],
        "implied_vol": mstr_opt["impliedVolatility"],
        "prev_day_iv": mstr_opt["prevDayImpliedVolatility"],
        "put_call_ratio": mstr_opt["putCallRatio"],
        "total_oi": mstr_opt["totalOi"],
        "call_oi": mstr_opt["callOi"],
        "put_oi": mstr_opt["putOi"],
        "timestamp": mstr_kpi["timeStampUtc"],
    }

    # --- STRF ---
    strf_kpi = fetch_json("https://api.microstrategy.com/btc/strfKpiData")[0]
    strf_data = {
        "date": now,
        "price": strf_kpi["price"],
        "3m_return_%": strf_kpi["threeMonth"],
        "1y_return_%": strf_kpi["oneYear"],
        "market_cap": strf_kpi["marketCap"],
        "historic_vol": strf_kpi["historicVolatility"],
        "prev_historic_vol": strf_kpi["prevHistoricalVolatility"],
        "mstr_cor": strf_kpi["mstrCor"],
        "btc_cor": strf_kpi["btcCor"],
        "spy_cor": strf_kpi["spyCor"],
        "pff_cor": strf_kpi["pffCor"],
        "timestamp": strf_kpi["timeStampUtc"],
    }

    # --- STRD ---
    strd_kpi = fetch_json("https://api.microstrategy.com/btc/strdKpiData")[0]
    strd_data = {
        "date": now,
        "price": strd_kpi["price"],
        "3m_return_%": strd_kpi["threeMonth"],
        "1y_return_%": strd_kpi["oneYear"],
        "market_cap": strd_kpi["marketCap"],
        "historic_vol": strd_kpi["historicVolatility"],
        "prev_historic_vol": strd_kpi["prevHistoricalVolatility"],
        "mstr_cor": strd_kpi["mstrCor"],
        "btc_cor": strd_kpi["btcCor"],
        "spy_cor": strd_kpi["spyCor"],
        "pff_cor": strd_kpi["pffCor"],
        "timestamp": strd_kpi["timeStampUtc"],
    }

    # --- STRK ---
    strk_kpi = fetch_json("https://api.microstrategy.com/btc/strkKpiData")[0]
    strk_data = {
        "date": now,
        "price": strk_kpi["price"],
        "3m_return_%": strk_kpi["threeMonth"],
        "1y_return_%": strk_kpi["oneYear"],
        "market_cap": strk_kpi["marketCap"],
        "historic_vol": strk_kpi["historicVolatility"],
        "prev_historic_vol": strk_kpi["prevHistoricalVolatility"],
        "mstr_cor": strk_kpi["mstrCor"],
        "btc_cor": strk_kpi["btcCor"],
        "spy_cor": strk_kpi["spyCor"],
        "pff_cor": strk_kpi["pffCor"],
        "timestamp": strk_kpi["timeStampUtc"],
    }

    return mstr_data, strf_data, strd_data, strk_data


def write_kpi_to_dynamo(ticker: str, data: dict):
    item = {
        "PK": ticker,
        "SK": data["timestamp"],
        "created_at": datetime.now(UTC).isoformat(),
        "price": data.get("price"),
        "market_cap": data.get("market_cap"),
        "historic_vol": (
            data.get("historic_vol")
            or data.get("historic_vol_kpi")
            or data.get("historic_vol_30d")
        ),
        # Optional MSTR-only fields
        "implied_vol": data.get("implied_vol"),
        "put_call_ratio": data.get("put_call_ratio"),
        "total_oi": data.get("total_oi"),
        "call_oi": data.get("call_oi"),
        "put_oi": data.get("put_oi"),
        "debt": data.get("debt"),
        "pref": data.get("pref"),
        "annualized_vol_kpi": data.get("annualized_vol_kpi"),
        "mstr_cor": data.get("mstr_cor"),
        "btc_cor": data.get("btc_cor"),
        "spy_cor": data.get("spy_cor"),
        "pff_cor": data.get("pff_cor"),
        "price_change_%": data.get("price_change_%"),
        "3m_return_%": data.get("3m_return_%"),
        "1y_return_%": data.get("1y_return_%"),
        "raw": data,
    }

    # Remove None fields to keep the table clean
    item = {k: v for k, v in item.items() if v is not None}

    StrategyKPIsTable.put_item(Item=item)
    print(f"✅ Wrote {ticker} at {data['timestamp']}")


def handler(event=None, context=None):
    init_env()
    mstr, strf, strd, strk = fetch_all_data()
    write_kpi_to_dynamo("MSTR", mstr)
    write_kpi_to_dynamo("STRF", strf)
    write_kpi_to_dynamo("STRD", strd)
    write_kpi_to_dynamo("STRK", strk)

    return {
        "status": "success",
        "data": {
            "MSTR": mstr,
            "STRF": strf,
            "STRD": strd,
            "STRK": strk,
        },
    }


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv(f"cdk/.env.{os.getenv('ENV_NAME', 'dev')}", override=True)
    resp = handler()
    mstr, strf, strd, strk = (
        resp["data"]["MSTR"],
        resp["data"]["STRF"],
        resp["data"]["STRD"],
        resp["data"]["STRK"],
    )

    print("\n📈 MSTR:")
    for k, v in mstr.items():
        print(f"{k}: {v}")

    print("\n📘 STRF:")
    for k, v in strf.items():
        print(f"{k}: {v}")

    print("\n📗 STRD:")
    for k, v in strd.items():
        print(f"{k}: {v}")

    print("\n📕 STRK:")
    for k, v in strk.items():
        print(f"{k}: {v}")
