"""
Crazy Time result logger.

Polls a results page every INTERVAL_SECONDS and appends any new result
to results.csv. Meant to run continuously (e.g. as a Railway worker).

IMPORTANT: You will likely need to adjust the CSS selector below (SELECTOR)
to match the actual page structure — sites change their markup often, and
I could not verify the exact selector for this page from here. Use your
browser's "Inspect element" on the results/history area of the page to
find the right one.
"""

import csv
import os
import time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

URL = "https://gamblingcounting.com/crazy-time"

# Adjust this selector to match the element(s) that show each result
# (e.g. a list item, table row, or span containing the latest outcome).
SELECTOR = ".result-item"  # <-- placeholder, verify and update this

INTERVAL_SECONDS = 15
CSV_PATH = os.environ.get("CSV_PATH", "results.csv")


def ensure_csv_header():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp_utc", "result"])


def load_last_seen():
    if not os.path.exists(CSV_PATH):
        return None
    with open(CSV_PATH, "r") as f:
        rows = list(csv.reader(f))
    if len(rows) <= 1:
        return None
    return rows[-1][1]


def append_result(result: str):
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(timezone.utc).isoformat(), result])


def main():
    ensure_csv_header()
    last_seen = load_last_seen()
    print(f"Starting. Last seen result: {last_seen}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)

        while True:
            try:
                page.reload(wait_until="networkidle", timeout=60000)
                elements = page.query_selector_all(SELECTOR)
                if elements:
                    latest = elements[0].inner_text().strip()
                    if latest and latest != last_seen:
                        append_result(latest)
                        print(f"New result logged: {latest}")
                        last_seen = latest
                else:
                    print("No elements matched SELECTOR — check and update it.")
            except Exception as e:
                print(f"Error during poll: {e}")

            time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
