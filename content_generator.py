"""
content_generator.py — the agent's only "labor."

Calls the Google Gemini API (free tier, no card required) to write a
short affiliate-style blog post on a topic. On the free tier the real
cost is $0, but we still track a small notional cost per post so the
survival mechanic has something to count down.
"""

import os
import re
import requests

MODEL = "gemini-3.6-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# Free tier costs $0 in real money. This is a placeholder so the
# balance still counts down for the survival mechanic.
NOTIONAL_COST_PER_POST = 0.01


def generate_post(topic: str, affiliate_link: str = "", affiliate_product: str = ""):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set GEMINI_API_KEY in your environment before running the agent."
        )

    affiliate_instruction = ""
    if affiliate_link and affiliate_product:
        affiliate_instruction = (
            f"\nNaturally mention and link to this product where relevant: "
            f"{affiliate_product} — {affiliate_link}. Do not force it if it doesn't fit."
        )

    prompt = f"""Write a short, genuinely useful blog post (300-500 words) about: {topic}

Format:
- Start with a single line: TITLE: <title>
- Then the body in markdown, no headers repeating the title.
- Write in a clear, honest, non-salesy voice. No hype, no fake urgency.
{affiliate_instruction}
"""

    resp = requests.post(
        f"{API_URL}?key={api_key}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")

    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]

    match = re.search(r"TITLE:\s*(.+)", text)
    title = match.group(1).strip() if match else topic
    body = re.sub(r"TITLE:\s*.+\n?", "", text, count=1).strip()

    return title, body, NOTIONAL_COST_PER_POST
