#!/usr/bin/env python3
import sys
import csv
from collections import defaultdict
from tabulate import tabulate

input_file = sys.argv[1]

HEADERS = [
    "Put_Bid",
    "Put_Ask",
    "Put_Mid",
    "Put_Change",
    "Put_Vol",
    "Put_OI",
    "Put_Delta",
    "Strike",
    "Call_Bid",
    "Call_Ask",
    "Call_Mid",
    "Call_Change",
    "Call_Vol",
    "Call_OI",
    "Call_Delta",
]

output_rows = []
current_expiry = ""
options_by_expiry = defaultdict(list)

with open(input_file, "r") as f:
    for line in f:
        stripped = line.strip()
        if not stripped or stripped.startswith("More") or stripped.startswith("Select"):
            continue
        if "Jul." in stripped or "Aug." in stripped or "Sep." in stripped:
            current_expiry = stripped
            continue
        fields = stripped.split()
        if len(fields) == 15:
            row = [current_expiry] + fields
            options_by_expiry[current_expiry].append(row)
            output_rows.append(row)

# Display tables with ITM flags
UNDERLYING_PRICE = 55.25  # Set this manually or dynamically from source

for expiry in options_by_expiry:
    print(f"\n📅 {expiry}")
    table = []
    for row in options_by_expiry[expiry]:
        strike = float(row[8])
        call_mid = float(row[11])
        put_mid = float(row[3])

        # Highlight ITM options
        call_tag = "*" if strike < UNDERLYING_PRICE else ""
        put_tag = "*" if strike > UNDERLYING_PRICE else ""

        row[8] = f"{strike:.2f}{call_tag}"  # Strike
        row[11] = f"{call_mid:.2f}{call_tag}"  # Call Mid
        row[3] = f"{put_mid:.2f}{put_tag}"  # Put Mid

        table.append(row)

    headers = ["Expiry"] + HEADERS
    print(tabulate(table, headers=headers, tablefmt="pretty"))

# Optional: Save to CSV if 2nd arg is given
if len(sys.argv) > 2:
    output_csv = sys.argv[2]
    with open(output_csv, "w", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Expiry"] + HEADERS)
        writer.writerows(output_rows)
    print(f"\n✅ CSV saved to: {output_csv}")
