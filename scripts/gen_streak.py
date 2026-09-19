"""Nixie-style contribution streak card, self-hosted instead of streak-stats.demolab.com.

Reads the contribution calendar from GitHub's GraphQL API (one query per
contribution year), computes total contributions, the current streak and the
longest streak, and writes an 800x195 SVG:
    GITHUB_TOKEN=... python scripts/gen_streak.py PolyLvst out/metrics.streak.svg

The current streak stays alive through "today" even before today's first
contribution, the same way GitHub and streak-stats treat it. "Today" is taken
at STREAK_UTC_OFFSET hours (default 7, Asia/Jakarta, which has no DST).
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone

API = "https://api.github.com/graphql"
A = "#ff9f1c"
FONT = "'Share Tech Mono','Courier New',Consolas,monospace"
# Octicons flame-16 (MIT, github.com/primer/octicons)
FLAME = ("M9.533.753V.752c.217 2.385 1.463 3.626 2.653 4.81C13.37 6.74 14.498 7.863 14.498 10c0 3.5-3 6-6.5 6S1.5 "
         "13.512 1.5 10c0-1.298.536-2.56 1.425-3.286.376-.308.862 0 1.035.454C4.46 8.487 5.581 8.419 6 8c.282-.282."
         "341-.811-.003-1.5C4.34 3.187 7.035.75 8.77.146c.39-.137.726.194.763.607ZM7.998 14.5c2.832 0 5-1.98 5-4.5 "
         "0-1.463-.68-2.19-1.879-3.383l-.036-.037c-1.013-1.008-2.3-2.29-2.834-4.434-.322.256-.63.579-.864.953-.432."
         "696-.621 1.58-.046 2.73.473.947.67 2.284-.278 3.232-.61.61-1.545.84-2.403.633a2.79 2.79 0 0 1-1.436-.874A3."
         "198 3.198 0 0 0 3 10c0 2.53 2.164 4.5 4.998 4.5Z")


def graphql(token, query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch_days(token, login):
    """{date: count} for every day since the first contribution year."""
    years = graphql(token, "query($login: String!) { user(login: $login) { contributionsCollection { contributionYears } } }",
                    {"login": login})["user"]["contributionsCollection"]["contributionYears"]
    query = """query($login: String!, $from: DateTime!, $to: DateTime!) { user(login: $login) {
      contributionsCollection(from: $from, to: $to) { contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }"""
    days = {}
    for year in sorted(years):
        cal = graphql(token, query, {"login": login, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"})
        for week in cal["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                days[date.fromisoformat(day["date"])] = day["contributionCount"]
    return days


def compute(days, today):
    active = sorted(d for d, n in days.items() if n > 0 and d <= today)
    total = sum(n for d, n in days.items() if d <= today)

    # current: walk back from today (or yesterday, if nothing yet today)
    cur_end = today if days.get(today, 0) > 0 else today - timedelta(days=1)
    cur_start, d = None, cur_end
    while days.get(d, 0) > 0:
        cur_start, d = d, d - timedelta(days=1)
    current = (cur_start, cur_end, (cur_end - cur_start).days + 1) if cur_start else (None, None, 0)

    # longest: scan consecutive active days
    longest, run_start, prev = (None, None, 0), None, None
    for d in active:
        run_start = d if prev is None or d - prev != timedelta(days=1) else run_start
        length = (d - run_start).days + 1
        if length > longest[2]:
            longest = (run_start, d, length)
        prev = d
    return {"total": total, "first": active[0] if active else None, "current": current, "longest": longest}


def fmt(d, today):
    return f"{d:%b} {d.day}" if d.year == today.year else f"{d:%b} {d.day}, {d.year}"


def span(start, end, today):
    if not start:
        return "no streak yet"
    return fmt(start, today) if start == end else f"{fmt(start, today)} - {fmt(end, today)}"


def render(stats, today):
    cur_start, cur_end, cur_len = stats["current"]
    lon_start, lon_end, lon_len = stats["longest"]
    first = f"{fmt(stats['first'], today)} - Present" if stats["first"] else "no contributions yet"
    circ = 2 * 3.14159265 * 40
    gap = 30  # opening at the top of the ring, where the flame sits
    gap_deg = gap / circ * 360

    def column(x, value, label, sub):
        return f"""
  <text x="{x}" y="104" class="num" font-size="40" filter="url(#glow)">{value}</text>
  <text x="{x}" y="136" class="label">{label}</text>
  <text x="{x}" y="160" class="sub">{sub}</text>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="195" viewBox="0 0 800 195" font-family="{FONT}">
  <defs>
    <style>
      text {{ fill: {A}; text-anchor: middle; }}
      .num {{ font-weight: bold; letter-spacing: 2px; }}
      .label {{ font-size: 12px; letter-spacing: 2px; fill-opacity: 0.75; }}
      .sub {{ font-size: 11px; letter-spacing: 1px; fill-opacity: 0.5; }}
    </style>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="{A}" fill-opacity="0.05"/>
    </pattern>
  </defs>
  <rect x="1" y="1" width="798" height="193" rx="6" fill="#0b0b0b" stroke="{A}" stroke-opacity="0.35"/>
  <rect x="1" y="1" width="798" height="193" rx="6" fill="url(#scan)"/>
  <text x="20" y="24" font-size="11" letter-spacing="2" fill-opacity="0.55" style="text-anchor: start">STREAK MONITOR // DAILY</text>
  <line x1="267" y1="44" x2="267" y2="172" stroke="{A}" stroke-opacity="0.25"/>
  <line x1="533" y1="44" x2="533" y2="172" stroke="{A}" stroke-opacity="0.25"/>
{column(133, f"{stats['total']:,}", "TOTAL CONTRIBUTIONS", first)}

  <circle cx="400" cy="84" r="40" fill="none" stroke="{A}" stroke-width="5" stroke-linecap="round"
    stroke-dasharray="{circ - gap:.1f} {gap}" transform="rotate({-90 + gap_deg / 2:.1f} 400 84)" filter="url(#glow)"/>
  <path d="{FLAME}" fill="{A}" transform="translate(389 32) scale(1.4)" filter="url(#glow)"/>
  <text x="400" y="97" class="num" font-size="34" filter="url(#glow)">{cur_len}</text>
  <text x="400" y="150" class="label" font-weight="bold" fill-opacity="1">CURRENT STREAK</text>
  <text x="400" y="172" class="sub">{span(cur_start, cur_end, today)}</text>
{column(667, lon_len, "LONGEST STREAK", span(lon_start, lon_end, today))}
</svg>
"""


def main():
    login, out = sys.argv[1], sys.argv[2]
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("set GITHUB_TOKEN")
    today = datetime.now(timezone(timedelta(hours=float(os.environ.get("STREAK_UTC_OFFSET", "7"))))).date()
    stats = compute(fetch_days(token, login), today)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(stats, today))
    print(f"total={stats['total']} current={stats['current'][2]} longest={stats['longest'][2]} -> {out}")


if __name__ == "__main__":
    main()
