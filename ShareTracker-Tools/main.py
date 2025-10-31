# Sample code for testing the yfinance package
# https://github.com/ranaroussi/yfinance
# https://aroussi.com/post/python-yahoo-finance
# https://towardsdatascience.com/the-easiest-way-to-pull-stock-data-into-your-python-program-yfinance-82c304ae35dc

import yfinance as yf
import sqlite3
from sqlite3 import Error
import time
from datetime import datetime
import math
import db
import sys
from sendemail import send_email

# CONSTANTS
sleep_delay = 0.0  # 2.0 wait between queries to prevent rate limiting


# Daily - function to import stock prices for only those stocks that are currently in use by portfolios
# Import closing price to STOCK table
# TODO: Import open, high, low, close, volume to HISTORY table
def daily_price_import_for_portfolio_stocks_only():
    print("Daily Price Import for Portfolio Stocks ...")
    conn = db.create_connection(db.database)
    stock_codes = db.get_stock_codes_in_use(conn)

    # Make a string from the list of tuples, with each element separated by a space, and appending .AX to each code
    stock_tickers = " ".join("%s.AX" % tup for tup in stock_codes)

    stock_tickers += " ^AORD ^AXJO"  # add indexes
    stock_codes.append(("^AORD", ""))  # add index to list
    stock_codes.append(("^AXJO", ""))  # add index to list

    print(stock_tickers)

    # DEBUGGING ONLY - only download a small subset of data ...
    # stock_tickers = "^AORD ANZ.AX AWC.AX BTI.AX OZLKCD.AX"
    # stock_codes = [("^AORD",""),("ANZ",""),("AWC",""),("BTI",""),("OZLKCD","")]

    data = yf.download(tickers=stock_tickers,
        period="1d",
        interval="1d",
        group_by='ticker',
        auto_adjust=True,
        prepost=True,
        threads=True,
        proxy=None
    )
    # print(data)

    # Imports prices to STOCK table
    # TODO: import prices to HISTORY table
    num_imports = 0
    email_body = [""]
    for stock in stock_codes:
        short_code = stock[0]
        if short_code.startswith("^"):  # support index like ^AORD
            code = short_code
        else:
            code = short_code + ".AX"

        if code in data:  # check that key exists
            close = data[code]['Close'][0]
            print(f"{code} closing price: {close:.3f}")
            email_body.append(f"{code} closing price: {close:.3f}")

            if not math.isnan(close):
                cur = conn.cursor()
                cur.execute("UPDATE stock SET last = ? WHERE code = ?", (f'{close:.3f}', short_code))
                num_imports += 1
    print(f"{num_imports} prices imported.")
    email_body.append(f"{num_imports} prices imported.")
    # for row in data:
    #     print (row)
    conn.commit()
    conn.close()

    email_body = "\n".join(email_body)  # join email_body list into a string with line breaks
    send_email("peter@huntit.com.au", "ShareTracker Daily Price Import for Portfolio Stocks", email_body)


# Daily - download open, high, low, close, volume for all stocks
# Import closing price to STOCK table
# Import open, high, low, close, volume to HISTORY table
def daily_price_import():
    print("Daily Price Import ...")
    conn = db.create_connection(db.database)
    stock_codes = db.get_all_stock_codes(conn)

    # Make a string from the list of tuples, with each element separated by a space, and appending .AX to each code
    stock_tickers = " ".join("%s.AX" % tup for tup in stock_codes)
    print(stock_tickers)

    # DEBUGGING ONLY - only download a small subset of data ...
    # stock_tickers = "^AORD ANZ.AX AWC.AX BTI.AX OZLKCD.AX"
    # stock_codes = [("^AORD",""),("ANZ",""),("AWC",""),("BTI",""),("OZLKCD","")]

    data = yf.download(tickers=stock_tickers,
        period="1d",
        interval="1d",
        group_by='ticker',
        auto_adjust=True,
        prepost=True,
        threads=True,
        proxy=None
    )
    # print(data)

    # Imports prices to STOCK table
    # TODO: import prices to HISTORY table
    num_imports = 0
    for stock in stock_codes:
        short_code = stock[0]
        if short_code.startswith("^"):  # support index like ^AORD
            code = short_code
        else:
            code = short_code + ".AX"

        if code in data: # check that key exists
            close = data[code]['Close'][0]
            print(f"{code} closing price: {close:.3f}")
            if not math.isnan(close):
                # update_query = f"UPDATE stock SET last = {close:.3f} WHERE code = '{short_code}'"
                # print(update_query)
                cur = conn.cursor()
                cur.execute("UPDATE stock SET last = ? WHERE code = ?", (f'{close:.3f}', short_code))
                # cur.execute(update_query)
                num_imports += 1
    print(f"{num_imports} prices imported.")

    conn.commit()
    conn.close()

