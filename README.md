# Crazy Time result logger

Logs results from a Crazy Time tracking page to `results.csv`, polling
every 15 seconds. Meant to run continuously as a background worker.

## Before deploying — check the selector

Open the results page in your browser, right-click the newest result in
the history list, choose "Inspect", and find the CSS selector (class name)
of the element wrapping each result. Put it in `scraper.py`:

```python
SELECTOR = ".result-item"  # replace with the real one
```

Without the right selector the script will run but log nothing useful.

## Deploy on Railway

Railway's "Describe your project or paste a repo link" screen wants a
GitHub repository, not local files, so:

1. Create a new (empty) repository on GitHub, e.g. `crazytime-tracker`.
2. Push this folder to it:
   ```
   cd crazytime-tracker
   git init
   git add .
   git commit -m "initial"
   git branch -M main
   git remote add origin https://github.com/<your-username>/crazytime-tracker.git
   git push -u origin main
   ```
3. In Railway, paste that repo's URL (`https://github.com/<your-username>/crazytime-tracker`)
   into the "paste a repo link" field.
4. Railway will detect the `Dockerfile` and build it automatically.
5. Deploy — it will start running continuously, appending new results to
   `results.csv` inside the container.

## Important: the CSV disappears on redeploy

Railway containers are ephemeral by default — `results.csv` will be wiped
whenever the service restarts or redeploys, unless you either:

- **Attach a Railway Volume** (Settings → Volumes → mount at `/app/data`,
  and set `CSV_PATH=/app/data/results.csv` as an environment variable), or
- **Write to Google Sheets instead of a local CSV** — more setup, but
  survives redeploys and you can open it live from anywhere. Ask me if
  you want this version of the script instead.

## A couple of things worth knowing

- This scrapes a third-party site's page. Sites can and do change their
  markup, rate-limit, or block automated requests — expect to maintain
  this occasionally.
- Every Crazy Time spin is statistically independent; logged history has
  no predictive value for future spins.
