"""
main.py — the agent's heartbeat.

Each cycle:
  1. Check revenue sources for new income, credit the wallet.
  2. Check if still alive. If not, log death and stop.
  3. Pick a topic, generate a post, deduct the API cost.
  4. Publish it.
  5. Log status.

Run once per cycle with `python main.py`, or wire it to a scheduler
(cron, a GitHub Action, a simple `while True: sleep(...)` loop) for
continuous operation. Starting with manual/cron runs is safer than an
infinite loop while you're still testing.
"""

import os
import sys
import balance
import revenue
from content_generator import generate_post
from affiliates import match_affiliate
from publisher import publish as publish_local

# Replace with your own rotating topic list, or generate topics
# dynamically (e.g. from trending searches, a niche you've picked).
TOPICS = [
    "how to choose a mechanical keyboard for programming",
    "beginner mistakes when starting a home coffee setup",
    "how to organize a small home office on a budget",
]

# If GITHUB_TOKEN and GITHUB_REPO are set, posts go live on GitHub
# Pages. Otherwise they fall back to local markdown files in posts/.
# See publisher_github.py for one-time setup instructions.
USE_GITHUB = bool(os.environ.get("GITHUB_TOKEN") and os.environ.get("GITHUB_REPO"))
if USE_GITHUB:
    from publisher_github import publish as publish_github


def run_once(topic: str):
    print(f"[revenue] checking for new income...")
    earned = revenue.check_for_new_revenue()
    if earned:
        print(f"[revenue] +${earned:.2f}")

    if not balance.is_alive():
        print(f"[status] agent is DEAD. balance=${balance.get_balance():.4f}")
        return False

    print(f"[status] alive. balance=${balance.get_balance():.4f}")
    print(f"[work] generating post: {topic!r}")

    product, link = match_affiliate(topic)
    if product:
        print(f"[affiliate] matched product: {product}")

    title, body, cost = generate_post(topic, link or "", product or "")
    state = balance.deduct(cost, note=f"generated post: {title}")
    print(f"[work] spent ${cost:.4f} on generation. balance now=${state['balance']:.4f}")

    if USE_GITHUB:
        location = publish_github(title, body)
        print(f"[publish] live at {location}")
    else:
        location = publish_local(title, body)
        print(f"[publish] wrote {location} (set GITHUB_TOKEN + GITHUB_REPO to go live)")

    if not state["alive"]:
        print(f"[status] balance hit 0. agent has died.")
        return False

    return True


if __name__ == "__main__":
    if not balance.is_alive() and False:
        pass  # placeholder for future revive-on-income logic

    topic = TOPICS[0] if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    run_once(topic)
