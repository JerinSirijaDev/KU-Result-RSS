# Kerala University SDE Results — RSS Feed

Watches https://exams.keralauniversity.ac.in/Login/check8 and produces
an RSS feed containing only result notifications whose title contains
`SDE`. Runs entirely on GitHub's free infrastructure — no server, no
always-on computer needed.

## Setup (one-time)

1. **Create a new GitHub repo** (public is simplest — e.g. `ku-sde-rss`).

2. **Push these files** to it:
   ```
   check_results.py
   requirements.txt
   .github/workflows/check.yml
   ```

3. **Edit `check_results.py`**: replace
   ```python
   FEED_SELF_LINK = "https://YOUR-USERNAME.github.io/YOUR-REPO/feed.xml"
   ```
   with your actual GitHub username and repo name.

4. **Enable GitHub Pages**:
   Repo → Settings → Pages → Source: `Deploy from a branch` → Branch: `main` / root.

5. **Enable Actions write permission**:
   Repo → Settings → Actions → General → Workflow permissions →
   select "Read and write permissions". (Needed so the workflow can
   commit the updated feed.xml back to the repo.)

6. **Trigger it once manually** to generate the first `feed.xml`:
   Repo → Actions tab → "Check KU SDE Results" → Run workflow.

7. Wait a minute, then your feed will be live at:
   ```
   https://YOUR-USERNAME.github.io/YOUR-REPO/feed.xml
   ```
   Subscribe to that URL in any RSS reader (Feedly, NetNewsWire, etc.)

## How it works

- Runs every 30 minutes via GitHub Actions cron (`.github/workflows/check.yml`).
- Fetches the results page, extracts every entry, filters for `SDE`
  (case-insensitive substring match) in the title.
- Tracks which PDF links have already been seen in `last_seen.json`
  (committed back to the repo each run) so re-runs don't re-notify.
- Rebuilds `feed.xml` from all currently-matched entries on the page
  each run — so your reader always has an accurate, deduplicated list.

## If parsing breaks

University sites occasionally tweak their HTML. If `check_results.py`
starts finding 0 SDE entries, or titles look garbled:

1. Run it locally: `python check_results.py` and check the printed output.
2. Inspect the live page's HTML (`view-source:` in browser) around a
   result entry, and adjust the parsing logic in `parse_entries()`
   in `check_results.py` — specifically how titles and dates are
   located relative to each PDF link.

## Changing the keyword

To watch for a different keyword instead of `SDE`, edit this line in
`check_results.py`:
```python
KEYWORD = "SDE"
```
