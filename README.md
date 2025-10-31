# Share Tracker

A simple stock portfolio tracking application for Australian equities.

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

The database file is located at: `ShareTracker-Web/sharetracker/apps/db.sqlite3`

## Project Structure

- **Main web app**: `ShareTracker-Web/sharetracker/run.py`
- **Application code**: `ShareTracker-Web/sharetracker/apps/` (routes, models, templates)
- **Background tools**: `ShareTracker-Tools/main.py` (price importer script)

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

