# Share Tracker

A simple stock portfolio tracking application for Australian equities.

## To run the app locally (development mode):

   - From `ShareTracker-Web/sharetracker/`: `flask run --host=127.0.0.1 --port=5000`
   - Visit http://127.0.0.1:5000
   - Login as Peter
  
## What it does

A stock portfolio tracking system that allows users to:
- Manage portfolios and track stock holdings through a web dashboard
- View portfolio values using real-time stock prices
- Optionally run automated daily price updates using a background tool

## Components

- **ShareTracker-Web/** – Flask web application with Argon Dashboard UI for managing portfolios
- **ShareTracker-Tools/** – Background utility scripts that fetch daily stock prices from Yahoo Finance and update the database

## Technology & Documentation

- **Flask** (Web Framework): https://flask.palletsprojects.com/
- **Argon Dashboard** (UI Template): https://www.creative-tim.com/product/argon-dashboard-flask

## Database Structure

The application uses SQLite with the following tables:

- `Users` - User accounts (id, username, email, password)
- `Portfolio` - User portfolios (id, user_id, name, notes)
- `Portfolio_Stock` - Stock holdings in portfolios (id, portfolio_id, stock_code, units, notes)
- `Stock` - Stock information (code, short_name, last price)
- `Company_Info` - Company details (stock_code, date, long_name, industry, sector, long_business_summary, logo_url)
- `History` - Historical price data (id, stock_code, date, open, high, low, close, volume)

### ASCII ER Diagram

```text
 Users (id PK)
   └─< Portfolio (id PK, user_id FK → Users.id)
          └─< Portfolio_Stock (id PK, portfolio_id FK → Portfolio.id,
                               stock_code FK → Stock.code)

 Stock (code PK)
   ├─ Company_Info (stock_code PK/FK → Stock.code)
   └─< History (id PK, stock_code FK → Stock.code)

Legend:
- PK: Primary Key
- FK: Foreign Key
- └─< one-to-many relationship (parent ─ child)
```

The database file is located at: `ShareTracker-Web/sharetracker/apps/db.sqlite3`

## Project Structure

- **Main web app**: `ShareTracker-Web/sharetracker/run.py`
- **Application code**: `ShareTracker-Web/sharetracker/apps/` (routes, models, templates)
- **Background tools**: `ShareTracker-Tools/main.py` (price importer script)

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

