# utils/simulation.py

import random

from utils.taxes import STATE, monthly_federal_tax


def simulate_month(state):
    cfg = state.cfg
    month = state.month

    # === BTC + Collateral ===
    btc_price = cfg.btc_price_init * (1 + cfg.btc_growth_rate) ** (month / 12)
    collateral_value = btc_price * cfg.btc_total
    ltv = (state.loan_balance / collateral_value) * 100 if collateral_value > 0 else 0

    if state.regime == "bull" and random.random() < cfg.bull_to_bear_prob:
        state.regime = "bear"
    elif state.regime == "bear" and random.random() < cfg.bear_to_bull_prob:
        state.regime = "bull"

    if state.regime == "bull":
        mean_decay = cfg.bull_mean_decay
        std_dev_decay = cfg.bull_std_dev_decay
    else:
        mean_decay = cfg.bear_mean_decay
        std_dev_decay = cfg.bear_std_dev_decay

    # === NAV Decay + Yield ===
    decay = random.gauss(mean_decay, std_dev_decay)
    decay = max(cfg.decay_low, min(decay, cfg.decay_high))
    dy = random.gauss(cfg.mean_yield, cfg.std_dev_yield)
    dy = max(cfg.dist_yield_low, min(dy, cfg.dist_yield_high))
    state.msty_price *= 1 - decay
    distribution_amount = state.msty_price * dy

    # === Revenue ===
    revenue = state.msty_shares * distribution_amount
    interest_due = state.loan_balance * cfg.loan_apy / 12
    interest_paid = min(interest_due, revenue)
    taxable_income = revenue - interest_paid
    fed_tax = monthly_federal_tax(taxable_income)
    state_tax = taxable_income * STATE
    total_tax = fed_tax + state_tax

    # === Determine Draw ===
    draw = 0
    for amount, min_rev, max_rev in cfg.draw_tiers:
        if min_rev <= taxable_income < max_rev:
            draw = amount
            break

    # === Net Cash ===
    net_cash = taxable_income - total_tax - draw

    # === Loan Paydown (from Net Cash) ===
    principal_paid = 0
    if net_cash > 0 and state.loan_balance > 0:
        principal_paid = min(net_cash, state.loan_balance)
        state.loan_balance -= principal_paid
        net_cash -= principal_paid

    # === Cash Buffer ===
    if net_cash < 0:
        shortfall = abs(net_cash)
        if state.cash_reserves >= shortfall:
            state.cash_reserves -= shortfall
            net_cash = 0
        else:
            state.fail = True
            return {
                "Month": month,
                "Revenue": revenue,
                "Draw": draw,
                "Total Tax": total_tax,
                "Net Cash": net_cash,
                "FAIL": "Net Cash + Cash Reserves < 0",
            }

    # === Cash Reserve Add (10%) ===
    if state.cash_reserves < 10_000 and net_cash > 0:
        reserve_add = 0.10 * net_cash
        state.cash_reserves += reserve_add
        net_cash -= reserve_add

    # === Compound Remainder ===
    new_shares = net_cash / state.msty_price if net_cash > 0 else 0
    state.msty_shares += new_shares

    # === Snapshot ===
    return {
        "Month": month,
        "Regime": 1 if state.regime == "bull" else 0,
        "Revenue": round(revenue, 2),
        "Draw": draw,
        "Total Tax": round(total_tax, 2),
        "Net Cash": round(net_cash, 2),
        "Paid to Loan": round(interest_paid + principal_paid, 2),
        "Loan Bal": round(state.loan_balance, 2),
        "Cash Res": round(state.cash_reserves, 2),
        "MSTY Price": round(state.msty_price, 2),
        "Dist": round(distribution_amount, 2),
        "Dist Yield": round(dy * 100, 2),
        "Decay Rate": round(decay * 100, 2),
        "MSTY Shares": round(state.msty_shares, 2),
        "New Shares": round(new_shares, 2),
        "BTC Val": round(btc_price * cfg.btc_total, 2),
        "Loan Left": round(state.loan_balance, 2),
        "LTV": round(ltv, 2),
    }
