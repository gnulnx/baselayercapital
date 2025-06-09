# game_state.py
class GameState:
    def __init__(self, cfg):
        self.month = 1
        self.cfg = cfg
        self.msty_price = 20.59  # TODO set this dynamically in config
        self.msty_shares = cfg.starting_capital_contributed / self.msty_price
        self.loan_balance = 0
        self.cash_reserves = cfg.starting_cash_reserves
        self.tranches_left = cfg.cash_tranche_count
        self.last_buy_month = -cfg.cash_tranche_period
        self.price_history = []
        self.regime = "bull"
        self.logs = []
        self.fail = False
        # anything else: loan_active, cumulative_fees_paid, etc.

    def snapshot(self):
        return {
            "Month": self.month,
            "MSTY Price": self.msty_price,
            "MSTY Shares": self.msty_shares,
            "Loan Balance": self.loan_balance,
            "Cash Reserves": self.cash_reserves,
            "Regime": self.regime,
            # add more fields as needed
        }
