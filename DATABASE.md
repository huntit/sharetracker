# Database Design and Operations

This document explains the data model, where it is defined in code, and how to run the database in development and production for SQLite and MySQL/PostgreSQL, including migrations.

## Overview
- Default DB: `ShareTracker-Web/sharetracker/apps/db.sqlite3` (SQLite)
- ORM Models (Flask SQLAlchemy): `ShareTracker-Web/sharetracker/apps/authentication/models.py`
- Raw SQLite DDL (tools): `ShareTracker-Tools/db.py` (creates additional tables used by the importer)
- App configuration and DB URIs: `ShareTracker-Web/sharetracker/apps/config.py`

## Logical Schema

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

## Table Details
- Users: id (PK), username (unique), email (unique), password (binary)
- Portfolio: id (PK), user_id (FK Users.id), name, notes
- Portfolio_Stock: id (PK), portfolio_id (FK Portfolio.id), stock_code (FK Stock.code), units, notes
- Stock: code (PK varchar(6)), short_name (varchar), last (decimal 10,3)
- Company_Info (tools): stock_code (PK/FK), date (datetime), long_name, industry, sector, long_business_summary, logo_url
- History (tools): id (PK autoinc), stock_code (FK), date, open, high, low, close, volume

## Where the Schema Is Defined in Code
- ORM models (web app): `ShareTracker-Web/sharetracker/apps/authentication/models.py`
  - Defines `Users`, `Portfolio`, `Portfolio_Stock`, `Stock` in SQLAlchemy
  - Pre-populates `Stock` after-create from `apps/static/ASXEQUITIESMetastock.txt`
- Tools DDL (SQLite only): `ShareTracker-Tools/db.py`
  - `check_tables()` creates tables if missing: `Stock`, `Company_Info`, `History`, `Portfolio`, `Portfolio_Stock`
  - `update_company_info()` upserts `Company_Info`
- Configuration (URIs): `ShareTracker-Web/sharetracker/apps/config.py`
  - Debug uses SQLite file; Production builds URI from env vars (`DB_ENGINE`, `DB_USERNAME`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`)

Note: `Company_Info` and `History` are not SQLAlchemy models in the web app; they are created/managed by the tools script. To manage them via migrations, add ORM models for them in the Flask app.

## SQLite (Development)
1) Create venv and install deps
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r "ShareTracker-Web/sharetracker/requirements.txt"
```
2) Environment
```bash
# ShareTracker-Web/sharetracker/.env
DEBUG=True
```
3) Initialize DB (tables via Alembic migrations)
```bash
cd ShareTracker-Web/sharetracker
export FLASK_APP=run.py
flask db init        # once
flask db migrate -m "init schema"
flask db upgrade
```

## MySQL (Production alternative)
1) Configure env (ProductionConfig)
```bash
# ShareTracker-Web/sharetracker/.env
DEBUG=False
DB_ENGINE=mysql
DB_USERNAME=<user>
DB_PASS=<password>
DB_HOST=<host>
DB_PORT=3306
DB_NAME=<database>
```
2) Install driver and deps
```bash
pip install -r ShareTracker-Web/sharetracker/requirements-mysql.txt
# If needed based on platform
pip install mysqlclient  # or PyMySQL
```
3) Apply migrations
```bash
cd ShareTracker-Web/sharetracker
export FLASK_APP=run.py
flask db upgrade
```

## PostgreSQL (Production alternative)
1) Configure env
```bash
# ShareTracker-Web/sharetracker/.env
DEBUG=False
DB_ENGINE=postgresql
DB_USERNAME=<user>
DB_PASS=<password>
DB_HOST=<host>
DB_PORT=5432
DB_NAME=<database>
```
2) Install deps and migrate
```bash
pip install -r ShareTracker-Web/sharetracker/requirements-pgsql.txt
cd ShareTracker-Web/sharetracker
export FLASK_APP=run.py
flask db upgrade
```

## Database Migrations (Flask-Migrate/Alembic)
```bash
cd ShareTracker-Web/sharetracker
export FLASK_APP=run.py

# First time only
flask db init

# When models change
flask db migrate -m "describe change"
flask db upgrade

# Optional: downgrade one revision
# flask db downgrade -1
```
Tips:
- Ensure models are imported by the app factory before running `migrate` so autogenerate sees them
- Tables created only in `ShareTracker-Tools/db.py` won’t be included unless modeled in SQLAlchemy

## Production Notes
- For Apache + mod_wsgi deployment (Virtualmin), follow `DEPLOYMENT.md`
- Set `DEBUG=False` and a strong `SECRET_KEY` in `.env`
- Prefer MySQL/PostgreSQL for multi-user or higher write concurrency
- Backups: SQLite (copy file), MySQL/PostgreSQL (use native dump tools)
