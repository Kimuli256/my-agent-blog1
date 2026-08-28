"""
revenue.py — where real money would come back INTO the wallet.

This is a stub on purpose. Ad revenue and affiliate commissions
aren't available in real time through a simple API call — they show
up in dashboards on a delay (days to weeks), and most networks
require you to apply and get approved as a human first:

  - Affiliate networks: Amazon Associates, ShareASale, Impact,
    Awin, Skimlinks — apply for an account yourself, get an
    affiliate ID, put your links in the generated posts (see
    content_generator.generate_post's affiliate_link param).
    Most give you a reporting API or CSV export you can poll here.
  - Ad revenue: Google AdSense (has a Management API for reading
    earnings), YouTube Partner Program, newsletter sponsorships.

check_for_new_revenue() below is a placeholder that always returns 0.
When you've picked a network and have API credentials, replace the
body with a real call to their reporting endpoint and credit()
whatever came in since the last check.
"""

from balance import credit


def check_for_new_revenue() -> float:
    """
    Poll your real revenue source(s) here and return the amount
    earned since the last check. Wire this to:
      - an affiliate network's reporting API, or
      - AdSense Management API, or
      - a Stripe balance webhook / poll, etc.
    """
    new_earnings = 0.0

    if new_earnings > 0:
        credit(new_earnings, note="revenue check")

    return new_earnings
