# Deployment Guide

This guide covers how to run Share Tracker locally on macOS and deploy it to production on an Ubuntu server with Virtualmin.

## Running Locally on macOS

### Prerequisites
- Python 3.10 or higher
- Git (optional)

### Steps

1. **Navigate to the project directory:**
   ```bash
   cd "/Users/peter/Sync/Developer/2022 ShareTracker"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r "ShareTracker-Web/sharetracker/requirements.txt"
   ```

4. **Set up environment variables (optional):**
   Create `ShareTracker-Web/sharetracker/.env` with:
   ```
   DEBUG=True
   ```

5. **Initialize the database:**
   ```bash
   cd ShareTracker-Web/sharetracker
   export FLASK_APP=run.py
   flask db upgrade
   ```
   (The database file will be created automatically on first run if using SQLite)

6. **Run the application:**
   ```bash
   flask run --host=127.0.0.1 --port=5000
   ```

7. **Access the application:**
   Open your browser to `http://127.0.0.1:5000`

### Optional: Running the Price Updater Tool

In a separate terminal window:

```bash
cd ShareTracker-Tools
python3 -m venv venv
source venv/bin/activate
pip install yfinance python-dotenv
python main.py daily
```

## Deploying to Production (Ubuntu with Virtualmin)

### Option A: Apache with mod_wsgi (Recommended for Virtualmin)

1. **Install system packages:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip libapache2-mod-wsgi-py3
   ```

2. **Copy project to server:**
   Upload the project files to your Virtualmin-managed domain directory (e.g., `/home/username/domains/yourdomain.com/public_html/sharetracker`)

3. **Set up Python virtual environment:**
   ```bash
   cd /path/to/sharetracker/ShareTracker-Web/sharetracker
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Create WSGI entry point:**
   Create a `wsgi.py` file in `ShareTracker-Web/sharetracker/`:
   ```python
   from run import app as application
   ```

5. **Configure Apache via Virtualmin:**
   - Navigate to Virtualmin > Server Configuration > Website Options
   - Enable "Python website" (mod_wsgi)
   - Set WSGI script path to: `/path/to/sharetracker/ShareTracker-Web/sharetracker/wsgi.py`
   - Set Python virtualenv path to: `/path/to/sharetracker/ShareTracker-Web/sharetracker/venv`

6. **Configure environment:**
   - Create `.env` file in `ShareTracker-Web/sharetracker/` with:
     ```
     DEBUG=False
     ```

7. **Set permissions:**
   Ensure Apache user has read/write access to the database:
   ```bash
   chmod 664 ShareTracker-Web/sharetracker/apps/db.sqlite3
   chmod 775 ShareTracker-Web/sharetracker/apps/
   ```

8. **Restart Apache:**
   ```bash
   sudo systemctl reload apache2
   ```

### Option B: Apache Reverse Proxy to Gunicorn

1. **Install packages:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip
   ```

2. **Set up virtual environment and install dependencies** (same as Option A, step 3)

3. **Run Gunicorn:**
   ```bash
   cd ShareTracker-Web/sharetracker
   source venv/bin/activate
   gunicorn --workers 3 --bind 127.0.0.1:8000 run:app
   ```

4. **Configure Apache reverse proxy in Virtualmin:**
   - Enable proxy modules in Apache
   - Configure VirtualHost to proxy requests to `http://127.0.0.1:8000`

5. **Set up systemd service (recommended):**
   Create `/etc/systemd/system/sharetracker.service`:
   ```ini
   [Unit]
   Description=ShareTracker Gunicorn service
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/sharetracker/ShareTracker-Web/sharetracker
   Environment="PATH=/path/to/sharetracker/ShareTracker-Web/sharetracker/venv/bin"
   ExecStart=/path/to/sharetracker/ShareTracker-Web/sharetracker/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 run:app

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable sharetracker
   sudo systemctl start sharetracker
   ```

## Production Notes

- Set `DEBUG=False` in production
- Use strong SECRET_KEY in `.env` file
- Consider using PostgreSQL or MySQL (requirements files provided) for production with multiple users
- Set up proper firewall rules
- Configure SSL/TLS certificates via Virtualmin
- Regularly backup the database file

## Database Backup

For SQLite database:
```bash
cp ShareTracker-Web/sharetracker/apps/db.sqlite3 backup_$(date +%Y%m%d).sqlite3
```

