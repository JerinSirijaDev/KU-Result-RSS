# Kerala University SDE Results RSS Feed

Watches the [Kerala University results page](https://exams.keralauniversity.ac.in/Login/check8)
and turns matching result notifications into an RSS feed. Runs on GitHub's
free infrastructure no server or always-on computer needed.

By default it watches for the keyword `SDE`, but you can change it to
anything (see below).

## Setup

1. **Clone this repo:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
   cd YOUR-REPO
   ```

2. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Set your feed URL** - edit this line in `check_results.py`:
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
   Subscribe to that URL in any RSS reader (Feedly, NetNewsWire, etc.)

## How it works

- Runs on a schedule via GitHub Actions (default: every 12 hours -
  change the `cron` line in `.github/workflows/check.yml` to adjust).
- Fetches the results page and extracts every entry.
- Keeps only entries whose title contains the configured keyword.
- Tracks already-seen entries in `last_seen.json` so nothing gets
  re-notified twice.
- Rebuilds `feed.xml` every run so the feed always reflects the current
  matching entries.

## Changing the keyword

Edit this line in `check_results.py`:
```python
KEYWORD = "SDE"
```
For example, to watch for BCA results instead:
```python
KEYWORD = "BCA"
```

## If parsing breaks

University sites occasionally change their HTML. If the script starts
finding 0 matches or titles look garbled:

1. Run it locally: `python check_results.py`
2. View the live page's HTML source around a result entry.
3. Adjust the extraction logic in `parse_entries()` inside
   `check_results.py` to match the new structure.