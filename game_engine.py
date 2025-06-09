# game_engine.py
from game_state import GameState
from utils.simulation import simulate_month


class GameEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.state = GameState(cfg)

    def play_turn(self):
        print(f"\n--- MONTH {self.state.month} ---")
        month_summary = simulate_month(self.state)

        print("\n--- Simulation Results ---")
        for k, v in month_summary.items():
            print(f"{k:15}: {v}")

        if self.state.net_cash < 0 and self.state.cash_reserves > 0:
            auto_cover = min(abs(self.state.net_cash), self.state.cash_reserves)
            self.state.cash_reserves -= auto_cover
            self.state.net_cash += auto_cover
            print(f"\n⚠️  Auto-covered ${auto_cover:,.2f} from cash reserves.")

        if self.state.net_cash < 0:
            self.prompt_shortfall_cover()

        self.prompt_action()

    def prompt_shortfall_cover(self):
        print("\n🚨 Net Cash Shortfall 🚨")
        print(f"You are short ${abs(self.state.net_cash):,.2f} this month.")
        needed = abs(self.state.net_cash)

        while self.state.net_cash < 0:
            print("\nOptions:")
            print("1) Use BTC-backed loan")
            print("2) Use cash reserves")
            print("3) Combination")
            print("4) Do nothing (exit/fail)")

            choice = input("How would you like to cover the shortfall? ").strip()

            if choice == "1":
                amount = float(input("Enter loan amount: $"))
                self.take_loan(amount)

            elif choice == "2":
                if self.state.cash_reserves <= 0:
                    print("⚠️ No cash reserves available.")
                    continue
                amount = float(input("Enter reserve amount to use: $"))
                amount = min(amount, self.state.cash_reserves)
                self.state.cash_reserves -= amount
                self.state.net_cash += amount

            elif choice == "3":
                loan_amt = float(input("Loan portion: $"))
                reserve_amt = float(input("Reserve portion: $"))
                self.take_loan(loan_amt)
                reserve_amt = min(reserve_amt, self.state.cash_reserves)
                self.state.cash_reserves -= reserve_amt
                self.state.net_cash += reserve_amt

            elif choice == "4":
                print("💥 You did not cover the shortfall. Game over.")
                exit()
            else:
                print("❌ Invalid input.")

        print("✅ Shortfall covered.")

    def take_loan(self, amount):
        self.state.loan_balance += amount
        self.state.msty_shares += amount / self.state.msty_price
        self.state.net_cash += amount

    def prompt_action(self):
        print("\nWhat would you like to do?")
        print("1) Take additional draw")
        print("2) Reinvest net cash")
        print("3) Trigger BTC-backed loan")
        print("4) Deploy cash (loan payoff or MSTY buy)")
        print("5) End game")

        choice = input("Enter choice: ").strip()
        self.process_action(choice)

    def process_action(self, choice):
        if choice == "1":
            try:
                amount = float(input("Enter additional draw amount: $"))
            except ValueError:
                print("⚠️ Invalid number. Skipping draw.")
                return
            self.state.extra_draw = amount
            print(f"✅ Additional draw of ${amount:,.2f} scheduled for next turn.")

        elif choice == "2":
            if self.state.net_cash > 0:
                shares_bought = self.state.net_cash / self.state.msty_price
                self.state.msty_shares += shares_bought
                print(
                    f"✅ Reinvested ${self.state.net_cash:,.2f} into {shares_bought:,.2f} MSTY shares."
                )
                self.state.net_cash = 0
            else:
                print("ℹ️ No cash to reinvest.")

        elif choice == "3":
            try:
                amount = float(input("Enter BTC-backed loan amount to take: $"))
            except ValueError:
                print("⚠️ Invalid number. Skipping loan.")
                return
            self.take_loan(amount)
            print(f"✅ Requested BTC-backed loan of ${amount:,.2f}.")

        elif choice == "4":
            if self.state.cash_reserves <= 0:
                print("⚠️ No cash reserves available.")
                return
            print("\nDeploy cash reserves:")
            print("1) Buy MSTY shares")
            print("2) Pay down loan")
            sub_choice = input("Enter choice: ").strip()

            if sub_choice == "1":
                amt = float(input("Enter amount to invest in MSTY: $"))
                if amt > self.state.cash_reserves:
                    print("❌ Not enough cash reserves.")
                    return
                self.state.cash_reserves -= amt
                self.state.msty_shares += amt / self.state.msty_price
                print(f"✅ Bought ${amt:,.2f} worth of MSTY shares.")

            elif sub_choice == "2":
                amt = float(input("Enter amount to pay toward loan: $"))
                if amt > self.state.cash_reserves:
                    print("❌ Not enough cash reserves.")
                    return
                self.state.cash_reserves -= amt
                self.state.loan_balance = max(0, self.state.loan_balance - amt)
                print(f"✅ Paid down ${amt:,.2f} of loan balance.")

        elif choice == "5":
            print("👋 Game over. Exiting.")
            exit()

        else:
            if self.state.net_cash > 0:
                self.state.cash_reserves += self.state.net_cash
                print(f"💰 Added ${self.state.net_cash:,.2f} to cash reserves.")
                self.state.net_cash = 0
            else:
                print("⏭️ No action taken this month.")

    def run(self):
        while not self.state.fail:
            self.play_turn()
            self.state.month += 1
