# game_engine.py
from game_state import GameState
from utils.simulation import simulate_month


class GameEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.state = GameState(cfg)

    def play_turn(self):
        print(f"\n--- MONTH {self.state.month} ---")
        # print(self.state.snapshot())

        month_summary = simulate_month(self.state)
        print("\n--- Simulation Results ---")
        for k, v in month_summary.items():
            print(f"{k:15}: {v}")

        # TODO: simulate turn, update state
        print("\nWhat would you like to do?")
        print("1) Take additional draw")
        print("2) Reinvest net cash")
        print("3) Trigger BTC-backed loan")
        print("4) End game")

        choice = input("Enter choice: ")
        self.process_action(choice)

    def process_action(self, choice):
        if choice == "4":
            print("Game over. Exiting.")
            exit()
        else:
            print(f"Action {choice} not implemented yet.")

    def run(self):
        while not self.state.fail:
            self.play_turn()
            self.state.month += 1
