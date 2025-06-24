# import defaultdict
from collections import defaultdict
import boto3
import os
from boto3.dynamodb.conditions import Key

ENV_NAME = os.getenv("ENV_NAME", "dev")
TABLE_NAME = os.getenv("BLC_EVENT_TABLE", f"{ENV_NAME}-BLCEventTable")


class BLCEvents:
    def __init__(self, ticker: str, sk_prefix: str = None, filters: dict = None):
        self.ticker = ticker.upper()
        self.pk = f"TICKER#{self.ticker}"
        self.sk_prefix = sk_prefix  # e.g. "DISTRO#", "BUY#", etc.
        self.filters = filters or {}  # optional future flexibility
        self._raw_items = self.fetch_from_dynamo()
        self._index_items_by_type()

    def fetch_from_dynamo(self) -> list[dict]:
        table = boto3.resource("dynamodb").Table(TABLE_NAME)

        key_expr = Key("PK").eq(self.pk)
        if self.sk_prefix:
            key_expr &= Key("SK").begins_with(self.sk_prefix)

        response = table.query(KeyConditionExpression=key_expr)
        items = response.get("Items", [])

        # Optional: Apply Python-side filters
        for key, value in self.filters.items():
            items = [item for item in items if item.get(key) == value]

        return items

    def _index_items_by_type(self):
        self.by_type = defaultdict(list)
        for item in self._raw_items:
            prefix = item["SK"].split("#")[0]
            self.by_type[prefix].append(item)

    # def get_distributions(self):
    #     return self.by_type.get("DISTRO", [])

    # def get_trades(self, trade_type="BUY"):
    #     return self.by_type.get(trade_type, [])

    # def get_options(self):
    #     return self.by_type.get("OPTION", [])

    # def get_summary(self):
    #     return [item for item in self._raw_items if item["SK"].startswith("SUMMARY#")]

    # def get_all_by_type(self, event_type: str):
    #     return self.by_type.get(event_type, [])
