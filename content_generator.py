"""
content_generator.py — the agent's only "labor."

Calls the Claude API to write a short affiliate-style blog post on a
topic. This is deliberately simple: one call in, one post out. Cost
estimation is approximate (token count x a per-token price) — good
enough to drive the survival mechanic, not meant to be exact billing.
"""

import os
import re
import anthropic

MODEL = "claude-sonnet-4-6"

# Rough public per-token pricing for the model above (USD). Update if
# pricing changes — this is only used to decide how much to deduct
# from the agent's own balance per call, not for real billing.
PRICE_PER_INPUT_TOKEN = 3.00 / 1_000_000
PRICE_PER_OUTPUT_TOKEN = 15.00 / 1_000_000


def estimate_cost(usage) -> float:
    return (
        usage.input_tokens * PRICE_PER_INPUT_TOKEN
        + usage.output_tokens * PRICE_PER_OUTPUT_TOKEN
    )


def generate_post(topic: str, affiliate_link: str = "", affiliate_product: str = ""):
    """
    Returns (title, body_markdown, cost_usd).
    Raises if ANTHROPIC_API_KEY isn't set.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set ANTHROPIC_API_KEY in your environment before running the agent."
        )

    client = anthropic.Anthropic(api_key=api_key)

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

    response = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(block.text for block in response.content if block.type == "text")
    cost = estimate_cost(response.usage)

    match = re.search(r"TITLE:\s*(.+)", text)
    title = match.group(1).strip() if match else topic
    body = re.sub(r"TITLE:\s*.+\n?", "", text, count=1).strip()

    return title, body, cost
