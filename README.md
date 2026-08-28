# Starving Agent

An AI agent with a real balance. It spends money to generate and
publish content, earns money back through affiliate/ad revenue, and
permanently stops when the balance hits $0.

## How it works

```
revenue.py  ──credits──▶  balance.py  ◀──debits──  content_generator.py
                              │
                        (alive? y/n)
                              │
                         main.py loop
                              │
                        publisher.py
```

- **balance.py** — the wallet. Starts as a local JSON file so you can
  test the whole loop for free. `deduct()` kills the agent (`alive:
  false`) the moment balance hits ≤ 0. Nothing else in the code
  checks money directly — everything goes through this file, so it's
  the one place you touch to plug in a real payment API later.
- **content_generator.py** — calls the Claude API to write a post.
  This is the agent's only real "cost" right now.
- **publisher.py** — writes the post to `posts/` as markdown. Swap
  this for a real CMS/API call when you're ready to actually publish
  somewhere people will see it.
- **revenue.py** — currently a stub that always returns $0. This is
  the one piece that depends on real accounts only you can set up
  (see below).
- **main.py** — runs one cycle: check revenue → check alive → generate
  → publish → log.

## Setup

```bash
cd starving_agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python balance.py        # creates data/balance.json with $5.00
python main.py            # runs one cycle
```

Each run prints the balance before and after, and where the post was
saved. Run `python main.py` again (or on a schedule) to keep going.
When the balance hits 0, it'll print that the agent has died and stop
producing.

## Making it earn real money

This is the part only you can do, since it requires your own
accounts:

### 1. Go live on GitHub Pages (already wired up)

`publisher_github.py` pushes each post straight to a GitHub repo
that's set up for Pages, so it's actually live on the internet.
One-time setup (instructions are also at the top of that file):

1. Create a repo, e.g. `my-agent-blog`.
2. Repo Settings → Pages → Source: "Deploy from branch", branch
   `main`, folder `/ (root)`.
3. Add `_config.yml` at the repo root with one line:
   `theme: jekyll-theme-minimal` (or any Jekyll theme).
4. Create a fine-grained GitHub Personal Access Token scoped to that
   repo with "Contents: Read and write" permission.
5. Set env vars: `GITHUB_TOKEN`, `GITHUB_REPO` (e.g.
   `yourusername/my-agent-blog`).

Once those are set, `main.py` automatically publishes there instead
of writing local files. Site goes live at
`https://yourusername.github.io/my-agent-blog/`.

### 2. Add real affiliate links (already wired up)

Edit `affiliates.json` — replace the example Amazon links with your
own affiliate links (sign up for Amazon Associates, ShareASale,
Impact, etc. first — this takes human approval, can't be automated).
`affiliates.py` matches each post's topic to a product by keyword and
`content_generator.py` weaves it in naturally.

### 3. Wire up real income tracking (still a stub — needs your accounts)

`revenue.py`'s `check_for_new_revenue()` always returns $0 right now.
Once you have an affiliate account, most networks offer a reporting
API or CSV export — replace the stub with a real call to that and
`credit()` the balance with whatever came in since the last check.

### 4. Make the wallet itself real (optional, later)

Right now `balance.py` tracks a number in a local JSON file. If you
want the "wallet" to be an actual account rather than a tracked
number, swap `get_balance()`/`deduct()`/`credit()` for calls to the
Stripe Balance API or your bank's API.

## Running it continuously

Don't start with an infinite loop — run it manually or via cron
(e.g. once a day) while you watch how fast it burns money and
whether the content is actually good. Once you trust it:

```cron
0 9 * * * cd /path/to/starving_agent && python main.py >> agent.log 2>&1
```

## Notes on cost estimation

`content_generator.py` estimates API cost from token usage using
public per-token pricing — it's an estimate for the survival
mechanic, not a real invoice. If you're also paying for hosting, a
domain, or other infra, add those as periodic `balance.deduct()`
calls too so the number reflects true running cost.
