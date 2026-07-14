# Kerala University Results RSS Feed

Watches the [Kerala University results page](https://exams.keralauniversity.ac.in/Login/check8)
and turns matching result notifications into an RSS feed. Runs on GitHub's
free infrastructure.

## Make your own KU results RSS feed

1. **Clone this repo:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
   cd YOUR-REPO
   ```

2. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Set your feed URL**, then edit this line in `check_results.py`:
   ```python
   FEED_SELF_LINK = "https://YOUR-USERNAME.github.io/YOUR-REPO/feed.xml"
   ```

4. **Push to your own GitHub repo.**

5. **Enable GitHub Pages:**
   Repo → Settings → Pages → Source: Deploy from a branch → `main` / root.

6. **Enable Actions write access:**
   Repo → Settings → Actions → General → Workflow permissions →
   "Read and write permissions."

7. **Run it once manually** to generate the first feed:
   Repo → Actions tab → "Check KU SDE Results" → Run workflow.

8. **Your feed is now live at:**
   ```
   https://YOUR-USERNAME.github.io/YOUR-REPO/feed.xml
   ```
   Subscribe to that URL in any RSS reader (Feeder ,Feedly, etc.)

## How it works

- Runs on a schedule via GitHub Actions (default: every 4 hours, 
  change the `cron` line in `.github/workflows/check.yml` to adjust).
- Fetches the results page and extracts every entry.
- Keeps only entries whose title contains **every** keyword listed in
  `KEYWORDS` (all must match, not just one).
- Tracks already-seen entries in `last_seen.json` so nothing gets
  re-notified twice.
- Rebuilds `feed.xml` every run so the feed always reflects the current
  matching entries.

## Changing the keywords

Edit this line in `check_results.py`:
```python
KEYWORDS = ["SDE","Computer Science"]
```

A result must contain all listed keywords to be included.
Use a single-item list (e.g. ["SDE"]) to match on just one keyword.
Add more items to require multiple keywords together — for example, ["SDE", "B.Com"] would only match results that mention both.
Matching is case-insensitive.
Want matches on any keyword instead of requiring all of them? 
In check_results.py, inside main(), change 'all' to 'any' in this line: 
```python
if all(k in e["title"].lower() for k in keywords_lower)
```
## If parsing breaks

Kerala University may occasionally change their HTML layout. If the
script starts finding 0 matches or titles look garbled:

1. Run it locally: `python check_results.py`
2. View the live page's HTML source around a result entry.
3. Adjust the extraction logic in `parse_entries()` inside
   `check_results.py` to match the new structure.

>This is built specifically for [Kerala University results page](https://exams.keralauniversity.ac.in/Login/check8)
