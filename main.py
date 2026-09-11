"""
main.py — the agent's daily loop.

This is what actually runs the "starving agent":
1. Make sure the wallet exists (first run only).
2. If the agent is out of money, stop and notify — don't keep trying.
3. Check for any new affiliate/ad revenue and credit it.
4. Pick a topic, generate a post, attach an affiliate link if one matches.
5. Publish the post (writes into posts/ in this repo).
6. Deduct the notional cost of the post from the wallet.
7. Report the result to Telegram.
"""

import os
import random

import requests

from affiliates import match_affiliate
from balance import DATA_PATH, credit, deduct, get_balance, init_wallet, is_alive
from content_generator import generate_post
from publisher import publish
from revenue import check_for_new_revenue

STARTING_BALANCE = 5.00

# Topics the agent rotates through. Add more any time — one per line.
TOPICS = [
    "How to choose a mechanical keyboard",
    "Setting up a home office on a budget",
    "Beginner's guide to home espresso",
    "How to pick a standing desk",
    "Simple habits for better sleep",
    "How to organize a small kitchen",
    "Getting started with houseplants",
    "Choosing your first road bike",
]


def send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=15,
        )
    except Exception as e:
        # Never let a Telegram hiccup crash the whole run.
        print(f"Telegram notify failed: {e}")


def run_bot() -> None:
    print("Agent is starting...")

    if not os.path.exists(DATA_PATH):
        init_wallet(STARTING_BALANCE)
        print(f"Wallet initialized with ${STARTING_BALANCE:.2f}")

    if not is_alive():
        msg = (
            f"💀 *Agent is out of funds.*\n\n"
            f"Balance: ${get_balance():.4f}\n"
            f"It has stopped posting. Add funds via balance.credit() to revive it."
        )
        send_telegram(msg)
        print("Agent is dead (balance <= 0). Stopping without posting.")
        return

    try:
        earned = check_for_new_revenue()
        if earned:
            print(f"Credited ${earned:.4f} in new revenue.")
    except Exception as e:
        print(f"Revenue check failed (non-fatal): {e}")

    topic = random.choice(TOPICS)
    product, link = match_affiliate(topic)

    try:
        title, body, cost = generate_post(
            topic,
            affiliate_link=link or "",
            affiliate_product=product or "",
        )
        path = publish(title, body)
        state = deduct(cost, note=f"post: {title}")

        affiliate_line = f"\n🔗 *Affiliate:* {product}" if product else ""
        status_report = (
            f"🚀 *New post published!*\n\n"
            f"📝 *Title:* {title}\n"
            f"📂 *File:* {os.path.basename(path)}"
            f"{affiliate_line}\n"
            f"💰 *Balance:* ${state['balance']:.4f}"
        )
        send_telegram(status_report)
        print(f"Success! Published '{title}'. Balance: ${state['balance']:.4f}")

    except Exception as e:
        error_msg = f"❌ *Bot Error:*\n{str(e)}"
        send_telegram(error_msg)
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    run_bot()
