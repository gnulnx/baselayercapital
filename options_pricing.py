#!/usr/bin/env python3
import sys
import csv
from collections import defaultdict
from rich.table import Table
from rich.console import Console
from rich import box

console = Console()
input_file = sys.argv[1]

UNDERLYING_PRICE = 54.30  # ← Update this manually for now

HEADERS = [
    "Call_Bid",
    "Call_Ask",
    "Call_Last",
    "Call_Change",
    "Call_Vol",
    "Call_OI",
    "Call_Delta",
    "Strike",
    "Put_Bid",
    "Put_Ask",
    "Put_Last",
    "Put_Change",
    "Put_Vol",
    "Put_OI",
    "Put_Delta",
]

options_by_expiry = defaultdict(list)
current_expiry = ""

with open(input_file, "r") as f:
    for line in f:
        stripped = line.strip()
        if not stripped or stripped.startswith("More") or stripped.startswith("Select"):
            continue
        if any(month in stripped for month in ["Jul.", "Aug.", "Sep."]):
            current_expiry = stripped
            continue
        fields = stripped.split()
        if len(fields) == 15:
            options_by_expiry[current_expiry].append(fields)


def colorize(text, color):
    return f"[{color}]{text}[/{color}]"


for expiry in options_by_expiry:
    console.print(f"\n📅 [bold yellow]{expiry}[/bold yellow]")
    table = Table(box=box.SIMPLE_HEAVY, expand=False)
    for header in HEADERS:
        table.add_column(header, justify="right", style="white", no_wrap=True)

    for row in options_by_expiry[expiry]:
        strike = float(row[7])
        # put_bid, put_ask, put_mid = float(row[0]), float(row[1]), float(row[2])
        # call_bid, call_ask, call_mid = float(row[8]), float(row[9]), float(row[10])

        call_bid, call_ask, call_mid = float(row[0]), float(row[1]), float(row[2])
        put_bid, put_ask, put_mid = float(row[8]), float(row[9]), float(row[10])

        is_put_itm = strike < UNDERLYING_PRICE
        is_call_itm = strike > UNDERLYING_PRICE

        # Apply color to entire side if ITM
        if is_put_itm:
            row[0] = colorize(row[0], "cyan")
            row[1] = colorize(row[1], "cyan")
            row[2] = colorize(row[2], "cyan")
            row[3] = colorize(row[3], "cyan")
            row[4] = colorize(row[4], "cyan")
            row[5] = colorize(row[5], "cyan")
            row[6] = colorize(row[6], "cyan")
        if is_call_itm:
            row[8] = colorize(row[8], "cyan")
            row[9] = colorize(row[9], "cyan")
            row[10] = colorize(row[10], "cyan")
            row[11] = colorize(row[11], "cyan")
            row[12] = colorize(row[12], "cyan")
            row[13] = colorize(row[13], "cyan")
            row[14] = colorize(row[14], "cyan")
            # row[15] = colorize(row[15], "cyan")

        row[7] = colorize(row[7], "green")

        table.add_row(*row)

    console.print(table)
