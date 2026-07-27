# Kerala University Results RSS Feed

Small script that converts updates from the Kerala University results
page into an RSS feed (`feed.xml`).

Quickstart

- Install dependencies:

```bash
python -m pip install -r requirements.txt
```

- Edit `check_results.py`: set `FEED_SELF_LINK` to your feed URL and
  update `KEYWORD` to the terms you want to match.

- Run once locally:

```bash
python check_results.py
```

Notes

- Matching is case-insensitive.
- The script records seen entries in `last_seen.json` and writes
  `feed.xml`.
- You can schedule runs using GitHub Actions if desired.

Feed example:

https://jerinsirijadev.github.io/KU-Result-RSS/feed.xml
