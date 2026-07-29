"""Scrape the public GitHub contributions calendar and write data/contributions.json.

No auth/PAT required — this hits the same HTML fragment endpoint GitHub's own
profile page uses to render the contributions graph. Since it depends on
GitHub's markup (which can change without notice), it fails loudly instead of
silently writing an empty/wrong grid.
"""

import datetime
import json
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "PriteshThorat"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_html() -> str:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # GitHub renders the count/date as accessible text in a separate
    # <tool-tip for="<td id>">...</tool-tip> element rather than inline on
    # the <td> itself, so build a lookup from cell id -> tooltip text first.
    tooltip_by_id = {}
    for tip in soup.select("tool-tip[for]"):
        tooltip_by_id[tip.get("for")] = tip.get_text(strip=True)

    days = []
    for cell in soup.select("td[data-date]"):
        date = cell.get("data-date")
        level = cell.get("data-level")
        count_text = tooltip_by_id.get(cell.get("id"), "") or cell.get("data-count") or cell.get("aria-label") or ""
        if date:
            days.append({"date": date, "level": level, "count_text": count_text})

    if not days:
        raise RuntimeError(
            "No contribution day cells found in the scraped HTML. "
            "GitHub's markup for the contributions fragment may have changed — "
            "refusing to write an empty/incorrect heatmap."
        )
    return days


def extract_count(count_text: str) -> int:
    lowered = count_text.lower()
    if lowered.startswith("no contributions"):
        return 0
    digits = ""
    for ch in count_text:
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    return int(digits) if digits else 0


def normalize_level(raw_level, count: int) -> int:
    if raw_level is not None:
        try:
            return max(0, min(4, int(raw_level)))
        except ValueError:
            pass
    # Fallback heuristic if data-level isn't present.
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    return 4


def build_weeks(days):
    parsed = []
    for day in days:
        if not day["date"]:
            continue
        date_obj = datetime.date.fromisoformat(day["date"])
        count = extract_count(day["count_text"])
        level = normalize_level(day["level"], count)
        parsed.append({"date": day["date"], "level": level, "count": count, "_dow": date_obj.weekday()})

    if not parsed:
        raise RuntimeError("Parsed zero valid day entries from scraped HTML.")

    parsed.sort(key=lambda d: d["date"])

    # Python weekday(): Monday=0..Sunday=6. GitHub's grid starts on Sunday.
    def sunday_index(dow: int) -> int:
        return (dow + 1) % 7

    weeks = []
    current_week = [None] * 7
    first_date = datetime.date.fromisoformat(parsed[0]["date"])
    current_week_start = first_date - datetime.timedelta(days=sunday_index(first_date.weekday()))

    for entry in parsed:
        date_obj = datetime.date.fromisoformat(entry["date"])
        days_since_week_start = (date_obj - current_week_start).days
        if days_since_week_start >= 7:
            weeks.append(current_week)
            current_week = [None] * 7
            current_week_start = current_week_start + datetime.timedelta(days=7)
            days_since_week_start = (date_obj - current_week_start).days
        idx = sunday_index(date_obj.weekday())
        current_week[idx] = {"date": entry["date"], "level": entry["level"], "count": entry["count"]}

    weeks.append(current_week)
    return weeks, sum(e["count"] for e in parsed)


def main():
    try:
        html = fetch_html()
        days = parse_days(html)
        weeks, total = build_weeks(days)
    except Exception as exc:  # noqa: BLE001 - deliberate: fail loudly, no silent fallback
        print(f"ERROR: failed to fetch/parse contributions: {exc}", file=sys.stderr)
        sys.exit(1)

    output = {
        "username": USERNAME,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_contributions": total,
        "weeks": weeks,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(weeks)} weeks, {total} total contributions)")


if __name__ == "__main__":
    main()
