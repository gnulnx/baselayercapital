# game_state.py
class GameState:
    def __init__(self, cfg):
        self.month = 1
        self.cfg = cfg
        self.msty_price = 20.59
        self.msty_shares = cfg.starting_capital_contributed / self.msty_price
        self.loan_balance = 0
        self.cash_reserves = cfg.starting_cash_reserves
        self.tranches_left = cfg.cash_tranche_count
        self.last_buy_month = -cfg.cash_tranche_period
        self.price_history = []
        self.regime = "bull"
        self.logs = []
        self.fail = False
        self.net_cash = 0.0
        self.extra_draw = 0.0
        self.extra_loan = 0.0

    def snapshot(self):
        return {
            "Month": self.month,
            "MSTY Price": self.msty_price,
            "MSTY Shares": self.msty_shares,
            "Loan Balance": self.loan_balance,
            "Cash Reserves": self.cash_reserves,
            "Regime": self.regime,
        }
