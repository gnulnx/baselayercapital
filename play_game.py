from game_engine import GameEngine
from utils.config_loader import load_config_ns

cfg = load_config_ns("base")

engine = GameEngine(cfg)
engine.run()
