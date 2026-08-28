"""
publisher_github.py — publishes posts to a live GitHub Pages blog.

Requires a GitHub repo set up for Pages with Jekyll (the default
GitHub Pages builder — no config needed beyond enabling Pages in the
repo's Settings). Uses GitHub's Contents API to create each post
file directly via HTTPS, so no git client or SSH keys needed.

Setup (one-time, do this yourself in a browser):
  1. Create a new repo, e.g. "my-agent-blog".
  2. Repo Settings → Pages → set Source to "Deploy from branch",
     branch "main", folder "/ (root)". Save.
  3. Add a minimal Jekyll config so it doesn't need a theme repo:
     create _config.yml with just `theme: jekyll-theme-minimal`
     (or any theme you like) at the repo root.
  4. Create a GitHub Personal Access Token (Settings → Developer
     settings → Fine-grained tokens) with "Contents: Read and write"
     permission scoped to that one repo.
  5. Set these environment variables:
       GITHUB_TOKEN=ghp_...
       GITHUB_REPO=yourusername/my-agent-blog
       GITHUB_BRANCH=main   (optional, defaults to main)

Your site will be live at https://yourusername.github.io/my-agent-blog/
within a minute or two of the first push (GitHub Pages builds on push).
"""

import base64
import os
import re
from datetime import datetime, timezone

import requests

API_ROOT = "https://api.github.com"


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60]


def publish(title: str, body_markdown: str) -> str:
    """
    Pushes a Jekyll-formatted post to _posts/ in the configured repo.
    Returns the live URL of the post (best-effort guess based on repo
    name — Jekyll's default permalink scheme).
    """
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO")
    branch = os.environ.get("GITHUB_BRANCH", "main")

    if not token or not repo:
        raise RuntimeError(
            "Set GITHUB_TOKEN and GITHUB_REPO environment variables first. "
            "See the setup instructions at the top of publisher_github.py."
        )

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    path_in_repo = f"_posts/{filename}"

    frontmatter = (
        "---\n"
        "layout: post\n"
        f"title: \"{title}\"\n"
        f"date: {date_str}\n"
        "---\n\n"
    )
    content = frontmatter + body_markdown
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    url = f"{API_ROOT}/repos/{repo}/contents/{path_in_repo}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {
        "message": f"Agent post: {title}",
        "content": content_b64,
        "branch": branch,
    }

    resp = requests.put(url, headers=headers, json=payload, timeout=30)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"GitHub publish failed ({resp.status_code}): {resp.text}")

    owner, name = repo.split("/")
    live_url = f"https://{owner}.github.io/{name}/{date_str.replace('-', '/')}/{slug}.html"
    return live_url
