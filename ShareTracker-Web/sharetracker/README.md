## Share Tracker

A simple stock portfolio tracker for Australian equities.

### What it does
- Manage user accounts and portfolios via a Flask web app.
- Store stocks, portfolio holdings, and company info in SQLite.
- Optionally run a helper script that fetches daily prices from Yahoo Finance (`yfinance`) and emails a brief summary.

### Components
- `ShareTracker-Web/` – Flask web application (Argon Dashboard UI).
- `ShareTracker-Tools/` – Utilities that update prices and company info into the same SQLite DB.

### Tech & Docs
- Flask (framework): https://flask.palletsprojects.com/
- Argon Dashboard (UI template): https://www.creative-tim.com/product/argon-dashboard-flask

### Database (SQLite) schema
- `Users` (id, username, email, password)
- `Portfolio` (id, user_id, name, notes)
- `Portfolio_Stock` (id, portfolio_id, stock_code, units, notes)
- `Stock` (code, short_name, last)
- `Company_Info` (stock_code, date, long_name, industry, sector, long_business_summary, logo_url)
- `History` (id, stock_code, date, open, high, low, close, volume)

Notes:
- The web app uses SQLAlchemy models under `sharetracker/apps/authentication/models.py`.
- The tools write directly to the same SQLite file at `sharetracker/apps/db.sqlite3`.

### Where to look
- App entry: `ShareTracker-Web/sharetracker/run.py`
- Blueprints & routes: `ShareTracker-Web/sharetracker/apps/`
- Tools entry: `ShareTracker-Tools/main.py`

See `DEPLOYMENT.md` for local run instructions and production deployment notes.
