# pylint: disable=invalid-name, missing-module-docstring, missing-function-docstring, too-many-locals, too-many-statements, too-many-branches, C0103, C0200, C0112

import locale
import random
from math import inf

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from matplotlib.widgets import Cursor

locale.setlocale(locale.LC_ALL, "")

# === Simulation Parameters ===
months = 120  # Number of months to simulate (e.g., 10 years)
epochs = 10000  # Number of Monte Carlo simulation runs
# If True, show average results across all runs; if False, show last run only
show_averaged_output = True
# If True, print failed runs with Decay Rate == 0.2000 for debugging
show_failed_runs = False

starting_capital_contributed = 440_000  # Initial capital contributed to the strategy
btc_total = 14  # Total BTC held (for LTV calculations)
# Cash reserves to cover shortfalls in net cash (not invested unless needed)
starting_cash_reserves = 20_000
cash_tranche_count = 4  # Number of tranches to split cash reserves into for opportunistic buying (0 disables feature)
cash_tranche_period = 6  # Lookback period (months) for volatility-adjusted buying logic

# Buy if price is 1.2 std dev below mean of lookback period (if tranches enabled)
vol_buy_threshold = -1.2

btc_price_init = 104_896.3  # Initial BTC price
# Annual linear growth rate for BTC price (used for BTC LTV calculations)
btc_growth_rate = 0.20

loan_apy = 0.13  # Annual percentage yield (interest rate) for loans
loan_origination_fee_rate = 0.0

# === Regime-based Leverage Parameters ===
target_ltv = 0.0  # Target LTV (%) for bull markets
# Only stack loans if LTV < (target_ltv - ltv_buffer), stop if >= target_ltv
ltv_buffer = 5

# Tax parameters
state_tax_rate = 0.05  # State tax rate (federal tax is computed monthly in the code)

# Minimum monthly distribution yield (as a fraction, e.g., 0.04 = 4%)
dist_yield_low = 0.05
dist_yield_high = 0.15  # Maximum monthly distribution yield (as a fraction)
mean_yield = 0.085  # Mean monthly distribution yield (historical average)
std_dev_yield = 0.0224  # Standard deviation of monthly yield (historical)

decay_low = -0.20  # Minimum monthly NAV decay (as a fraction, e.g., -0.20 = -20%)
decay_high = 0.20  # Maximum monthly NAV decay (as a fraction)
# mean_decay and std_dev_decay are not used directly; regime switching is used instead

# === Regime Switching Parameters ===
# These control how often the simulation switches between bull and bear market regimes,
# affecting the NAV decay patterns of MSTY over time.

# --- How This Works ---
# Each month, there's a chance of switching from the current regime (bull or bear) to the other.
# You define that chance using these probabilities:
#   - bull_to_bear_prob: chance of ending a bull market and switching to a bear market
#   - bear_to_bull_prob: chance of ending a bear market and switching to a bull market

# --- How to Use This ---
# If you want a bull market to last on average 36 months:
#     bull_to_bear_prob = 1 / 36  ≈ 0.0278
# If you want a bear market to last on average 12 months:
#     bear_to_bull_prob = 1 / 12  ≈ 0.0833

# --- How to Control the Long-Term Regime Balance ---
# The expected fraction of time spent in bull markets is:
#     bull_fraction = bear_to_bull_prob / (bull_to_bull_prob + bull_to_bear_prob)
# For example:
#     With bull_to_bear_prob = 0.0667 and bear_to_bull_prob = 0.20,
#     bull_fraction = 0.20 / (0.20 + 0.0667) ≈ 0.75 → 75% of time in bull, 25% in bear

# --- Quick Reference Table ---
# | Avg Bull Duration | bull_to_bear_prob |
# |-------------------|------------------|
# | 12 months         | 0.0833           |
# | 24 months         | 0.0417           |
# | 36 months         | 0.0278           |

# | Avg Bear Duration | bear_to_bull_prob |
# |-------------------|------------------|
# | 6 months          | 0.1667            |
# | 12 months         | 0.0833            |
# | 18 months         | 0.0556            |

# --- Example Setup for 75/25 regime split ---
bull_to_bear_prob = 0.0278  # ~36 months average bull duration
bear_to_bull_prob = 0.0833  # ~12 months average bear duration

# --- NAV Decay by Regime ---
# Bull: slight positive or flat NAV (simulate modest appreciation)
bull_mean_decay = -0.005  # Bull: -0.5% average monthly NAV decay
bull_std_dev_decay = 0.08
bear_mean_decay = 0.10  # Bear: -4% average monthly NAV decay
bear_std_dev_decay = 0.10


