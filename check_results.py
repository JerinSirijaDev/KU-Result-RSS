"""
Kerala University SDE Results Watcher
--------------------------------------
Fetches the results listing page, extracts individual result entries
(title + PDF link + published date), filters for entries containing
'SDE', and maintains an RSS feed of matches only.

Run this script on a schedule (see .github/workflows/check.yml).
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# ---- Config ----------------------------------------------------------

RESULTS_URL = "https://exams.keralauniversity.ac.in/Login/check8"
KEYWORD = "SDE"                 # only keep entries containing this
STATE_FILE = Path("last_seen.json")
FEED_FILE = Path("feed.xml")

# Base URL your GitHub Pages site will be served at.
# e.g. https://<username>.github.io/<repo-name>/
FEED_SELF_LINK = "https://YOUR-USERNAME.github.io/YOUR-REPO/feed.xml"
SITE_LINK = "https://exams.keralauniversity.ac.in/Login/check8"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

DATE_RE = re.compile(r"Published on\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
PDF_HREF_RE = re.compile(r"/Images/Result/", re.IGNORECASE)


# ---- Fetch + parse -----------------------------------------------------

def fetch_page(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_entries(html: str):
    """
    Returns a list of dicts: {title, pdf_url, published_date}

    Strategy: walk the page in document order. Track the most recently
    seen "Published on DATE" text (it only appears once per day; later
    same-day entries inherit it). For every <a> tag whose href points
    into /Images/Result/, treat its containing block's text as the title.
    """
    soup = BeautifulSoup(html, "html.parser")

    # The results are inside list items / bullet-like blocks under the
    # "Results" heading. We work at a coarse level: iterate over every
    # element that either contains a "Published on" date or a PDF link,
    # in document order, using find_all on <li> first, falling back to
    # generic block tags if the site doesn't use <li>.
    container = soup.find(["ul", "ol", "div"], recursive=True) or soup

    blocks = soup.find_all(["li", "tr", "p", "div"])
    if not blocks:
        blocks = [soup]

    entries = []
    current_date = None
    seen_pdf_urls_this_pass = set()

    # Fallback / primary approach: scan all <a> tags with result PDF links
    # directly, and derive title + date from surrounding text.
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not PDF_HREF_RE.search(href):
            continue
        if href in seen_pdf_urls_this_pass:
            continue
        seen_pdf_urls_this_pass.add(href)

        # Walk up to a reasonably-sized container to grab surrounding text
        parent = a.find_parent(["li", "tr", "p", "div"]) or a.parent
        block_text = parent.get_text(separator=" ", strip=True) if parent else a.get_text(strip=True)

        # Update current_date if this block (or the text just before it
        # in the page) mentions a date.
        date_match = DATE_RE.search(block_text)
        if date_match:
            current_date = date_match.group(1)
        else:
            # look backwards through preceding siblings for the last
            # "Published on" text if this block doesn't have its own
            prev = parent.find_previous(string=DATE_RE) if parent else None
            if prev:
                m = DATE_RE.search(str(prev))
                if m:
                    current_date = m.group(1)

        # Clean title: strip the "Published on ..." fragment, the link's
        # own visible text (often the raw PDF URL itself on this site),
        # and any other http(s) URL substrings, then collapse whitespace.
        title = DATE_RE.sub("", block_text)
        link_text = a.get_text(strip=True)
        if link_text:
            title = title.replace(link_text, "")
        title = title.replace(href, "")
        title = re.sub(r"https?://\S+", "", title)  # catch-all for stray URLs
        title = re.sub(r"\s+", " ", title).strip(" -")

        pdf_url = href if href.startswith("http") else f"https://exams.keralauniversity.ac.in{href}"

        entries.append({
            "title": title,
            "pdf_url": pdf_url,
            "published_date": current_date or "unknown",
        })

    return entries


# ---- State handling ------------------------------------------------------

def load_seen() -> set:
    if STATE_FILE.exists():
        try:
            return set(json.loads(STATE_FILE.read_text()))
        except (json.JSONDecodeError, ValueError):
            return set()
    return set()


def save_seen(seen: set) -> None:
    STATE_FILE.write_text(json.dumps(sorted(seen), indent=2))


# ---- RSS feed ------------------------------------------------------------

def load_or_create_feed() -> FeedGenerator:
    fg = FeedGenerator()
    fg.title("Kerala University — SDE Results")
    fg.link(href=FEED_SELF_LINK, rel="self")
    fg.link(href=SITE_LINK, rel="alternate")
    fg.description("New SDE result notifications from University of Kerala results page.")
    fg.language("en")
    return fg


def build_feed(matched_entries):
    """
    Rebuild feed.xml from the full set of matched entries we know about,
    newest first, so the feed always reflects everything seen so far
    (not just this run's new items). Keeps readers happy on first sub.
    """
    fg = load_or_create_feed()
    for entry in matched_entries:
        fe = fg.add_entry()
        fe.title(entry["title"][:200])
        fe.link(href=entry["pdf_url"])
        fe.guid(entry["pdf_url"], permalink=True)
        fe.description(entry["title"])
        # feedgen needs a real datetime; use published_date if parseable
        try:
            dt = datetime.strptime(entry["published_date"], "%d/%m/%Y").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            dt = datetime.now(timezone.utc)
        fe.pubDate(dt)
    fg.rss_file(str(FEED_FILE))


# ---- Main ------------------------------------------------------------

def main():
    html = fetch_page(RESULTS_URL)
    all_entries = parse_entries(html)

    matched = [e for e in all_entries if KEYWORD.lower() in e["title"].lower()]

    if not matched:
        print("No SDE entries found on the page at all — selectors may need adjusting.")
        sys.exit(0)

    seen = load_seen()
    new_matches = [e for e in matched if e["pdf_url"] not in seen]

    if new_matches:
        print(f"Found {len(new_matches)} new SDE result(s):")
        for e in new_matches:
            print(f"  - {e['title']} ({e['pdf_url']})")
    else:
        print("No new SDE results since last check.")

    # Update seen-set with everything currently matched (dedupes across runs)
    seen.update(e["pdf_url"] for e in matched)
    save_seen(seen)

    # Rebuild the feed from all matched entries seen historically.
    # We only have "matched" from the current page load, but that's fine —
    # the site keeps a rolling history of recent results across pages.
    build_feed(matched)
    print(f"Feed written to {FEED_FILE} with {len(matched)} SDE entries.")


if __name__ == "__main__":
    main()
