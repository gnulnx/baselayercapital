import os
import json
import uuid
from decimal import Decimal
from datetime import datetime
import boto3

ENV_NAME = os.getenv("ENV_NAME", "dev")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TransactionsTableName = f"{ENV_NAME}-Transactions"


def init_env():
    global TransactionsTable
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    TransactionsTable = dynamodb.Table(TransactionsTableName)


def parse_amount(value):
    return Decimal(value.replace("$", "").replace(",", "")) if value else None


def parse_quantity(value):
    try:
        return int(value.replace(",", "")) if value else None
    except Exception:
        return None


def normalize_date_field(date_str):
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date().isoformat()
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None


def generate_sk(effective_date, symbol, action):
    parts = [effective_date]
    if symbol:
        parts.append(symbol)
    if action:
        parts.append(action.replace(" ", "_"))
    return "#".join(parts)


def write_transactions_to_dynamo(transactions):
    with TransactionsTable.batch_writer(overwrite_by_pkeys=["PK"]) as batch:
        for txn in transactions:
            if "as of" in txn["Date"]:
                effective_date = normalize_date_field(
                    txn["Date"].split("as of")[1].strip()
                )
                posted_date = normalize_date_field(
                    txn["Date"].split("as of")[0].strip()
                )
            else:
                # Fallback if "as of" is not present
                effective_date = normalize_date_field(txn["Date"])
                posted_date = effective_date

            pk = uuid.uuid3(uuid.NAMESPACE_DNS, json.dumps(txn)).hex
            sk = generate_sk(effective_date, txn.get("Symbol"), txn.get("Action"))

            item = {
                "PK": pk,
                "SK": sk,
                "Action": txn.get("Action"),
                "Symbol": txn.get("Symbol") or None,
                "Description": txn.get("Description"),
                "Quantity": parse_quantity(txn.get("Quantity")),
                "Price": parse_amount(txn.get("Price")),
                "FeesAndCommission": parse_amount(txn.get("Fees & Comm")),
                "Amount": parse_amount(txn.get("Amount")),
                "PostedDate": posted_date,
                "EffectiveDate": effective_date,
                "RawDateField": txn["Date"],
                "Source": "Schwab JSON",
            }

            item = {k: v for k, v in item.items() if v is not None}
            batch.put_item(Item=item)

    print(f"Wrote {len(transactions)} transactions to {TransactionsTableName}.")


def handler(event, context):
    transactions = event.get("transactions", [])
    write_transactions_to_dynamo(transactions)
    return {"status": "success", "count": len(transactions)}


def main():
    json_file = "Limit_Liability_Company_XXX003_Transactions_20250709-111042.json"
    with open(json_file, "r") as f:
        data = json.load(f)

    transactions = data.get("BrokerageTransactions", [])
    write_transactions_to_dynamo(transactions)


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv(f"cdk/.env.{os.getenv('ENV_NAME', 'dev')}", override=True)
    init_env()
    main()