# === Draw Tiers ===
# Each tuple is (draw amount, min revenue, max revenue). Used to determine income draw based on revenue.
draw_tiers = [
    (10_000, 0, 100_000),
    (12_500, 100_000, 200_000),
    (15_000, 200_000, 300_000),
    (20_000, 300_000, 500_000),
    (25_000, 500_000, 750_000),
    (30_000, 750_000, inf),
]


# === Tax Function ===
def monthly_federal_tax(income_monthly):
    annual = income_monthly * 12
    brackets = [0, 23200, 94300, 201050, 383900, 487450, 731200, float("inf")]
    rates = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    tax = 0
    for i in range(len(rates)):
        low, high = brackets[i], brackets[i + 1]
        if annual > low:
            taxable = min(annual, high) - low
            tax += taxable * rates[i]
        else:
            break
    return tax / 12


# === Rolling Loan Model (No Business Units) ===
# This simulation models a single rolling loan against BTC collateral, refinancing to target LTV in bull regimes.
# MSTY shares are pooled; refinancing/top-up is used to buy more MSTY. No BU/tranche logic remains.
avg_results = {}
fails = 0
successes = 0
fail_months = []  # Track the month of each fail
for _ in range(epochs):
    msty_price = 20.59
    msty_shares = starting_capital_contributed / msty_price
    loan_balance = 0
    fail = False
    results = []
    cash_reserves = starting_cash_reserves
    tranche_size = (
        starting_cash_reserves / cash_tranche_count if cash_tranche_count > 0 else 0
    )
    tranches_left = cash_tranche_count
    price_history = []
    last_buy_month = -cash_tranche_period
    regime = "bull" if random.random() < 0.7 else "bear"
    loan_active = False  # Track if a loan is currently active
    cumulative_fees_paid = 0

    for month in range(1, months + 1):
        btc_price = btc_price_init * (1 + btc_growth_rate) ** (month / 12)
        collateral_value = btc_price * btc_total
        ltv = (loan_balance / collateral_value) * 100 if collateral_value > 0 else 0

        # === Bull regime: always refinance to target LTV (principal only) ===
        if regime == "bull" and ltv < (target_ltv - ltv_buffer):
            target_loan = (target_ltv / 100) * collateral_value
            # print("Target Loan:", target_loan, "Collateral Value:", collateral_value)
            # input()
            # Refinance to target LTV every month in bull regime
            topup = target_loan - loan_balance
            if abs(topup) > 1e-2:
                # if abs(topup) > 100:
                if topup > 0:
                    origination_fee = topup * loan_origination_fee_rate
                    net_loan_proceeds = topup - origination_fee
                    loan_balance += topup  # full loan amount owed
                    msty_shares += net_loan_proceeds / msty_price
                    cumulative_fees_paid += origination_fee  # track if desired
                # elif topup < 0:
                #     paydown = min(-topup, loan_balance)
                #     loan_balance -= paydown
                #     if loan_balance <= 1e-6:
                #         loan_balance = 0
                #         loan_active = False

            loan_active = loan_balance > 0

        # Regime switching logic
        if regime == "bull":
            if random.random() < bull_to_bear_prob:
                regime = "bear"
        elif regime == "bear":
            if random.random() < bear_to_bull_prob:
                regime = "bull"
        if regime == "bull":
            mean_decay = bull_mean_decay
            std_dev_decay = bull_std_dev_decay
        else:
            mean_decay = bear_mean_decay
            std_dev_decay = bear_std_dev_decay

        # Calculate the modelled NAV decay and distribution yield
        decay = random.gauss(mean_decay, std_dev_decay)
        decay = max(decay_low, min(decay, decay_high))
        dy = random.gauss(mean_yield, std_dev_yield)
        dy = max(dist_yield_low, min(dy, dist_yield_high))
        msty_price *= 1 - decay
        distribution_amount = msty_price * dy

        # Step 1: Calculate total revenue from MSTY distributions
        revenue = msty_shares * distribution_amount

        # Step 2 Calculate interst payment that is due
        interest_due = loan_balance * loan_apy / 12
        interest_paid = min(interest_due, revenue)

        # Step 3: Compute taxable income
        taxable_income = revenue - interest_paid  # deduct business loan interest

        # Step 4: Calculate taxes on taxable income
        fed_tax = monthly_federal_tax(taxable_income)
        state_tax = taxable_income * state_tax_rate
        tax = fed_tax + state_tax

        # Step 5: Determine draw (personal income) based on taxable income
        for amount, min_rev, max_rev in draw_tiers:
            if min_rev <= taxable_income < max_rev:
                draw = amount
                break

        # Step 6 Calculate net cash after revenue, tax, draw, and interest
        net_cash = taxable_income - tax - draw

        # Step 7: Only pay down principal from positive net_cash, capped at loan balance
        principal_paid = 0.0
        if net_cash > 0 and loan_balance > 0:
            principal_paid = min(net_cash, loan_balance)
            loan_balance -= principal_paid
            net_cash -= principal_paid
            if loan_balance <= 1e-6:
                loan_balance = 0
                loan_active = False

        ltv = (
            (loan_balance / (btc_price * btc_total)) * 100
            if btc_price * btc_total > 0
            else 0
        )

        base_output = {
            "Month": month,
            "Regime": 1 if regime == "bull" else 0,
            "Revenue": round(revenue, 2),
            "Draw": draw,
            "Total Tax": round(tax, 2),
            "Net Cash": round(net_cash, 2),
            "Paid to Loan": round(interest_paid + principal_paid, 2),
            "Loan Bal": round(loan_balance, 2),
            "Cash Res": round(cash_reserves, 2),
            "MSTY Price": round(msty_price, 2),
            "Dist": round(distribution_amount, 2),
            "Dist Yield": round(dy * 100, 2),
            "Decay Rate": round(decay * 100, 2),
            "MSTY Shares": round(msty_shares, 2),
            "New Shares": round(net_cash / msty_price if net_cash > 0 else 0, 2),
            "BTC Val": round(btc_price * btc_total, 2),
            "Loan Left": round(loan_balance, 2),
            "LTV": round(ltv, 2),
        }
        # Use cash reserves if net_cash < 0
        if net_cash < 0:
            shortfall = abs(net_cash)
            if cash_reserves >= shortfall:
                cash_reserves -= shortfall
                base_output["Cash Res"] = round(cash_reserves, 2)
                net_cash = 0
                base_output["Net Cash"] = 0
            else:
                base_output["PASS"] = "❌"
                base_output["Fail Reason"] = "Net Cash + Cash Reserves < 0"
                results.append(base_output)
                fail = True
                fail_months.append(month)
                if show_failed_runs:
                    df = pd.DataFrame(results)
                    print(df.to_string(index=False))
                    count_2000 = (df["Decay Rate"].round(4) == 0.2000).sum()
                    total_months = len(df)
                    ratio = count_2000 / total_months
                    print(
                        f"Decay Rate == 0.2000: {count_2000} months out of {total_months}"
                    )
                    print(f"Ratio: {ratio:.2%}")
                    input("Simulation failed. Press Enter to continue...")
                break
        # Set aside 10% of net_cash to cash reserves if reserves are under $10,000 and net_cash is positive
        if cash_reserves < 10_000 and net_cash > 0:
            reserve_add = 0.10 * net_cash
            cash_reserves += reserve_add
            net_cash -= reserve_add
            base_output["Cash Res"] = round(cash_reserves, 2)
            base_output["Net Cash"] = round(net_cash, 2)
        # Volatility-adjusted buying logic (for cash reserves)
        price_history.append(msty_price)
        if len(price_history) > cash_tranche_period:
            price_history.pop(0)
        if (
            tranches_left > 0
            and len(price_history) == cash_tranche_period
            and (month - last_buy_month) >= 1
        ):
            mean_price = sum(price_history) / cash_tranche_period
            std_price = (
                sum((p - mean_price) ** 2 for p in price_history) / cash_tranche_period
            ) ** 0.5
            threshold_price = mean_price + vol_buy_threshold * std_price
            if msty_price < threshold_price:
                buy_amt = min(tranche_size, cash_reserves)
                if buy_amt > 0:
                    added_shares = buy_amt / msty_price
                    msty_shares += added_shares
                    cash_reserves -= buy_amt
                    tranches_left -= 1
                    last_buy_month = month
        # Compound any remaining net_cash
        msty_shares += net_cash / msty_price if net_cash > 0 else 0
        results.append(base_output)

    for idx, row in enumerate(results):
        if idx not in avg_results:
            avg_results[idx] = {k: 0 for k in row if isinstance(row[k], (int, float))}
            avg_results[idx]["count"] = 0
        for k, v in row.items():
            if isinstance(v, (int, float)):
                avg_results[idx][k] += v
        avg_results[idx]["count"] += 1

    if not fail:
        successes += 1
    else:
        fails += 1