# Monthly - download company info for all stocks in STOCK table
# Import shortName to STOCK table
# Import data to COMPANY_INFO table
def monthly_company_info_update():
    print("Monthly Company Info Update ...")
    conn = db.create_connection(db.database)
    stock_codes = db.get_all_stock_codes(conn)

    # Make a string from the list of tuples, with each element separated by a space, and appending .AX to each code
    stock_tickers = " ".join("%s.AX" % tup for tup in stock_codes)

    # DEBUGGING ONLY - only download a small subset of data ...
    # stock_codes = [("^AORD",""),("ANZ",""),("AWC",""),("BTI",""),("OZLKCD","")]
    # stock_tickers = "^AORD ANZ.AX AWC.AX BTI.AX OZLKCD.AX"
    # stock_codes = [("CBO",""),("CBR",""),("CBTC",""),("CCE","")]
    # stock_tickers = "CBO.AX CBR.AX CBTC.AX CCE.AX"

    print(stock_tickers)

    tickers = yf.Tickers(stock_tickers)  # returns a named tuple of Ticker objects

    num_updates = 0
    for stock in stock_codes:
        short_code = stock[0]
        if short_code.startswith("^"):  # support index like ^AORD
            code = short_code
        else:
            code = short_code + ".AX"

        if code in tickers.tickers:  # check that key exists
            info = tickers.tickers[code].info   # download company info
            print(info)
            # Update short_name in STOCK table
            if "shortName" in info:
                short_name = info["shortName"]
                print(short_name)
                # update_query = f"UPDATE stock SET short_name = '{short_name}' WHERE code = '{short_code}'"
                # print(update_query)
                cur = conn.cursor()
                # cur.execute(update_query)
                cur.execute("UPDATE stock SET short_name = ? WHERE code = ?", (short_name, short_code))
                conn.commit()
                num_updates += 1

            # Update company info in COMPANY_INFO table
            db.update_company_info(conn,short_code,info)

            time.sleep(sleep_delay)  # wait between queries to prevent rate limiting

    print(f"{num_updates} companies updated.")
    conn.commit()
    conn.close()

if __name__ == '__main__':

    print("Welcome to the yfinance share price importer")
    print("Database:",db.database)
    print("Current Time =", datetime.now().strftime("%H:%M:%S"))
    start_time = time.time()

    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))
    args = sys.argv[1:]
    print(args)

    # To schedule this script to run every day, use the following command:
    # https://betterprogramming.pub/https-medium-com-ratik96-scheduling-jobs-with-crontab-on-macos-add5a8b26c30
    # Terminal Command to do the daily import:
    # /Users/peter/Sync/Developer/2022\ ShareTracker/ShareTracker-Tools/venv/bin/python3 /Users/peter/Sync/Developer/2022\ ShareTracker/ShareTracker-Tools/main.py daily
    # crontab -e
    # 0 17 * * MON-FRI /Users/peter/Sync/Developer/2022\ ShareTracker/ShareTracker-Tools/venv/bin/python3 /Users/peter/Sync/Developer/2022\ ShareTracker/ShareTracker-Tools/main.py daily >/tmp/stdout.log 2>/tmp/stderr.log
    # crontab -l to list cron jobs
    # View /tmp/stdout.log and /tmp/stderr.log for output
    # On command line argument, run the daily import
    if args[0] == "daily":
      daily_price_import_for_portfolio_stocks_only()

    # Check that database tables exist, and create them if not
    db.check_tables()

    # daily_price_import()
    # monthly_company_info_update()

    print("Current Time =", datetime.now().strftime("%H:%M:%S"))
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print(f"Elapsed: {elapsed_time:.2f} minutes")



"""
    index = yf.Ticker("^AORD")
    index_info = index.info
    print(index_info)
    market_price = index_info['regularMarketPrice']
    print('AORD: ', market_price)


    company = yf.Ticker("ANZ.AX")
    # get stock info
    company_info = company.info
    print(company_info)

    market_price = company_info['regularMarketPrice']
    previous_close_price = company_info['regularMarketPreviousClose']
    print('ANZ market price ', market_price)
    print('ANZ previous close price ', previous_close_price)

    #
    # hist = company.history(period="1d")
    # # print(hist)
    # close = hist['Close']
    # print(f"ANZ closing price: {close}")

    dividends = company.dividends
    print(dividends)

    company3 = yf.Ticker("AWC.AX")
    # get stock info
    company_info3 = company3.info
    print(company_info3)

    market_price3 = company_info3['regularMarketPrice']
    previous_close_price3 = company_info3['regularMarketPreviousClose']
    print('AWC market price ', market_price3)
    print('AWC previous close price ', previous_close_price3)

    dividends3 = company3.dividends
    print(dividends3)


    company2 = yf.Ticker("BTI.AX")
    # get stock info
    company2_info = company2.info
    print(company2_info)

    dividends2 = company2.dividends
    print(dividends2)


    data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers="^AORD ANZ.AX AWC.AX BTI.AX",

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period="1d",

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval="1d",

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by='ticker',

        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust=True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost=True,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads=True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy=None
    )

    print(data)

    for field in data['AWC.AX']['Close']:
        print(field)
        # print(data['AWC.AX']['Close'])
    print(data['AWC.AX']['Close'][0])

    # print("ANZ - " + data['ANZ.AX']['Close'])
    # print(data['Close']['ANZ.AX'])
    # print(data['Close']['AWC.AX'])
    # print(data['Close']['BTI.AX'])
    # print(data['Close'])

    for field in data['ANZ.AX']:
        print(data['ANZ.AX'][field][0])

    # print(data['ANZ.AX']['Close']['Date'])

    awc_close = data['AWC.AX']['Close'][0]
    print(f"AWC closing price: {awc_close:.3f}")

"""