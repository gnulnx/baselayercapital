from math import inf

# === Simulation Parameters ===
months = 120  # Number of months to simulate (e.g., 10 years)
epochs = 2000  # Number of Monte Carlo simulation runs
show_averaged_output = (
    False  # If True, show average results across all runs; if False, show last run only
)
show_failed_runs = (
    False  # If True, print failed runs with Decay Rate == 0.2000 for debugging
)

starting_capital_contributed = 300_000  # Initial capital contributed to the strategy
btc_total = 14  # Total BTC held (for LTV calculations)
starting_cash_reserves = (
    20_000  # Cash reserves to cover shortfalls in net cash (not invested unless needed)
)
cash_tranche_count = 4  # Number of tranches to split cash reserves into for opportunistic buying (0 disables feature)
cash_tranche_period = 6  # Lookback period (months) for volatility-adjusted buying logic
vol_buy_threshold = (
    -1.2
)  # Buy if price is 1.2 std dev below mean of lookback period (if tranches enabled)

btc_price_init = 104_896.3  # Initial BTC price
btc_growth_rate = (
    0.20  # Annual linear growth rate for BTC price (used for BTC LTV calculations)
)

loan_apy = 0.13  # Annual percentage yield (interest rate) for loans
loan_origination_fee_rate = 0.0

# === Regime-based Leverage Parameters ===
target_ltv = 10.0  # Target LTV (%) for bull markets
ltv_buffer = (
    4  # Only stack loans if LTV < (target_ltv - ltv_buffer), stop if >= target_ltv
)

# Tax parameters
state_tax_rate = 0.05  # State tax rate (federal tax is computed monthly in the code)

dist_yield_low = (
    0.04  # Minimum monthly distribution yield (as a fraction, e.g., 0.04 = 4%)
)
dist_yield_high = 0.15  # Maximum monthly distribution yield (as a fraction)
mean_yield = 0.065  # Mean monthly distribution yield (historical average)
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
bull_to_bear_prob = 0.0667  # Bull markets last ~15 months
bear_to_bull_prob = 0.20  # Bear markets last ~5 months

# --- NAV Decay by Regime ---
bull_mean_decay = (
    0.01  # Bull: slight positive or flat NAV (simulate modest appreciation)
)
bull_std_dev_decay = 0.15
bear_mean_decay = 0.04  # Bear: -4% average monthly NAV decay
bear_std_dev_decay = 0.25


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
