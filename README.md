
# CS2 Skin Price Tracker

A data pipeline and dashboard that tracks daily prices of AK-47 skins (Factory New) in Counter-Strike 2 and shows which skins have gained or lost the most value over a chosen period.

**Live dashboard:** [link, if you publish it]

![Dashboard screenshot](docs/dashboard.png)

## What it does

- Collects prices for all AK-47 | ... (Factory New) skins from the Skinport marketplace once a day
- Stores every snapshot in a SQLite database, building up price history over time
- Shows current prices, top winners and losers over a selectable period, and a price chart per skin in a Streamlit dashboard

## How it works

```
GitHub Actions (daily cron)
        |
        v
src/fetch_skinport.py  -->  data/prices.db (SQLite)  -->  src/dashboard.py (Streamlit)
```

1. A scheduled GitHub Actions workflow runs `fetch_skinport.py` every day
2. The script makes one request to Skinport's public API, filters the result and appends the rows to the database
3. The workflow commits the updated database back to the repository, so the history grows without manual work
4. The dashboard reads the database with pandas and calculates price changes

## Tech stack

Python, requests, SQLite, pandas, Streamlit, GitHub Actions

## Run it locally

```bash
git clone https://github.com/pisch77/cs-skin-tracker.git
cd cs-skin-tracker
python -m venv venv
venv\Scripts\activate        # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run src/dashboard.py
```

Run the dashboard from the project root so it finds `data/prices.db`.

## Design decisions and limitations

- **Why Skinport and not Steam:** I first built a collector for the Steam Community Market's `priceoverview` endpoint (`src/fetch_prices.py`, kept in the repo). Steam answered every request with HTTP 429 (rate limited), even a single request after several weeks, so I switched to Skinport, which has a public API without authentication and returns all items in one request.
- **Prices are listing prices, not sale prices.** The tracker shows the lowest current listing on Skinport, which is not necessarily what items actually sell for.
- **Thin markets are noisy.** Some skins have only one or two listings, so a single seller can move the "price" a lot. The dashboard has a minimum-listings filter for winners and losers to reduce this.
- **Not comparable with Steam.** Skinport and Steam prices differ, so numbers from the two should not be mixed.
- **Short history.** Winners and losers only become meaningful after a couple of weeks of data.

## Possible next steps

- Include other wear levels and weapon types
- Volatility measure in addition to percentage change
- Alerts for large price moves
- Test coverage for the price-change calculations