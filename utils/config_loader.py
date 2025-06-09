# config_loader.py
import importlib
from types import SimpleNamespace


def load_config_ns(scenario: str) -> SimpleNamespace:
    mod = importlib.import_module(f"scenarios.{scenario}")
    return SimpleNamespace(
        **{k: getattr(mod, k) for k in dir(mod) if not k.startswith("__")}
    )
