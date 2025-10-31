## Deployment Guide

This guide shows how to run Share Tracker locally on macOS and how to deploy to an Ubuntu server managed by Virtualmin.

### 1) Run locally on macOS

Prereqs:
- Python 3.10+
- Git (optional)

Steps:
1. Open Terminal in the project root: `.../2022 ShareTracker/`
2. Create and activate a virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
3. Install dependencies for the web app:
   - `pip install -r "ShareTracker-Web/sharetracker/requirements.txt"`
4. Configure environment (optional but recommended):
   - Create `ShareTracker-Web/sharetracker/.env` and set for development:
     - `DEBUG=True`
5. Initialize the database:
   - From `ShareTracker-Web/sharetracker/` directory, run:
     - `export FLASK_APP=run.py` (macOS)
     - `flask db upgrade` (creates tables if using migrations; first run may just create the SQLite file on access)
6. Run the app:
   - From `ShareTracker-Web/sharetracker/`: `flask run --host=127.0.0.1 --port=5000`
   - Visit http://127.0.0.1:5000

Optional: price updater
- In a separate terminal (and venv if you want isolation), you can run daily updates:
  - `cd ShareTracker-Tools`
  - `python3 -m venv venv && source venv/bin/activate`
  - `pip install -r ../ShareTracker-Web/sharetracker/requirements.txt && pip install yfinance python-dotenv`
  - `python main.py daily`

### 2) Deploy to Ubuntu with Virtualmin (Apache)

Goal: run the Flask app via `mod_wsgi` under Apache (Virtualmin-managed).

Prereqs:
- Ubuntu 20.04+ with Virtualmin
- A domain/subdomain configured in Virtualmin

Option A – Apache mod_wsgi (simplest under Virtualmin)
1. Install system packages:
   - `sudo apt update && sudo apt install python3 python3-venv python3-pip libapache2-mod-wsgi-py3`
2. Copy project to server (e.g., `/home/youruser/domains/yourdomain/public_html/sharetracker` or another directory owned by the Virtualmin user).
3. Create a virtualenv and install deps:
   - `cd /path/to/sharetracker/ShareTracker-Web/sharetracker`
   - `python3 -m venv venv && source venv/bin/activate`
   - `pip install -r requirements.txt`
4. Create a `wsgi.py` entry point (if not present) that exposes `application`:
   ```python
   from run import app as application
   ```
5. Configure Apache (Virtualmin > Server Configuration > Website Options):
   - Enable Python website (mod_wsgi).
   - Point WSGI script to your `wsgi.py` path.
   - Set Python virtualenv path to your `venv`.
6. Environment:
   - Place `.env` next to `run.py` (same directory) and set `DEBUG=False` in production.
7. Database:
   - SQLite file lives at `ShareTracker-Web/sharetracker/apps/db.sqlite3` (ensure the Apache user has read/write permissions to this file and directory).
8. Reload Apache in Virtualmin (or `sudo systemctl reload apache2`).

Notes
- For production, consider PostgreSQL/MySQL (requirements files provided) if you expect multiple users and heavier load.
- Keep `DEBUG=False` in production. Use strong secrets and firewall the server.




