"""
affiliates.py — matches a topic to an affiliate product/link.

Edit affiliates.json to add your real affiliate links (Amazon
Associates, ShareASale, Impact, etc. — whatever you signed up for).
Each entry needs keywords, a product name, and your affiliate link
for that product. The first entry whose keywords appear in the topic
wins; if nothing matches, no affiliate link is added to that post.
"""

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "affiliates.json")


def load_affiliates():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def match_affiliate(topic: str):
    """Returns (product, link) or (None, None) if nothing matches."""
    topic_lower = topic.lower()
    for entry in load_affiliates():
        if any(kw.lower() in topic_lower for kw in entry["keywords"]):
            return entry["product"], entry["link"]
    return None, None
