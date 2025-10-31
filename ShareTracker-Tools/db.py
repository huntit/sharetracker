# Sqlite database functions
import sqlite3
from sqlite3 import Error
from datetime import datetime


# CONSTANTS
database = r"/Users/peter/Sync/Developer/2022 ShareTracker/ShareTracker-Web/sharetracker/apps/db.sqlite3"


def create_connection(db_file):
    """ create a database connection to the SQLite database specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def get_all_stock_codes(conn):
    """
    Query all rows in the stock table
    :param conn: the Connection object
    :return: all stock codes in tuple (code, blank)
    """
    cur = conn.cursor()
    # cur.execute("SELECT stock.code FROM stock;")
    # only select stocks without a name and are 3 letters
    # cur.execute("SELECT stock.code FROM stock WHERE stock.short_name = '' AND length(stock.code) = 3 LIMIT 500;")
    # cur.execute("SELECT stock.code FROM stock WHERE length(stock.code) = 4 LIMIT 500;")
    cur.execute("SELECT stock.code FROM stock;")
    rows = cur.fetchall()  # tuple of (code, <blank>)
    # for row in rows:
    #     print(row[0])
    return rows


def get_stock_codes_in_use(conn):
    """
    Query stock codes that are currently in use in portfolios
    :param conn: the Connection object
    :return: all stock codes in tuple (code, blank)
    """
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT stock_code FROM Portfolio_Stock;")
    rows = cur.fetchall()  # tuple of (code, <blank>)
    return rows


# Check if SQLite database tables exist and create them if not
def check_tables():
    print("Checking Tables ...")
    conn = create_connection(database)
    cur = conn.cursor()

    # MARK: STOCK
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Stock';")
    rows = cur.fetchall()
    if len(rows) == 0:
        print("Creating Stock table ...")
        # code = db.Column(db.String(6), primary_key=True)
        # short_name = db.Column(db.String(256), unique=False)
        # last = db.Column(db.Numeric(10, 3))
        create_table_sql = """CREATE TABLE Stock (
                                        code VARCHAR(6) NOT NULL PRIMARY KEY,
                                        short_name VARCHAR(256) ,
                                        last DECIMAL(10, 3)
                                    );"""
        cur.execute(create_table_sql)
        conn.commit()
        print("Stock table created successfully")

    # MARK: COMPANY_INFO
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Company_Info';")
    rows = cur.fetchall()
    if len(rows) == 0:
        print("Creating Company_Info table ...")
        create_table_sql = """CREATE TABLE Company_Info (
                                        stock_code VARCHAR(6) NOT NULL PRIMARY KEY,
                                        date DATE NOT NULL,
                                        long_name VARCHAR(1024),
                                        industry VARCHAR(256),
                                        sector VARCHAR(256),
                                        long_business_summary VARCHAR(4096),
                                        logo_url VARCHAR(256)
                                    );"""
        cur.execute(create_table_sql)
        conn.commit()
        print("Company_Info table created successfully")

    # MARK: HISTORY
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='History';")
    rows = cur.fetchall()
    if len(rows) == 0:
        print("Creating History table ...")
        create_table_sql = """CREATE TABLE History (
                                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                        stock_code VARCHAR(6) NOT NULL,
                                        date DATE NOT NULL,
                                        open DECIMAL(10, 3),
                                        high DECIMAL(10, 3),
                                        low DECIMAL(10, 3),
                                        close DECIMAL(10, 3),
                                        volume INTEGER
                                    );"""
        cur.execute(create_table_sql)
        conn.commit()
        print("History table created successfully")

    # MARK: PORTFOLIO
    table_name = "Portfolio"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    rows = cur.fetchall()
    if len(rows) == 0:
        print(f"Creating {table_name} table ...")
        create_table_sql = f"""CREATE TABLE {table_name} (
                                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                        user_id INTEGER NOT NULL,
                                        name VARCHAR(256),
                                        notes TEXT
                                    );"""
        cur.execute(create_table_sql)
        conn.commit()
        print(f"{table_name} table created successfully")

    # MARK: PORTFOLIO_STOCK
    table_name = "Portfolio_Stock"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    rows = cur.fetchall()
    if len(rows) == 0:
        print(f"Creating {table_name} table ...")
        create_table_sql = f"""CREATE TABLE {table_name} (
                                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                        portfolio_id INTEGER NOT NULL,
                                        stock_code VARCHAR(6) NOT NULL,
                                        units INTEGER NOT NULL,
                                        notes TEXT
                                    );"""
        cur.execute(create_table_sql)
        conn.commit()
        print(f"{table_name} table created successfully")


# Update company info table with latest data (insert if it doesn't exist)
def update_company_info(conn, stock_code, info):
    """
    Insert or Update company info table with latest data
    :param conn: the Connection object
    :param stock_code: stock code
    :param info: dictionary of company info
    :return:
    """
    # check that keys exist in dictionary first
    # if {"long_name", "industry", "sector", "long_business_summary", "logo_url"} <= info.keys():

    cur = conn.cursor()
    print(f"Updating {stock_code} into Company_Info table ...")
    cur.execute("INSERT OR REPLACE INTO Company_Info(stock_code, date) VALUES(?, ?)", (stock_code, str(datetime.now())))

    # datetime('now', 'localtime')
    if "longName" in info.keys():
        cur.execute("UPDATE Company_Info SET long_name = ? WHERE stock_code = ?", (info["longName"], stock_code))
    if "industry" in info.keys():
        cur.execute("UPDATE Company_Info SET industry = ? WHERE stock_code = ?", (info["industry"], stock_code))
    if "sector" in info.keys():
        cur.execute("UPDATE Company_Info SET sector = ? WHERE stock_code = ?", (info["sector"], stock_code))
    if "longBusinessSummary" in info.keys():
        cur.execute("UPDATE Company_Info SET long_business_summary = ? WHERE stock_code = ?", (info["longBusinessSummary"], stock_code))
    if "logo_url" in info.keys():
        cur.execute("UPDATE Company_Info SET logo_url = ? WHERE stock_code = ?", (info["logo_url"], stock_code))

    conn.commit()

    print(f"{stock_code} updated in Company_Info table successfully")