final = []
if show_averaged_output:
    for idx, data in sorted(avg_results.items()):
        count = data.pop("count")
        row = {k: round(v / count, 2) for k, v in data.items()}
        row["Month"] = idx + 1
        final.append(row)
    df = pd.DataFrame(final)
else:
    df = pd.DataFrame(results)


def print_centered_df(df, width=10):
    # Build centered header
    headers = [f"{col:^{width}}" for col in df.columns]
    header_row = " ".join(headers)

    # Build each row with centered strings
    lines = [header_row]
    for _, row in df.iterrows():
        line = " ".join(f"{str(val):^{width}}" for val in row)
        lines.append(line)

    print("\n".join(lines))


print_centered_df(df, width=12)

print("\n--- Success Summary ---")
print(f"Odds of Success: {100 * successes / epochs:.2f}%")
if fail_months:
    avg_fail_month = sum(fail_months) / len(fail_months)
    print(f"Average Fail Month: {avg_fail_month:.2f} (across {len(fail_months)} fails)")
else:
    print("No failures occurred in any run.")

# === Economic Summary (Final Month) ===
ending_row = df.iloc[-1]
ending_msty_shares = ending_row["MSTY Shares"]
ending_loan = (
    ending_row["Loan Left"] if "Loan Left" in ending_row else ending_row["Loan Bal"]
)
ending_cash = ending_row["Cash Res"] + ending_row["Net Cash"]
ending_msty_price = ending_row["MSTY Price"]
ending_net_worth = ending_msty_shares * ending_msty_price + ending_cash - ending_loan
print("\n--- Simulations TOTAL Results ---")
print("\n--- Economic Summary (Final Month) ---")
# locale.currency( 188518982.18, grouping=True
print(f"ENDING BTC value: {locale.currency(ending_row['BTC Val'], grouping=True)}")
print(f"Ending MSTY Shares: {ending_msty_shares:.2f}")
print(f"Ending MSTY Price: ${ending_msty_price:,.2f}")
print(f"Ending Loan Balance: ${ending_loan:,.2f}")
print(f"Ending Cash (Reserves + Net): ${ending_cash:,.2f}")
print(f"Ending Net Worth: ${ending_net_worth:,.2f}")


