# game_engine.py

from game_state import GameState
from utils.simulation import simulate_month


class GameEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.state = GameState(cfg)

    def play_turn(self):
        month_summary = simulate_month(self.state)
        print(f"\n--- MONTH {self.state.month} Simulation Results ---")
        # jprint(month_summary)
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
        while True:
            print("\nChoose an action:")
            print("1) Reinvest net cash into MSTY")
            print("2) Take BTC-backed loan")
            print("3) Use cash reserves to buy MSTY")
            print("4) Pay down loan principal")
            print("5) Take additional draw")
            print("6) Finish month")

            choice = input("Enter choice: ").strip()
            if choice == "6" or choice == "":
                if self.state.net_cash > 0:
                    self.state.cash_reserves += self.state.net_cash
                    print(
                        f"💰 Moved ${self.state.net_cash:,.2f} net cash into cash reserves."
                    )
                    self.state.net_cash = 0
                print("✅ Ending month.\n")
                break

            self.process_action(choice)

    def process_action(self, choice):
        if choice == "1":
            if self.state.net_cash > 0:
                shares_bought = self.state.net_cash / self.state.msty_price
                self.state.msty_shares += shares_bought
                print(
                    f"✅ Reinvested ${self.state.net_cash:,.2f} into {shares_bought:,.2f} MSTY shares."
                )
                self.state.net_cash = 0
            else:
                print("ℹ️ No net cash available to reinvest.")

        elif choice == "2":
            try:
                amount = float(input("Enter BTC-backed loan amount to take: $"))
            except ValueError:
                print("⚠️ Invalid number.")
                return
            self.state.loan_balance += amount
            self.state.cash_reserves += amount
            print(f"✅ Loan of ${amount:,.2f} added to cash reserves.")

        elif choice == "3":
            if self.state.cash_reserves <= 0:
                print("⚠️ No cash reserves available.")
                return
            try:
                amount = float(input("Enter cash reserve amount to invest: $"))
            except ValueError:
                print("⚠️ Invalid number.")
                return
            amount = min(amount, self.state.cash_reserves)
            shares_bought = amount / self.state.msty_price
            self.state.msty_shares += shares_bought
            self.state.cash_reserves -= amount
            print(
                f"✅ Bought {shares_bought:,.2f} MSTY shares with ${amount:,.2f} cash."
            )

        elif choice == "4":
            if self.state.loan_balance <= 0:
                print("ℹ️ No loan to pay down.")
                return
            try:
                amount = float(input("Enter amount to pay down on the loan: $"))
            except ValueError:
                print("⚠️ Invalid number.")
                return
            amount = min(amount, self.state.cash_reserves, self.state.loan_balance)
            self.state.loan_balance -= amount
            self.state.cash_reserves -= amount
            print(f"✅ Paid ${amount:,.2f} towards loan principal.")

        elif choice == "5":
            try:
                amount = float(input("Enter additional draw amount: $"))
            except ValueError:
                print("⚠️ Invalid number.")
                return
            self.state.extra_draw = amount
            print(f"✅ Scheduled extra draw of ${amount:,.2f} for next month.")

        else:
            print("❌ Invalid action.")

    def run(self):
        while not self.state.fail:
            self.play_turn()
            self.state.month += 1
