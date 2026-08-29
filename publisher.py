"""
publisher.py — turns a generated post into something published.

Right now this just writes a markdown file into posts/. That's
intentionally the simplest possible "publish" step so you can test
the whole loop with zero external accounts. Real options to swap in
later (pick one):

  - Ghost / WordPress: POST to their REST API instead of writing a file
  - GitHub Pages / Jekyll: commit the markdown file to a repo (use
    the GitHub API) and let Pages build it
  - Substack / Beehiiv: most don't have public post-creation APIs;
    you'd likely use their email-in publishing address instead
  - Medium: has a public API for posting under your account

Whatever you pick, keep the function signature (title, body) -> url
so nothing else in the agent has to change.
"""

import os
import re
from datetime import datetime, timezone

POSTS_DIR = os.path.join(os.path.dirname(__file__), "posts")


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60]


def publish(title: str, body_markdown: str) -> str:
    os.makedirs(POSTS_DIR, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    path = os.path.join(POSTS_DIR, filename)

    frontmatter = (
        "---\n"
        f"title: \"{title}\"\n"
        f"date: {date_str}\n"
        "---\n\n"
    )
    with open(path, "w") as f:
        f.write(frontmatter + body_markdown)

    return path
