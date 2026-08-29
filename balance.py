"""
balance.py — the agent's "wallet" and life-support system.

For now this is a JSON file acting as a stand-in wallet. Swap the
functions below for real calls to Stripe's Balance API, a bank API,
or a crypto wallet SDK once you're ready to connect real money.
The rest of the agent doesn't need to know the difference — it only
calls get_balance(), deduct(), and credit().
"""

import json
import os
from datetime import datetime, timezone

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "balance.json")


def _load():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"No wallet found at {DATA_PATH}. Run init_wallet(starting_balance) first."
        )
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def _save(state):
    with open(DATA_PATH, "w") as f:
        json.dump(state, f, indent=2)


def init_wallet(starting_balance: float):
    """Fund the agent for the first time. Call this once, manually."""
    state = {
        "balance": round(starting_balance, 4),
        "alive": True,
        "born_at": datetime.now(timezone.utc).isoformat(),
        "died_at": None,
        "history": [
            {
                "type": "funding",
                "amount": starting_balance,
                "note": "initial funding",
                "at": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    _save(state)
    return state


def get_balance() -> float:
    return _load()["balance"]


def is_alive() -> bool:
    return _load()["alive"]


def deduct(amount: float, note: str = ""):
    """Spend money. If this drains the balance to 0 or below, the agent dies."""
    state = _load()
    state["balance"] = round(state["balance"] - amount, 4)
    state["history"].append(
        {"type": "expense", "amount": amount, "note": note, "at": datetime.now(timezone.utc).isoformat()}
    )
    if state["balance"] <= 0 and state["alive"]:
        state["alive"] = False
        state["died_at"] = datetime.now(timezone.utc).isoformat()
        state["history"].append(
            {"type": "death", "amount": 0, "note": "balance depleted", "at": state["died_at"]}
        )
    _save(state)
    return state


def credit(amount: float, note: str = ""):
    """Earn money. Can revive a dead agent if you want that behavior — see main.py."""
    state = _load()
    state["balance"] = round(state["balance"] + amount, 4)
    state["history"].append(
        {"type": "income", "amount": amount, "note": note, "at": datetime.now(timezone.utc).isoformat()}
    )
    _save(state)
    return state


if __name__ == "__main__":
    # Quick manual test / first-time setup
    if not os.path.exists(DATA_PATH):
        init_wallet(5.00)
        print("Wallet created with $5.00 starting balance.")
    print(_load())