def human_readable_log_labels(x, pos):
    if x >= 1_000_000:
        return f"{x / 1_000_000:.0f}M"
    elif x >= 1_000:
        return f"{x / 1_000:.0f}K"
    else:
        return f"{x:.0f}"


# === Plot Revenue and Draw ===
fig, ax1 = plt.subplots(figsize=(14, 6))
ax1.plot(df["Month"], df["Revenue"], label="Revenue", color="tab:blue")
ax1.set_xlabel("Month")
ax1.set_ylabel("Revenue", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax1.set_yscale("log")
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(human_readable_log_labels))
ax1.set_yticks([1e5, 1e6, 1e7])  # Set fixed major ticks


ax2 = ax1.twinx()
ax2.plot(
    df["Month"], df["Draw"], label="Draw (Income)", linestyle="--", color="tab:green"
)
ax2.set_ylabel("Draw (Income)", color="tab:green")
ax2.tick_params(axis="y", labelcolor="tab:green")

title = (
    "Revenue vs Income Draw Over Time (Averaged Over Simulations)"
    if show_averaged_output
    else "Revenue vs Income Draw Over Time (Last Run)"
)
fig.suptitle(title)
fig.tight_layout()

cursor = Cursor(ax1, useblit=True, color="gray", linewidth=1)

annot = ax1.annotate(
    "",
    xy=(0, 0),
    xytext=(15, 15),
    textcoords="offset points",
    bbox=dict(boxstyle="round", fc="w"),
    arrowprops=dict(arrowstyle="->"),
)
annot.set_visible(False)


def update_annot(event):  # noqa
    if event.inaxes not in [ax1, ax2]:
        annot.set_visible(False)
        fig.canvas.draw_idle()
        return

    x = int(round(event.xdata))
    if 1 <= x <= len(df):
        month = df.loc[x - 1, "Month"]
        revenue = df.loc[x - 1, "Revenue"]
        draw_val = df.loc[x - 1, "Draw"]

        annot.xy = (x, revenue)
        text = f"Month: {month}\nRevenue: ${revenue:,.0f}\nDraw: ${draw_val:,.0f}"
        annot.set_text(text)
        annot.set_visible(True)
        fig.canvas.draw_idle()


fig.canvas.mpl_connect("motion_notify_event", update_annot)
plt.show()
